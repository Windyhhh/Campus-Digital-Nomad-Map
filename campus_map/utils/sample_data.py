from ..models import db, Space, Tag

def init_sample_data():
    """初始化示例数据"""
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
