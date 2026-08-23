from ..models import Achievement, SpaceReport
from flask_login import current_user

def check_and_award_achievements(user):
    """检查用户是否达成新成就并授予"""
    achievements = Achievement.query.all()
    user_report_count = SpaceReport.query.filter_by(user_id=user.id).count()

    for achievement in achievements:
        # 检查用户是否已经获得此成就
        if achievement in user.achievements:
            continue

        # 检查是否满足成就条件
        earned = False
        if achievement.points_required > 0 and user.points >= achievement.points_required:
            earned = True
        elif achievement.reports_required > 0 and user_report_count >= achievement.reports_required:
            earned = True

        if earned:
            # 授予成就
            user.achievements.append(achievement)
