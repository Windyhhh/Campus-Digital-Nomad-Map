from flask import Flask
from flask_login import LoginManager
from .config import config
from .models import db, User
from .routes import main_bp, api_bp, api_v2_bp

# 初始化登录管理器
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))

def create_app(config_name=None):
    """创建Flask应用实例"""
    if config_name is None:
        config_name = 'default'
    
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化应用配置
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(api_v2_bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 初始化示例数据
        from .utils.sample_data import init_sample_data
        init_sample_data()
    
    return app
