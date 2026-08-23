from flask import jsonify, request
from flask_login import login_required, current_user
from ..models import SpaceReport, Space, Reservation, db
from . import api_v2_bp
from datetime import datetime, timedelta

# API: 获取热力图数据
@api_v2_bp.route('/heatmap')
@login_required
def get_heatmap_data():
    """获取校园热力图数据"""
    try:
        # 获取最近24小时的上报数据
        yesterday = datetime.utcnow() - timedelta(days=1)

        reports = SpaceReport.query.filter(SpaceReport.created_at >= yesterday).all()

        # 按空间聚合数据
        heatmap_data = {}
        for report in reports:
            space_id = report.space_id
            if space_id not in heatmap_data:
                space = Space.query.get(space_id)
                heatmap_data[space_id] = {
                    'space_id': space_id,
                    'name': space.name,
                    'location': space.location,
                    'coordinates': [123.4644 + (space_id * 0.001), 41.6698 + (space_id * 0.001)],  # 模拟坐标
                    'count': 0,
                    'avg_crowding': 0
                }

            heatmap_data[space_id]['count'] += 1
            heatmap_data[space_id]['avg_crowding'] += report.crowding_level

        # 计算平均值
        for space_id in heatmap_data:
            if heatmap_data[space_id]['count'] > 0:
                heatmap_data[space_id]['avg_crowding'] /= heatmap_data[space_id]['count']

        return jsonify(list(heatmap_data.values()))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 获取实时通知
@api_v2_bp.route('/notifications')
@login_required
def get_notifications():
    """获取用户通知"""
    try:
        # 这里可以添加通知逻辑
        # 暂时返回示例数据
        notifications = [
            {
                'id': 1,
                'type': 'achievement',
                'title': '成就解锁',
                'message': '恭喜你解锁了"初出茅庐"成就！',
                'time': '5分钟前',
                'read': False
            },
            {
                'id': 2,
                'type': 'report',
                'title': '上报成功',
                'message': '你的上报已被采纳，获得10积分',
                'time': '1小时前',
                'read': True
            }
        ]

        return jsonify(notifications)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
