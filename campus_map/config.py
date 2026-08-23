import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # 密钥配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///campus_map.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 高德地图API密钥
    AMAP_KEY = os.getenv('AMAP_KEY', '')
    
    # 校园中心坐标
    CAMPUS_CENTER = [123.4644, 41.6698]  # 东北大学浑南校区中心坐标
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 静态文件配置
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 机器学习模型配置
    ML_MODEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml', 'models')
    ML_MODEL_TYPE = os.getenv('ML_MODEL_TYPE', 'random_forest')
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.ML_MODEL_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_campus_map.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # 生产环境数据库配置，优先使用环境变量
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///campus_map.db')

# 配置映射，用于根据环境变量选择不同的配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
