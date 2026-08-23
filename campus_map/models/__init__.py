from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化数据库
db = SQLAlchemy()

# 关联表定义（需要在模型之前定义）
user_achievements = db.Table('user_achievements',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('achievement_id', db.Integer, db.ForeignKey('achievement.id'), primary_key=True),
    db.Column('earned_at', db.DateTime, default=datetime.utcnow)
)

# 空间标签关联表
space_tags = db.Table('space_tags',
    db.Column('space_id', db.Integer, db.ForeignKey('space.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, teacher, admin, visitor
    department = db.Column(db.String(100))  # 院系/部门
    student_id = db.Column(db.String(20))  # 学号/工号
    phone = db.Column(db.String(20))  # 联系电话
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_role_display(self):
        """获取角色显示名称"""
        role_map = {
            'student': '学生',
            'teacher': '教师',
            'admin': '管理员',
            'visitor': '访客'
        }
        return role_map.get(self.role, '未知')

    def has_permission(self, permission):
        """检查用户权限"""
        permissions = {
            'admin': ['manage_users', 'manage_spaces', 'view_analytics', 'manage_reservations'],
            'teacher': ['reserve_priority', 'view_analytics', 'manage_reservations'],
            'student': ['reserve_normal', 'report_space'],
            'visitor': ['view_only']
        }
        return permission in permissions.get(self.role, [])

    # 用户成就关系
    achievements = db.relationship('Achievement', secondary=user_achievements, backref=db.backref('users', lazy='dynamic'))
    # 用户预约关系
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')

# 空间模型
class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(50), nullable=False)
    floor = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    space_type = db.Column(db.String(50), nullable=False)  # 自习室、讨论室、咖啡厅等
    x_coordinate = db.Column(db.Float, nullable=False)
    y_coordinate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def location(self):
        """获取位置信息（building + floor）"""
        return f"{self.building} {self.floor}"

    @property
    def type(self):
        """获取空间类型（兼容旧代码）"""
        return self.space_type

# 空间状态上报模型
class SpaceReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crowding_level = db.Column(db.Integer, nullable=False)  # 1-5级拥挤度
    noise_level = db.Column(db.Integer, nullable=False)  # 1-5级噪音
    power_available = db.Column(db.Boolean, default=True)
    wifi_quality = db.Column(db.Integer, nullable=False)  # 1-5级网速
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    space = db.relationship('Space', backref=db.backref('reports', lazy=True))
    user = db.relationship('User', backref=db.backref('reports', lazy=True))

# 标签模型
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#007bff')  # 十六进制颜色

# 成就模型
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='fas fa-trophy')
    points_required = db.Column(db.Integer, default=0)
    reports_required = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 预约模型
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.String(200))  # 预约目的
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled, completed
    num_people = db.Column(db.Integer, default=1)  # 预约人数
    notes = db.Column(db.Text)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_status_display(self):
        """获取状态显示名称"""
        status_map = {
            'pending': '待审核',
            'approved': '已批准',
            'rejected': '已拒绝',
            'cancelled': '已取消',
            'completed': '已完成'
        }
        return status_map.get(self.status, '未知')

    def get_status_color(self):
        """获取状态颜色"""
        color_map = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
            'completed': 'info'
        }
        return color_map.get(self.status, 'secondary')

    def is_active(self):
        """检查预约是否有效"""
        return self.status == 'approved' and self.end_time > datetime.utcnow()

    # 关系
    space = db.relationship('Space', backref=db.backref('reservations', lazy=True))

    def can_cancel(self, user):
        """检查是否可以取消"""
        if user.role == 'admin':
            return True
        if self.user_id == user.id and self.status in ['pending', 'approved']:
            return self.start_time > datetime.utcnow()
        return False
