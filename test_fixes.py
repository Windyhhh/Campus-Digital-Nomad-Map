#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试修复后的功能
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000'

# 测试账户
TEST_USER = {
    'username': 'admin',
    'password': 'admin123'
}

session = requests.Session()

def test_login():
    """测试登录"""
    print("\n" + "="*60)
    print("🔐 测试登录功能")
    print("="*60)
    
    response = session.post(f'{BASE_URL}/login', data=TEST_USER)
    if response.status_code == 200:
        print("✅ 登录成功")
        return True
    else:
        print(f"❌ 登录失败: {response.status_code}")
        return False

def test_get_reservations():
    """测试获取预约列表"""
    print("\n" + "="*60)
    print("📅 测试获取预约列表")
    print("="*60)
    
    try:
        response = session.get(f'{BASE_URL}/api/reservations')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取预约列表成功，共 {len(data)} 条预约")
            if data:
                print(f"   第一条预约: {data[0]['space_name']} - {data[0]['status_display']}")
            return True
        else:
            print(f"❌ 获取预约列表失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 获取预约列表异常: {str(e)}")
        return False

def test_get_spaces():
    """测试获取空间列表"""
    print("\n" + "="*60)
    print("🏢 测试获取空间列表")
    print("="*60)
    
    try:
        response = session.get(f'{BASE_URL}/api/spaces')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取空间列表成功，共 {len(data)} 个空间")
            if data:
                space = data[0]
                print(f"   第一个空间: {space['name']}")
                print(f"   - 位置: {space.get('building', 'N/A')} {space.get('floor', 'N/A')}")
                print(f"   - 容量: {space['capacity']}人")
                print(f"   - 拥挤度: {space.get('crowding', 'N/A')}")
            return True
        else:
            print(f"❌ 获取空间列表失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 获取空间列表异常: {str(e)}")
        return False

def test_predict_all():
    """测试批量预测"""
    print("\n" + "="*60)
    print("🤖 测试批量预测功能")
    print("="*60)
    
    try:
        response = session.get(f'{BASE_URL}/api/ml/predict-all')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 批量预测成功，共 {len(data)} 个空间的预测")
            if data:
                pred = data[0]
                print(f"   第一个预测: {pred['space_name']}")
                print(f"   - 下一小时预测: {pred.get('next_hour', 'N/A')}")
            return True
        else:
            print(f"❌ 批量预测失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 批量预测异常: {str(e)}")
        return False

def test_heatmap():
    """测试热力图数据"""
    print("\n" + "="*60)
    print("🔥 测试热力图数据")
    print("="*60)
    
    try:
        response = session.get(f'{BASE_URL}/api/v2/heatmap')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取热力图数据成功，共 {len(data)} 个数据点")
            if data:
                point = data[0]
                print(f"   第一个数据点: {point['name']}")
                print(f"   - 位置: {point.get('location', 'N/A')}")
                print(f"   - 平均拥挤度: {point.get('avg_crowding', 'N/A')}")
            return True
        else:
            print(f"❌ 获取热力图数据失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 获取热力图数据异常: {str(e)}")
        return False

def test_pages():
    """测试页面访问"""
    print("\n" + "="*60)
    print("📄 测试页面访问")
    print("="*60)
    
    pages = [
        ('/', '首页'),
        ('/v2/dashboard', '地图页'),
        ('/reservations', '预约页'),
        ('/predictions', '预测页'),
        ('/profile', '个人中心'),
    ]
    
    results = []
    for url, name in pages:
        try:
            response = session.get(f'{BASE_URL}{url}')
            if response.status_code == 200:
                print(f"✅ {name}: 200 OK")
                results.append(True)
            else:
                print(f"❌ {name}: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            results.append(False)
    
    return all(results)

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🧪 开始测试修复后的功能")
    print("="*60)
    
    results = []
    
    # 测试登录
    if test_login():
        # 测试各个API
        results.append(("登录", test_login()))
        results.append(("获取预约列表", test_get_reservations()))
        results.append(("获取空间列表", test_get_spaces()))
        results.append(("批量预测", test_predict_all()))
        results.append(("热力图数据", test_heatmap()))
        results.append(("页面访问", test_pages()))
    else:
        print("❌ 登录失败，无法继续测试")
        return
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")

if __name__ == '__main__':
    main()

