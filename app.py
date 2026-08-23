from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from ml_predictor import predictor

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///campus_map.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['AMAP_KEY'] = os.getenv('AMAP_KEY', '')  # 高德地图API密钥
app.config['CAMPUS_CENTER'] = [123.4644, 41.6698]  # 东北大学浑南校区中心坐标

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 关联表定义（需要在模型之前定义）
user_achievements = db.Table('user_achievements',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('achievement_id', db.Integer, db.ForeignKey('achievement.id'), primary_key=True),
    db.Column('earned_at', db.DateTime, default=datetime.utcnow)
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

# 空间标签关联表
space_tags = db.Table('space_tags',
    db.Column('space_id', db.Integer, db.ForeignKey('space.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由
@app.route('/')
def index():
    """首页 - 统一的主仪表板"""
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    spaces = Space.query.all()
    return render_template('dashboard.html', spaces=spaces)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# API路由
@app.route('/api/spaces')
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

@app.route('/api/report', methods=['POST'])
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

@app.route('/api/spaces/<int:space_id>/reports')
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

# 成就检查函数
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

@app.route('/api/user/achievements')
@login_required
def get_user_achievements():
    """获取用户成就"""
    achievements_data = []
    for achievement in current_user.achievements:
        achievements_data.append({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'icon': achievement.icon,
            'earned_at': achievement.earned_at.isoformat() if hasattr(achievement, 'earned_at') else None
        })

    return jsonify(achievements_data)

@app.route('/api/user/stats')
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

# 初始化示例数据
def init_sample_data():
    # 检查是否已有数据
    if Space.query.first():
        return

    # 创建示例空间
    spaces = [
        Space(name='图书馆阅览室', building='图书馆', floor='2F', capacity=200,
              space_type='图书馆', x_coordinate=15.6, y_coordinate=16.7),
        Space(name='A301自习室', building='A座教学楼', floor='3F', capacity=50,
              space_type='自习室', x_coordinate=38.8, y_coordinate=15.0),
        Space(name='B201讨论室', building='B座教学楼', floor='2F', capacity=20,
              space_type='讨论室', x_coordinate=57.5, y_coordinate=15.0),
        Space(name='星巴克咖啡厅', building='学生中心', floor='1F', capacity=30,
              space_type='咖啡厅', x_coordinate=12.5, y_coordinate=40.0),
        Space(name='活动中心自习区', building='学生活动中心', floor='2F', capacity=80,
              space_type='自习室', x_coordinate=34.4, y_coordinate=41.7),
    ]

    for space in spaces:
        db.session.add(space)

    # 创建示例标签
    tags = [
        Tag(name='安静', color='#28a745'),
        Tag(name='有电源', color='#ffc107'),
        Tag(name='网速快', color='#007bff'),
        Tag(name='适合讨论', color='#6f42c1'),
        Tag(name='光线好', color='#fd7e14'),
        Tag(name='宽敞', color='#20c997'),
    ]

    for tag in tags:
        db.session.add(tag)

    db.session.commit()

# V2版本路由 - 使用新模板
@app.route('/v2')
def index_v2():
    return render_template('index_v2.html')

@app.route('/v2/dashboard')
@login_required
def dashboard_v2():
    return render_template('dashboard_v2.html', amap_key=app.config['AMAP_KEY'])

# API: 获取热力图数据
@app.route('/api/v2/heatmap')
@login_required
def get_heatmap_data():
    """获取校园热力图数据"""
    try:
        # 获取最近24小时的上报数据
        from datetime import timedelta
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

# API: 空间预约
@app.route('/api/v2/reserve', methods=['POST'])
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

# API: 获取用户预约列表
@app.route('/api/reservations')
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

# API: 取消预约
@app.route('/api/reservations/<int:reservation_id>/cancel', methods=['POST'])
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

# API: 审核预约（管理员/教师）
@app.route('/api/reservations/<int:reservation_id>/approve', methods=['POST'])
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

# API: 获取实时通知
@app.route('/api/v2/notifications')
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

# API: 训练预测模型
@app.route('/api/ml/train', methods=['POST'])
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
@app.route('/api/ml/predict/<int:space_id>')
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
@app.route('/api/ml/predict-all')
@login_required
def predict_all_spaces():
    """预测所有空间的拥挤度"""
    try:
        spaces = Space.query.all()

        # 尝试加载模型
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

# 页面路由: 预测分析页面
@app.route('/predictions')
@login_required
def predictions_page():
    """预测分析页面"""
    return render_template('predictions.html')

# 页面路由: 预约管理页面
@app.route('/reservations')
@login_required
def reservations_page():
    """预约管理页面"""
    return render_template('reservations.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    app.run(debug=True)
