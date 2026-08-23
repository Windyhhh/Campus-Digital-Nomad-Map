#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3.0 功能演示脚本
展示新增的多角色、预约、AI预测功能
"""

import os
import sys
from datetime import datetime, timedelta
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Space, SpaceReport, Reservation
from ml_predictor import predictor

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def demo_roles():
    """演示多角色系统"""
    print_header("1. 多角色用户系统演示")
    
    with app.app_context():
        users = User.query.all()
        
        print(f"\n共有 {len(users)} 个用户：\n")
        
        role_counts = {}
        for user in users:
            role = user.role
            role_counts[role] = role_counts.get(role, 0) + 1
            
            print(f"👤 {user.username:10s} | {user.get_role_display():6s} | {user.department:12s} | {user.student_id:10s} | 积分: {user.points}")
        
        print(f"\n角色统计：")
        for role, count in role_counts.items():
            role_map = {
                'admin': '管理员',
                'teacher': '教师',
                'student': '学生',
                'visitor': '访客'
            }
            print(f"  {role_map.get(role, role)}: {count}人")
        
        print("\n权限示例：")
        admin = User.query.filter_by(role='admin').first()
        teacher = User.query.filter_by(role='teacher').first()
        student = User.query.filter_by(role='student').first()
        
        if admin:
            print(f"  {admin.username}（管理员）可以管理用户: {admin.has_permission('manage_users')}")
        if teacher:
            print(f"  {teacher.username}（教师）可以优先预约: {teacher.has_permission('reserve_priority')}")
        if student:
            print(f"  {student.username}（学生）可以上报空间: {student.has_permission('report_space')}")

def demo_reservations():
    """演示预约系统"""
    print_header("2. 预约系统演示")
    
    with app.app_context():
        reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
        
        print(f"\n最近 {len(reservations)} 条预约记录：\n")
        
        for r in reservations:
            status_icon = {
                'pending': '⏳',
                'approved': '✅',
                'rejected': '❌',
                'cancelled': '🚫',
                'completed': '✔️'
            }.get(r.status, '❓')
            
            print(f"{status_icon} {r.user.username:10s} | {r.space.name:15s} | {r.get_status_display():6s} | {r.start_time.strftime('%m-%d %H:%M')} - {r.end_time.strftime('%H:%M')} | {r.purpose}")
        
        # 统计
        status_counts = {}
        for r in Reservation.query.all():
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
        
        print(f"\n预约状态统计：")
        for status, count in status_counts.items():
            status_map = {
                'pending': '待审核',
                'approved': '已批准',
                'rejected': '已拒绝',
                'cancelled': '已取消',
                'completed': '已完成'
            }
            print(f"  {status_map.get(status, status)}: {count}条")
        
        # 演示创建预约
        print(f"\n演示创建新预约：")
        user = User.query.filter_by(role='student').first()
        space = Space.query.first()
        
        if user and space:
            now = datetime.now()
            start_time = now + timedelta(days=1, hours=2)
            end_time = start_time + timedelta(hours=2)
            
            print(f"  用户: {user.username}")
            print(f"  空间: {space.name}")
            print(f"  时间: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
            print(f"  目的: 小组讨论")
            print(f"  状态: {'待审核' if user.role == 'student' else '已批准'}")

def demo_predictions():
    """演示AI预测功能"""
    print_header("3. AI智能预测演示")
    
    with app.app_context():
        # 获取历史数据
        reports = SpaceReport.query.all()
        print(f"\n历史上报数据: {len(reports)} 条")
        
        if len(reports) >= 20:
            print("✅ 数据充足，可以训练模型")
            
            # 准备训练数据
            print("\n准备训练数据...")
            reports_data = []
            for report in reports:
                reports_data.append({
                    'created_at': report.created_at,
                    'space_id': report.space_id,
                    'space': {
                        'type': report.space.space_type,
                        'capacity': report.space.capacity
                    },
                    'crowding_level': report.crowding_level,
                    'hour': report.created_at.hour,
                    'day_of_week': report.created_at.weekday()
                })
            
            # 训练模型
            print("开始训练模型（随机森林）...")
            predictor.train(reports_data, model_type='random_forest')
            print("✅ 模型训练完成！")
            
        else:
            print(f"⚠️ 数据不足（需要至少20条，当前{len(reports)}条）")
            print("使用默认预测规则...")
        
        # 尝试加载模型
        if predictor.load_model():
            print("\n✅ 已加载训练好的模型")
        else:
            print("\n⚠️ 未找到训练好的模型，使用默认规则")
        
        # 演示预测
        print("\n预测示例：")
        spaces = Space.query.limit(3).all()
        
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

            # 预测未来3小时
            predictions = predictor.predict_next_hours(
                space={
                    'type': space.space_type,
                    'capacity': space.capacity
                },
                historical_data=historical_data,
                hours=3
            )
            
            print(f"\n📍 {space.name} ({space.space_type})")
            for pred in predictions:
                color_icon = {
                    '#10B981': '🟢',
                    '#84CC16': '🟡',
                    '#F59E0B': '🟠',
                    '#EF4444': '🔴',
                    '#991B1B': '🟣'
                }.get(pred['color'], '⚪')
                
                print(f"  {pred['time']} {color_icon} {pred['crowding_text']:6s} (拥挤度: {pred['crowding_level']:.1f}/5.0)")

def demo_api_endpoints():
    """演示API端点"""
    print_header("4. API端点列表")
    
    print("\n预约相关API：")
    print("  GET  /api/reservations                    - 获取用户预约列表")
    print("  POST /api/v2/reserve                      - 创建新预约")
    print("  POST /api/reservations/<id>/cancel        - 取消预约")
    print("  POST /api/reservations/<id>/approve       - 审核预约")
    
    print("\n预测相关API：")
    print("  POST /api/ml/train                        - 训练预测模型（管理员）")
    print("  GET  /api/ml/predict/<space_id>           - 预测单个空间")
    print("  GET  /api/ml/predict-all                  - 预测所有空间")
    
    print("\n页面路由：")
    print("  /reservations                             - 预约管理页面")
    print("  /predictions                              - 预测分析页面")
    print("  /v2                                       - V2版首页")
    print("  /v2/dashboard                             - V2版地图页")

def demo_statistics():
    """显示统计信息"""
    print_header("5. 系统统计")
    
    with app.app_context():
        user_count = User.query.count()
        space_count = Space.query.count()
        report_count = SpaceReport.query.count()
        reservation_count = Reservation.query.count()
        
        print(f"\n📊 数据统计：")
        print(f"  用户数量: {user_count}")
        print(f"  空间数量: {space_count}")
        print(f"  上报记录: {report_count}")
        print(f"  预约记录: {reservation_count}")
        
        # 最活跃用户
        from sqlalchemy import func
        top_users = db.session.query(
            User.username,
            func.count(SpaceReport.id).label('report_count')
        ).join(SpaceReport).group_by(User.id).order_by(func.count(SpaceReport.id).desc()).limit(3).all()
        
        print(f"\n🏆 最活跃用户（上报次数）：")
        for i, (username, count) in enumerate(top_users, 1):
            print(f"  {i}. {username}: {count}次")
        
        # 最热门空间
        top_spaces = db.session.query(
            Space.name,
            func.count(SpaceReport.id).label('report_count')
        ).join(SpaceReport).group_by(Space.id).order_by(func.count(SpaceReport.id).desc()).limit(3).all()
        
        print(f"\n🔥 最热门空间（上报次数）：")
        for i, (name, count) in enumerate(top_spaces, 1):
            print(f"  {i}. {name}: {count}次")

def main():
    """主函数"""
    print("\n" + "🎉" * 30)
    print("  校园数字游民活地图 V3.0 功能演示")
    print("🎉" * 30)
    
    try:
        demo_roles()
        demo_reservations()
        demo_predictions()
        demo_api_endpoints()
        demo_statistics()
        
        print_header("演示完成")
        print("\n✅ 所有功能演示完成！")
        print("\n快速访问：")
        print("  首页: http://127.0.0.1:5000/v2")
        print("  地图: http://127.0.0.1:5000/v2/dashboard")
        print("  预约: http://127.0.0.1:5000/reservations")
        print("  预测: http://127.0.0.1:5000/predictions")
        
        print("\n示例账户：")
        print("  管理员: admin / admin123")
        print("  教师:   张教授 / password123")
        print("  学生:   张三 / password123")
        print("  访客:   访客001 / password123")
        
        print("\n" + "=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

