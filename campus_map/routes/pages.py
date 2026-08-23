from flask import render_template
from flask_login import login_required
from . import main_bp
from ..models import Space

@main_bp.route('/')
def index():
    """首页 - 统一的主仪表板"""
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    spaces = Space.query.all()
    return render_template('dashboard.html', spaces=spaces)

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# V2版本路由 - 使用新模板
@main_bp.route('/v2')
def index_v2():
    return render_template('index_v2.html')

@main_bp.route('/v2/dashboard')
@login_required
def dashboard_v2():
    from flask import current_app
    return render_template('dashboard_v2.html', amap_key=current_app.config['AMAP_KEY'])

# 页面路由: 预测分析页面
@main_bp.route('/predictions')
@login_required
def predictions_page():
    """预测分析页面"""
    return render_template('predictions.html')

# 页面路由: 预约管理页面
@main_bp.route('/reservations')
@login_required
def reservations_page():
    """预约管理页面"""
    return render_template('reservations.html')
