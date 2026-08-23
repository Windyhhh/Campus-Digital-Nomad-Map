from flask import jsonify, request
from flask_login import login_required, current_user
from ..models import Space, SpaceReport
from . import api_bp

# API: 训练预测模型
@api_bp.route('/ml/train', methods=['POST'])
@login_required
def train_prediction_model():
    """训练机器学习预测模型（仅管理员）"""
    try:
        if current_user.role != 'admin':
            return jsonify({'error': '无权限'}), 403

        # 获取所有历史上报数据
        reports = SpaceReport.query.all()

        if len(reports) < 20:
            return jsonify({'error': '数据不足，至少需要20条上报记录'}), 400

        # 准备训练数据
        reports_data = []
        for report in reports:
            reports_data.append({
                'created_at': report.created_at,
                'space_id': report.space_id,
                'space': {
                    'type': report.space.type,
                    'capacity': report.space.capacity
                },
                'crowding_level': report.crowding_level
            })

        # 训练模型
        from ..ml.predictor import predictor
        model_type = request.get_json().get('model_type', 'random_forest')
        predictor.train(reports_data, model_type=model_type)

        return jsonify({
            'success': True,
            'message': f'模型训练成功！使用了 {len(reports)} 条数据',
            'data_count': len(reports)
        })

    except Exception as e:
        return jsonify({'error': f'训练失败: {str(e)}'}), 500

# API: 预测空间拥挤度
@api_bp.route('/ml/predict/<int:space_id>')
@login_required
def predict_space_crowding(space_id):
    """预测指定空间未来几小时的拥挤度"""
    try:
        space = Space.query.get_or_404(space_id)

        # 获取历史数据
        historical_reports = SpaceReport.query.filter_by(space_id=space_id).order_by(SpaceReport.created_at.desc()).limit(100).all()

        historical_data = []
        for report in historical_reports:
            historical_data.append({
                'created_at': report.created_at,
                'hour': report.created_at.hour,
                'day_of_week': report.created_at.weekday(),
                'crowding_level': report.crowding_level
            })

        # 尝试加载已训练的模型
        from ..ml.predictor import predictor
        predictor.load_model()

        # 预测未来6小时
        hours = request.args.get('hours', 6, type=int)
        predictions = predictor.predict_next_hours(
            space={
                'type': space.type,
                'capacity': space.capacity
            },
            historical_data=historical_data,
            hours=hours
        )

        return jsonify({
            'space_id': space_id,
            'space_name': space.name,
            'predictions': predictions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 批量预测所有空间
@api_bp.route('/ml/predict-all')
@login_required
def predict_all_spaces():
    """预测所有空间的拥挤度"""
    try:
        spaces = Space.query.all()

        # 尝试加载模型
        from ..ml.predictor import predictor
        predictor.load_model()

        results = []
        for space in spaces:
            # 获取历史数据
            historical_reports = SpaceReport.query.filter_by(space_id=space.id).order_by(SpaceReport.created_at.desc()).limit(50).all()

            historical_data = []
            for report in historical_reports:
                historical_data.append({
                    'created_at': report.created_at,
                    'hour': report.created_at.hour,
                    'day_of_week': report.created_at.weekday(),
                    'crowding_level': report.crowding_level
                })

            # 预测下一个小时
            next_hour_prediction = predictor.predict_next_hours(
                space={
                    'type': space.type,
                    'capacity': space.capacity
                },
                historical_data=historical_data,
                hours=1
            )

            if next_hour_prediction:
                results.append({
                    'space_id': space.id,
                    'space_name': space.name,
                    'space_type': space.type,
                    'location': space.location,
                    'next_hour': next_hour_prediction[0]
                })

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
