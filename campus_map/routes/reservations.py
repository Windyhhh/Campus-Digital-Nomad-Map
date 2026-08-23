from flask import jsonify, request
from flask_login import login_required, current_user
from ..models import Reservation, Space, db
from . import api_bp
from datetime import datetime

# API: 空间预约
@api_bp.route('/v2/reserve', methods=['POST'])
@login_required
def reserve_space():
    """预约空间"""
    try:
        data = request.get_json()
        space_id = data.get('space_id')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        purpose = data.get('purpose', '')
        num_people = data.get('num_people', 1)
        notes = data.get('notes', '')

        # 验证必填字段
        if not all([space_id, start_time_str, end_time_str]):
            return jsonify({'error': '缺少必填字段'}), 400

        # 解析时间
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except:
            return jsonify({'error': '时间格式错误'}), 400

        # 验证时间逻辑
        if start_time >= end_time:
            return jsonify({'error': '结束时间必须晚于开始时间'}), 400

        if start_time < datetime.utcnow():
            return jsonify({'error': '不能预约过去的时间'}), 400

        # 检查空间是否存在
        space = Space.query.get(space_id)
        if not space:
            return jsonify({'error': '空间不存在'}), 404

        # 检查时间冲突
        conflicting = Reservation.query.filter(
            Reservation.space_id == space_id,
            Reservation.status.in_(['pending', 'approved']),
            db.or_(
                db.and_(Reservation.start_time <= start_time, Reservation.end_time > start_time),
                db.and_(Reservation.start_time < end_time, Reservation.end_time >= end_time),
                db.and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time)
            )
        ).first()

        if conflicting:
            return jsonify({'error': '该时间段已被预约'}), 409

        # 创建预约
        reservation = Reservation(
            user_id=current_user.id,
            space_id=space_id,
            start_time=start_time,
            end_time=end_time,
            purpose=purpose,
            num_people=num_people,
            notes=notes,
            status='approved' if current_user.role in ['admin', 'teacher'] else 'pending'
        )

        db.session.add(reservation)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '预约成功！' if reservation.status == 'approved' else '预约已提交，等待审核',
            'reservation': {
                'id': reservation.id,
                'space_name': space.name,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'status': reservation.status,
                'status_display': reservation.get_status_display()
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'预约失败：{str(e)}'
        }), 500

# API: 审核预约（管理员/教师）
@api_bp.route('/reservations/<int:reservation_id>/approve', methods=['POST'])
@login_required
def approve_reservation(reservation_id):
    """审核预约"""
    try:
        if current_user.role not in ['admin', 'teacher']:
            return jsonify({'error': '无权限'}), 403

        reservation = Reservation.query.get_or_404(reservation_id)
        data = request.get_json()
        action = data.get('action')  # approve or reject

        if action == 'approve':
            reservation.status = 'approved'
            message = '预约已批准'
        elif action == 'reject':
            reservation.status = 'rejected'
            message = '预约已拒绝'
        else:
            return jsonify({'error': '无效的操作'}), 400

        db.session.commit()

        return jsonify({
            'success': True,
            'message': message
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
