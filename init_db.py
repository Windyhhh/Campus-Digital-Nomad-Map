#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和插入示例数据
"""

import os
import sys
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Space, SpaceReport, Tag, Achievement, Reservation, space_tags, user_achievements

def create_tables():
    """创建数据库表"""
    print("正在创建数据库表...")
    with app.app_context():
        db.create_all()
        print("数据库表创建完成！")

def create_sample_users():
    """创建示例用户"""
    print("正在创建示例用户...")

    users_data = [
        {'username': 'admin', 'email': 'admin@neu.edu.cn', 'password': 'admin123', 'points': 500, 'role': 'admin', 'department': '信息中心', 'student_id': 'A001', 'phone': '13800138000'},
        {'username': '张教授', 'email': 'zhang@neu.edu.cn', 'password': 'password123', 'points': 300, 'role': 'teacher', 'department': '计算机学院', 'student_id': 'T001', 'phone': '13800138001'},
        {'username': '李老师', 'email': 'li@neu.edu.cn', 'password': 'password123', 'points': 250, 'role': 'teacher', 'department': '软件学院', 'student_id': 'T002', 'phone': '13800138002'},
        {'username': '张三', 'email': 'zhangsan@stu.neu.edu.cn', 'password': 'password123', 'points': 150, 'role': 'student', 'department': '计算机学院', 'student_id': '20210001', 'phone': '13900139001'},
        {'username': '李四', 'email': 'lisi@stu.neu.edu.cn', 'password': 'password123', 'points': 200, 'role': 'student', 'department': '软件学院', 'student_id': '20210002', 'phone': '13900139002'},
        {'username': '王五', 'email': 'wangwu@stu.neu.edu.cn', 'password': 'password123', 'points': 80, 'role': 'student', 'department': '信息学院', 'student_id': '20210003', 'phone': '13900139003'},
        {'username': '赵六', 'email': 'zhaoliu@stu.neu.edu.cn', 'password': 'password123', 'points': 300, 'role': 'student', 'department': '计算机学院', 'student_id': '20210004', 'phone': '13900139004'},
        {'username': '访客001', 'email': 'visitor@example.com', 'password': 'password123', 'points': 0, 'role': 'visitor', 'department': '校外', 'student_id': 'V001', 'phone': '13900139005'},
    ]

    for user_data in users_data:
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                points=user_data['points'],
                role=user_data['role'],
                department=user_data.get('department'),
                student_id=user_data.get('student_id'),
                phone=user_data.get('phone')
            )
            user.set_password(user_data['password'])
            db.session.add(user)

    db.session.commit()
    print(f"创建了 {len(users_data)} 个示例用户（管理员、教师、学生、访客）")

def create_sample_spaces():
    """创建示例空间"""
    print("正在创建示例空间...")
    
    spaces_data = [
        {
            'name': '图书馆阅览室',
            'building': '图书馆',
            'floor': '2F',
            'capacity': 200,
            'space_type': '图书馆',
            'x_coordinate': 15.6,
            'y_coordinate': 16.7
        },
        {
            'name': 'A301自习室',
            'building': 'A座教学楼',
            'floor': '3F',
            'capacity': 50,
            'space_type': '自习室',
            'x_coordinate': 38.8,
            'y_coordinate': 15.0
        },
        {
            'name': 'A302自习室',
            'building': 'A座教学楼',
            'floor': '3F',
            'capacity': 45,
            'space_type': '自习室',
            'x_coordinate': 40.0,
            'y_coordinate': 18.0
        },
        {
            'name': 'B201讨论室',
            'building': 'B座教学楼',
            'floor': '2F',
            'capacity': 20,
            'space_type': '讨论室',
            'x_coordinate': 57.5,
            'y_coordinate': 15.0
        },
        {
            'name': 'B202讨论室',
            'building': 'B座教学楼',
            'floor': '2F',
            'capacity': 15,
            'space_type': '讨论室',
            'x_coordinate': 59.0,
            'y_coordinate': 18.0
        },
        {
            'name': 'C101实验室',
            'building': 'C座教学楼',
            'floor': '1F',
            'capacity': 30,
            'space_type': '实验室',
            'x_coordinate': 76.3,
            'y_coordinate': 15.0
        },
        {
            'name': '星巴克咖啡厅',
            'building': '学生中心',
            'floor': '1F',
            'capacity': 30,
            'space_type': '咖啡厅',
            'x_coordinate': 12.5,
            'y_coordinate': 40.0
        },
        {
            'name': '活动中心自习区',
            'building': '学生活动中心',
            'floor': '2F',
            'capacity': 80,
            'space_type': '自习室',
            'x_coordinate': 34.4,
            'y_coordinate': 41.7
        },
        {
            'name': '食堂休息区',
            'building': '第一食堂',
            'floor': '2F',
            'capacity': 40,
            'space_type': '休息区',
            'x_coordinate': 13.8,
            'y_coordinate': 65.0
        },
        {
            'name': '体育馆休息室',
            'building': '体育馆',
            'floor': '1F',
            'capacity': 25,
            'space_type': '休息区',
            'x_coordinate': 31.3,
            'y_coordinate': 65.0
        }
    ]
    
    for space_data in spaces_data:
        # 检查空间是否已存在
        existing_space = Space.query.filter_by(
            name=space_data['name'], 
            building=space_data['building']
        ).first()
        
        if not existing_space:
            space = Space(**space_data)
            db.session.add(space)
    
    db.session.commit()
    print(f"创建了 {len(spaces_data)} 个示例空间")

def create_sample_tags():
    """创建示例标签"""
    print("正在创建示例标签...")
    
    tags_data = [
        {'name': '安静', 'color': '#28a745'},
        {'name': '有电源', 'color': '#ffc107'},
        {'name': '网速快', 'color': '#007bff'},
        {'name': '适合讨论', 'color': '#6f42c1'},
        {'name': '光线好', 'color': '#fd7e14'},
        {'name': '宽敞', 'color': '#20c997'},
        {'name': '有投影', 'color': '#dc3545'},
        {'name': '空调', 'color': '#6c757d'},
        {'name': '靠窗', 'color': '#17a2b8'},
        {'name': '24小时', 'color': '#343a40'},
    ]
    
    for tag_data in tags_data:
        # 检查标签是否已存在
        existing_tag = Tag.query.filter_by(name=tag_data['name']).first()
        if not existing_tag:
            tag = Tag(**tag_data)
            db.session.add(tag)
    
    db.session.commit()
    print(f"创建了 {len(tags_data)} 个示例标签")

def create_sample_achievements():
    """创建示例成就"""
    print("正在创建示例成就...")

    achievements_data = [
        {
            'name': '新手上路',
            'description': '完成第一次空间状态上报',
            'icon': 'fas fa-baby',
            'reports_required': 1
        },
        {
            'name': '积极贡献者',
            'description': '累计上报10次空间状态',
            'icon': 'fas fa-hand-holding-heart',
            'reports_required': 10
        },
        {
            'name': '空间探索者',
            'description': '上报过5个不同的空间',
            'icon': 'fas fa-compass',
            'reports_required': 5
        },
        {
            'name': '信息达人',
            'description': '累计获得100积分',
            'icon': 'fas fa-star',
            'points_required': 100
        },
        {
            'name': '校园专家',
            'description': '累计获得500积分',
            'icon': 'fas fa-graduation-cap',
            'points_required': 500
        },
        {
            'name': '超级贡献者',
            'description': '累计上报50次空间状态',
            'icon': 'fas fa-trophy',
            'reports_required': 50
        }
    ]

    for achievement_data in achievements_data:
        # 检查成就是否已存在
        existing_achievement = Achievement.query.filter_by(name=achievement_data['name']).first()
        if not existing_achievement:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)

    db.session.commit()
    print(f"创建了 {len(achievements_data)} 个示例成就")

def create_sample_reports():
    """创建示例上报数据"""
    print("正在创建示例上报数据...")
    
    users = User.query.all()
    spaces = Space.query.all()
    
    if not users or not spaces:
        print("没有用户或空间数据，跳过创建上报数据")
        return
    
    # 为每个空间创建一些历史上报数据
    report_count = 0
    for space in spaces:
        # 每个空间创建3-8个上报记录
        num_reports = random.randint(3, 8)
        
        for i in range(num_reports):
            # 随机选择用户
            user = random.choice(users)
            
            # 生成随机的上报时间（过去7天内）
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            report_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # 生成随机的状态数据
            report = SpaceReport(
                space_id=space.id,
                user_id=user.id,
                crowding_level=random.randint(1, 5),
                noise_level=random.randint(1, 5),
                wifi_quality=random.randint(1, 5),
                power_available=random.choice([True, False]),
                comment=random.choice([
                    '', '环境不错', '人比较多', '很安静', '网速有点慢', 
                    '适合学习', '光线很好', '有点吵', '空调温度刚好', '推荐！'
                ]),
                created_at=report_time
            )
            
            db.session.add(report)
            report_count += 1
    
    db.session.commit()
    print(f"创建了 {report_count} 条示例上报数据")

def create_sample_reservations():
    """创建示例预约数据"""
    print("正在创建示例预约数据...")

    users = User.query.all()
    spaces = Space.query.all()

    if not users or not spaces:
        print("警告：没有用户或空间数据，跳过预约创建")
        return

    reservation_count = 0
    now = datetime.now()

    # 创建一些未来的预约
    for i in range(15):
        user = random.choice(users)
        space = random.choice(spaces)

        # 随机生成未来1-7天的预约
        days_ahead = random.randint(0, 7)
        hour = random.randint(8, 20)

        start_time = now + timedelta(days=days_ahead, hours=hour-now.hour, minutes=-now.minute, seconds=-now.second)
        duration = random.choice([1, 2, 3, 4])  # 1-4小时
        end_time = start_time + timedelta(hours=duration)

        # 随机状态
        if days_ahead == 0:
            status = random.choice(['pending', 'approved', 'cancelled'])
        else:
            status = random.choice(['pending', 'approved'])

        # 预约目的
        purposes = [
            '小组讨论', '自习', '项目会议', '考试复习',
            '论文写作', '编程实践', '课程作业', '学术研讨'
        ]

        reservation = Reservation(
            user_id=user.id,
            space_id=space.id,
            start_time=start_time,
            end_time=end_time,
            purpose=random.choice(purposes),
            num_people=random.randint(1, 6),
            status=status,
            notes=random.choice(['', '需要投影仪', '需要白板', '需要安静环境', ''])
        )

        db.session.add(reservation)
        reservation_count += 1

    # 创建一些过去的预约（已完成）
    for i in range(10):
        user = random.choice(users)
        space = random.choice(spaces)

        days_ago = random.randint(1, 30)
        hour = random.randint(8, 20)

        start_time = now - timedelta(days=days_ago, hours=now.hour-hour, minutes=now.minute, seconds=now.second)
        duration = random.randint(1, 4)
        end_time = start_time + timedelta(hours=duration)

        reservation = Reservation(
            user_id=user.id,
            space_id=space.id,
            start_time=start_time,
            end_time=end_time,
            purpose=random.choice(['小组讨论', '自习', '项目会议', '考试复习']),
            num_people=random.randint(1, 6),
            status='completed',
            notes=''
        )

        db.session.add(reservation)
        reservation_count += 1

    db.session.commit()
    print(f"创建了 {reservation_count} 条示例预约数据")

def main():
    """主函数"""
    print("开始初始化数据库...")
    print("=" * 50)

    with app.app_context():
        # 创建表
        create_tables()

        # 创建示例数据
        create_sample_users()
        create_sample_spaces()
        create_sample_tags()
        create_sample_achievements()
        create_sample_reports()
        create_sample_reservations()

        print("=" * 50)
        print("数据库初始化完成！")
        print("\n示例账户信息：")
        print("管理员账户: admin / admin123")
        print("教师账户: 张教授 / password123")
        print("教师账户: 李老师 / password123")
        print("学生账户: 张三 / password123")
        print("学生账户: 李四 / password123")
        print("\n请使用以上账户登录系统进行测试。")

if __name__ == '__main__':
    main()
