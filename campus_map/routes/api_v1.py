from flask import jsonify, request
from flask_login import login_required, current_user
from ..models import Space, SpaceReport, User, db, Reservation
from . import api_bp
from ..utils.achievements import check_and_award_achievements

@api_bp.route('/spaces')
@login_required
def get_spaces():
    spaces = Space.query.all()
    spaces_data = []

    for space in spaces:
        # 获取最新的上报数据
        latest_report = SpaceReport.query.filter_by(space_id=space.id).order_by(SpaceReport.created_at.desc()).first()

        space_data = {
            'id': space.id,
            'name': space.name,
            'building': space.building,
            'floor': space.floor,
            'capacity': space.capacity,
            'type': space.space_type,
            'x': space.x_coordinate,
            'y': space.y_coordinate,
            'crowding': latest_report.crowding_level if latest_report else 1,
            'noise': latest_report.noise_level if latest_report else 1,
            'wifi': latest_report.wifi_quality if latest_report else 3,
            'power': latest_report.power_available if latest_report else True,
            'lastUpdate': latest_report.created_at.isoformat() if latest_report else None,
            'comment': latest_report.comment if latest_report else None
        }
        spaces_data.append(space_data)

    return jsonify(spaces_data)

@api_bp.route('/report', methods=['POST'])
@login_required
def submit_report():
    try:
        data = request.get_json()

        # 创建新的上报记录
        report = SpaceReport(
            space_id=data['space_id'],
            user_id=current_user.id,
            crowding_level=data['crowding_level'],
            noise_level=data['noise_level'],
            wifi_quality=data['wifi_quality'],
            power_available=data.get('power_available', False),
            comment=data.get('comment', '')
        )

        db.session.add(report)

        # 给用户增加积分
        current_user.points += 10

        # 检查并授予成就
        check_and_award_achievements(current_user)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '上报成功！您获得了10积分！',
            'points': current_user.points
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '上报失败，请重试'
        }), 500

@api_bp.route('/spaces/<int:space_id>/reports')
@login_required
def get_space_reports(space_id):
    reports = SpaceReport.query.filter_by(space_id=space_id).order_by(SpaceReport.created_at.desc()).limit(10).all()

    reports_data = []
    for report in reports:
        reports_data.append({
            'id': report.id,
            'user': report.user.username,
            'crowding_level': report.crowding_level,
            'noise_level': report.noise_level,
            'wifi_quality': report.wifi_quality,
            'power_available': report.power_available,
            'comment': report.comment,
            'created_at': report.created_at.isoformat()
        })

    return jsonify(reports_data)

@api_bp.route('/user/achievements')
@login_required
def get_user_achievements():
    """获取用户成就"""
    achievements_data = []
    for achievement in current_user.achievements:
        # 查找成就获得时间
        earned_at = None
        for assoc in achievement.users:  # 这里会得到关联对象
            if assoc.id == current_user.id:
                # 获取关联表中的earned_at字段
                from ..models import user_achievements
                result = db.session.query(user_achievements.c.earned_at).filter(
                    user_achievements.c.user_id == current_user.id,
                    user_achievements.c.achievement_id == achievement.id
                ).first()
                if result:
                    earned_at = result.earned_at.isoformat()
                break
        
        achievements_data.append({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'icon': achievement.icon,
            'earned_at': earned_at
        })

    return jsonify(achievements_data)

@api_bp.route('/user/stats')
@login_required
def get_user_stats():
    """获取用户统计信息"""
    report_count = SpaceReport.query.filter_by(user_id=current_user.id).count()
    unique_spaces = db.session.query(SpaceReport.space_id).filter_by(user_id=current_user.id).distinct().count()

    return jsonify({
        'points': current_user.points,
        'total_reports': report_count,
        'unique_spaces': unique_spaces,
        'achievements_count': len(current_user.achievements),
        'member_since': current_user.created_at.isoformat()
    })

@api_bp.route('/reservations')
@login_required
def get_reservations():
    """获取用户的预约列表"""
    try:
        # 管理员可以查看所有预约
        if current_user.role == 'admin':
            reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()
        else:
            reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.created_at.desc()).all()

        return jsonify([{
            'id': r.id,
            'space_id': r.space_id,
            'space_name': r.space.name,
            'space_location': r.space.location,
            'start_time': r.start_time.isoformat(),
            'end_time': r.end_time.isoformat(),
            'purpose': r.purpose,
            'num_people': r.num_people,
            'status': r.status,
            'status_display': r.get_status_display(),
            'status_color': r.get_status_color(),
            'is_active': r.is_active(),
            'can_cancel': r.can_cancel(current_user),
            'created_at': r.created_at.isoformat()
        } for r in reservations])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    """取消预约"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)

        if not reservation.can_cancel(current_user):
            return jsonify({'error': '无权取消此预约'}), 403

        reservation.status = 'cancelled'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '预约已取消'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
