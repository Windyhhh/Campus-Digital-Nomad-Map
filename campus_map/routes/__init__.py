from flask import Blueprint

# 创建蓝图
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')
api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# 导入各个路由模块
from . import auth, pages, api_v1, api_v2, reservations, predictions
