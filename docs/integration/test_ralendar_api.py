#!/usr/bin/env python3
"""
Ralendar API 测试脚本 - 供 Roamio 团队验证集成

使用方法:
    python test_ralendar_api.py --token YOUR_ACCESS_TOKEN
"""

import requests
import json
import argparse
from datetime import datetime, timedelta

# Ralendar API 配置
BASE_URL = 'https://app7626.acapp.acwing.com.cn/api/v1'

class RalendarAPITester:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.test_trip_slug = f'test-trip-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    
    def print_result(self, test_name, success, response=None, error=None):
        """打印测试结果"""
        status = '✅' if success else '❌'
        print(f'\n{status} {test_name}')
        
        if response:
            print(f'   状态码: {response.status_code}')
            if response.status_code < 400:
                try:
                    data = response.json()
                    print(f'   响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...')
                except:
                    print(f'   响应: {response.text[:200]}...')
        
        if error:
            print(f'   错误: {error}')
    
    def test_1_auth_check(self):
        """测试 1: 验证 Token 是否有效"""
        print('\n' + '='*60)
        print('测试 1: Token 验证')
        print('='*60)
        
        try:
            response = requests.get(
                f'{BASE_URL}/auth/me/',
                headers=self.headers,
                timeout=10
            )
            
            success = response.status_code == 200
            self.print_result('Token 验证', success, response)
            
            if success:
                user = response.json()
                print(f'   ✅ 用户: {user.get("username")} ({user.get("email")})')
            
            return success
        except Exception as e:
            self.print_result('Token 验证', False, error=str(e))
            return False
    
    def test_2_create_single_event(self):
        """测试 2: 创建单个事件"""
        print('\n' + '='*60)
        print('测试 2: 创建单个事件')
        print('='*60)
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        event_data = {
            'title': f'测试事件 - {datetime.now().strftime("%H:%M:%S")}',
            'description': '这是一个测试事件（来自 Roamio API 测试）',
            'start_time': f'{tomorrow}T10:00:00+08:00',
            'end_time': f'{tomorrow}T12:00:00+08:00',
            'location': '测试地点',
            'latitude': 39.9163,
            'longitude': 116.3972,
            'reminder_minutes': 60,
            'email_reminder': False,
            'source_app': 'roamio',
            'related_trip_slug': self.test_trip_slug
        }
        
        try:
            response = requests.post(
                f'{BASE_URL}/events/',
                headers=self.headers,
                json=event_data,
                timeout=10
            )
            
            success = response.status_code == 201
            self.print_result('创建单个事件', success, response)
            
            if success:
                event = response.json()
                self.created_event_id = event.get('id')
                print(f'   ✅ 事件ID: {self.created_event_id}')
            
            return success
        except Exception as e:
            self.print_result('创建单个事件', False, error=str(e))
            return False
    
    def test_3_batch_create_events(self):
        """测试 3: 批量创建事件"""
        print('\n' + '='*60)
        print('测试 3: 批量创建事件')
        print('='*60)
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        
        batch_data = {
            'source_app': 'roamio',
            'related_trip_slug': self.test_trip_slug,
            'events': [
                {
                    'title': '批量测试 - 事件1',
                    'start_time': f'{tomorrow}T09:00:00+08:00',
                    'end_time': f'{tomorrow}T10:00:00+08:00',
                    'location': '北京故宫',
                    'latitude': 39.9163,
                    'longitude': 116.3972
                },
                {
                    'title': '批量测试 - 事件2',
                    'start_time': f'{tomorrow}T14:00:00+08:00',
                    'end_time': f'{tomorrow}T16:00:00+08:00',
                    'location': '颐和园'
                },
                {
                    'title': '批量测试 - 事件3',
                    'start_time': f'{day_after}T10:00:00+08:00',
                    'end_time': f'{day_after}T18:00:00+08:00',
                    'location': '长城'
                }
            ]
        }
        
        try:
            response = requests.post(
                f'{BASE_URL}/fusion/events/batch/',
                headers=self.headers,
                json=batch_data,
                timeout=10
            )
            
            success = response.status_code == 201
            self.print_result('批量创建事件', success, response)
            
            if success:
                result = response.json()
                print(f'   ✅ 创建数量: {result.get("created_count")}')
                print(f'   ⚠️  跳过数量: {result.get("skipped_count")}')
            
            return success
        except Exception as e:
            self.print_result('批量创建事件', False, error=str(e))
            return False
    
    def test_4_get_trip_events(self):
        """测试 4: 获取旅行计划的事件"""
        print('\n' + '='*60)
        print('测试 4: 获取旅行计划的事件')
        print('='*60)
        
        try:
            response = requests.get(
                f'{BASE_URL}/fusion/events/trip/{self.test_trip_slug}/',
                headers=self.headers,
                timeout=10
            )
            
            success = response.status_code == 200
            self.print_result('获取旅行事件', success, response)
            
            if success:
                result = response.json()
                count = result.get('count', 0)
                print(f'   ✅ 事件数量: {count}')
                
                # 期望至少有 4 个事件（测试2创建1个 + 测试3创建3个）
                if count >= 4:
                    print(f'   ✅ 数量正确（>=4）')
                else:
                    print(f'   ⚠️  数量不符合预期（期望>=4，实际{count}）')
            
            return success
        except Exception as e:
            self.print_result('获取旅行事件', False, error=str(e))
            return False
    
    def test_5_update_event(self):
        """测试 5: 更新事件"""
        print('\n' + '='*60)
        print('测试 5: 更新事件')
        print('='*60)
        
        if not hasattr(self, 'created_event_id'):
            print('   ⚠️  跳过：没有可更新的事件ID')
            return False
        
        update_data = {
            'title': f'测试事件（已更新）- {datetime.now().strftime("%H:%M:%S")}',
            'description': '这个事件已被更新'
        }
        
        try:
            response = requests.patch(
                f'{BASE_URL}/events/{self.created_event_id}/',
                headers=self.headers,
                json=update_data,
                timeout=10
            )
            
            success = response.status_code == 200
            self.print_result('更新事件', success, response)
            
            return success
        except Exception as e:
            self.print_result('更新事件', False, error=str(e))
            return False
    
    def test_6_delete_trip_events(self):
        """测试 6: 删除旅行计划的所有事件"""
        print('\n' + '='*60)
        print('测试 6: 删除旅行计划的所有事件')
        print('='*60)
        
        try:
            response = requests.delete(
                f'{BASE_URL}/fusion/events/trip/{self.test_trip_slug}/',
                headers=self.headers,
                timeout=10
            )
            
            success = response.status_code == 200
            self.print_result('删除旅行事件', success, response)
            
            if success:
                result = response.json()
                print(f'   ✅ 删除数量: {result.get("deleted_count")}')
            
            return success
        except Exception as e:
            self.print_result('删除旅行事件', False, error=str(e))
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print('\n' + '='*60)
        print('🚀 Ralendar API 测试开始')
        print('='*60)
        print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'API 地址: {BASE_URL}')
        print(f'测试 Trip: {self.test_trip_slug}')
        
        results = {}
        
        # 按顺序运行测试
        results['1. Token 验证'] = self.test_1_auth_check()
        
        if not results['1. Token 验证']:
            print('\n❌ Token 验证失败，终止测试')
            print('\n建议检查：')
            print('  1. Token 是否正确')
            print('  2. Token 是否已过期')
            print('  3. Roamio 和 Ralendar 的 SECRET_KEY 是否一致')
            return results
        
        results['2. 创建单个事件'] = self.test_2_create_single_event()
        results['3. 批量创建事件'] = self.test_3_batch_create_events()
        results['4. 获取旅行事件'] = self.test_4_get_trip_events()
        results['5. 更新事件'] = self.test_5_update_event()
        results['6. 删除旅行事件'] = self.test_6_delete_trip_events()
        
        # 汇总结果
        print('\n' + '='*60)
        print('📊 测试结果汇总')
        print('='*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, success in results.items():
            status = '✅' if success else '❌'
            print(f'{status} {test_name}')
        
        print(f'\n通过: {passed}/{total}')
        
        if passed == total:
            print('\n🎉 所有测试通过！Ralendar API 集成准备就绪！')
        else:
            print(f'\n⚠️  部分测试失败（{total - passed} 个）')
            print('\n建议检查：')
            print('  1. 网络连接是否正常')
            print('  2. API 地址是否正确')
            print('  3. 请求数据格式是否符合规范')
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='测试 Ralendar API 集成（供 Roamio 团队使用）'
    )
    parser.add_argument(
        '--token',
        required=True,
        help='用户的 JWT access_token'
    )
    parser.add_argument(
        '--base-url',
        default=BASE_URL,
        help=f'Ralendar API 基础 URL（默认: {BASE_URL}）'
    )
    
    args = parser.parse_args()
    
    # 更新全局 BASE_URL
    global BASE_URL
    BASE_URL = args.base_url
    
    # 运行测试
    tester = RalendarAPITester(args.token)
    results = tester.run_all_tests()
    
    # 返回退出码
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        exit(0)  # 所有测试通过
    else:
        exit(1)  # 部分测试失败


if __name__ == '__main__':
    main()

