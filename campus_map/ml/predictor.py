"""
机器学习预测模块
使用历史数据预测未来时段的教室人数
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import joblib
import os

class CrowdingPredictor:
    """教室拥挤度预测器"""
    
    def __init__(self, model_path='../ml/models/crowding_model.pkl'):
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建绝对路径
        self.model_path = os.path.join(current_dir, 'models', 'crowding_model.pkl')
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'hour', 'day_of_week', 'is_weekend', 'is_exam_period',
            'space_capacity', 'space_type_encoded', 'avg_crowding_last_week',
            'avg_crowding_same_time_last_week', 'trend_last_3_days'
        ]
        
    def extract_features(self, datetime_obj, space, historical_data=None):
        """从时间和空间信息中提取特征"""
        features = {}
        
        # 时间特征
        features['hour'] = datetime_obj.hour
        features['day_of_week'] = datetime_obj.weekday()
        features['is_weekend'] = 1 if datetime_obj.weekday() >= 5 else 0
        
        # 考试周期特征（简化版，可根据实际校历调整）
        month = datetime_obj.month
        features['is_exam_period'] = 1 if month in [1, 6, 7, 12] else 0
        
        # 空间特征
        features['space_capacity'] = space.get('capacity', 50)
        
        # 空间类型编码
        space_type_map = {
            '图书馆': 1,
            '自习室': 2,
            '讨论室': 3,
            '实验室': 4,
            '教室': 5,
            '咖啡厅': 6
        }
        features['space_type_encoded'] = space_type_map.get(space.get('type', ''), 0)
        
        # 历史数据特征
        if historical_data and len(historical_data) > 0:
            # 过去一周平均拥挤度
            features['avg_crowding_last_week'] = np.mean([d['crowding_level'] for d in historical_data[-7:]])
            
            # 上周同一时间的拥挤度
            same_time_data = [d for d in historical_data if d['hour'] == features['hour'] and d['day_of_week'] == features['day_of_week']]
            features['avg_crowding_same_time_last_week'] = np.mean([d['crowding_level'] for d in same_time_data]) if same_time_data else 3.0
            
            # 最近3天的趋势
            if len(historical_data) >= 3:
                recent_crowding = [d['crowding_level'] for d in historical_data[-3:]]
                features['trend_last_3_days'] = (recent_crowding[-1] - recent_crowding[0]) / 3
            else:
                features['trend_last_3_days'] = 0
        else:
            # 默认值
            features['avg_crowding_last_week'] = 3.0
            features['avg_crowding_same_time_last_week'] = 3.0
            features['trend_last_3_days'] = 0
        
        return features
    
    def prepare_training_data(self, reports_data):
        """准备训练数据"""
        features_list = []
        labels = []
        
        for report in reports_data:
            # 提取特征
            datetime_obj = report['created_at']
            space = report['space']
            
            # 获取该报告之前的历史数据
            historical = [r for r in reports_data if r['created_at'] < datetime_obj and r['space_id'] == report['space_id']]
            
            features = self.extract_features(datetime_obj, space, historical)
            features_list.append(list(features.values()))
            labels.append(report['crowding_level'])
        
        return np.array(features_list), np.array(labels)
    
    def train(self, reports_data, model_type='random_forest'):
        """训练模型"""
        print(f"开始训练模型，数据量: {len(reports_data)}")
        
        # 准备数据
        X, y = self.prepare_training_data(reports_data)
        
        if len(X) < 10:
            print("警告：训练数据不足，使用默认模型")
            self.model = LinearRegression()
        else:
            # 数据标准化
            X = self.scaler.fit_transform(X)
            
            # 分割训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 选择模型
            if model_type == 'random_forest':
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    random_state=42
                )
            elif model_type == 'gradient_boosting':
                self.model = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
            else:
                self.model = LinearRegression()
            
            # 训练模型
            self.model.fit(X_train, y_train)
            
            # 评估模型
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            print(f"训练集得分: {train_score:.4f}")
            print(f"测试集得分: {test_score:.4f}")
        
        # 保存模型
        self.save_model()
        
        return self.model
    
    def predict(self, datetime_obj, space, historical_data=None):
        """预测指定时间和空间的拥挤度"""
        if self.model is None:
            # 如果没有训练模型，返回默认值
            return self._default_prediction(datetime_obj, space)
        
        # 提取特征
        features = self.extract_features(datetime_obj, space, historical_data)
        X = np.array([list(features.values())])
        
        # 标准化
        if hasattr(self.scaler, 'mean_'):
            X = self.scaler.transform(X)
        
        # 预测
        prediction = self.model.predict(X)[0]
        
        # 限制在1-5范围内
        prediction = max(1, min(5, prediction))
        
        return round(prediction, 2)
    
    def predict_next_hours(self, space, historical_data=None, hours=6):
        """预测未来几个小时的拥挤度"""
        predictions = []
        current_time = datetime.now()
        
        for i in range(hours):
            future_time = current_time + timedelta(hours=i+1)
            crowding = self.predict(future_time, space, historical_data)
            
            predictions.append({
                'time': future_time.strftime('%H:%M'),
                'datetime': future_time.isoformat(),
                'crowding_level': crowding,
                'crowding_text': self._get_crowding_text(crowding),
                'color': self._get_crowding_color(crowding)
            })
        
        return predictions
    
    def _default_prediction(self, datetime_obj, space):
        """基于规则的默认预测（当没有训练模型时）"""
        hour = datetime_obj.hour
        day_of_week = datetime_obj.weekday()
        
        # 基础拥挤度
        base_crowding = 3.0
        
        # 时间因素
        if 8 <= hour <= 11 or 14 <= hour <= 17:
            base_crowding += 1.0  # 上课时间更拥挤
        elif hour < 8 or hour > 21:
            base_crowding -= 1.5  # 早晚时间较空闲
        
        # 周末因素
        if day_of_week >= 5:
            base_crowding -= 0.5
        
        # 空间类型因素
        if space.get('type') == '图书馆':
            base_crowding += 0.5
        elif space.get('type') == '咖啡厅':
            base_crowding -= 0.3
        
        # 限制在1-5范围内
        return max(1, min(5, base_crowding))
    
    def _get_crowding_text(self, level):
        """获取拥挤度文本描述"""
        if level <= 1.5:
            return '很空闲'
        elif level <= 2.5:
            return '较空闲'
        elif level <= 3.5:
            return '一般'
        elif level <= 4.5:
            return '较拥挤'
        else:
            return '很拥挤'
    
    def _get_crowding_color(self, level):
        """获取拥挤度颜色"""
        if level <= 1.5:
            return '#10B981'  # 绿色
        elif level <= 2.5:
            return '#84CC16'  # 黄绿色
        elif level <= 3.5:
            return '#F59E0B'  # 橙色
        elif level <= 4.5:
            return '#EF4444'  # 红色
        else:
            return '#991B1B'  # 深红色
    
    def save_model(self):
        """保存模型"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, self.model_path)
        print(f"模型已保存到: {self.model_path}")
    
    def load_model(self):
        """加载模型"""
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.scaler = data['scaler']
            print(f"模型已从 {self.model_path} 加载")
            return True
        return False

# 全局预测器实例
predictor = CrowdingPredictor()

