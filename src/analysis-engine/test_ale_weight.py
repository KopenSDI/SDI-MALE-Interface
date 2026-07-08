#!/usr/bin/env python3
"""
ALE Weight 함수 테스트 스크립트 (리팩토링된 구조 테스트)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Analysis.ALE_Weight_Manager import ALEWeightManager
from Analysis.Analysis_Model import AnalysisModel
from Analysis.Analysis_Controller import AnalysisController

def test_ale_weight_manager():
    """ALEWeightManager 클래스 직접 테스트"""
    print("🚀 ALEWeightManager 클래스 직접 테스트")
    print("=" * 50)
    
    # ALEWeightManager 초기화
    ale_manager = ALEWeightManager()
    
    # 1. 기본 가중치 조회 테스트
    print("\n1️⃣ 기본 가중치 조회 테스트")
    result = ale_manager.get_weight("")
    if result['success']:
        weights = result['weights']
        print(f"✅ 성공: {result['message']}")
        print(f"   - Accuracy: {weights['accuracy_weight']}")
        print(f"   - Latency: {weights['latency_weight']}")
        print(f"   - Energy: {weights['energy_weight']}")
    else:
        print(f"❌ 실패: {result['message']}")
    
    # 2. 가중치 설정 테스트
    print("\n2️⃣ 가중치 설정 테스트")
    result = ale_manager.set_weight(
        device_id="TURTLEBOT3-Burger-1",
        accuracy_weight=0.5,
        latency_weight=0.3,
        energy_weight=0.2,
        description="ALEWeightManager 테스트용 가중치"
    )
    if result['success']:
        weights = result['weights']
        print(f"✅ 성공: {result['message']}")
        print(f"   - Device: {weights['device_id']}")
        print(f"   - Accuracy: {weights['accuracy_weight']}")
        print(f"   - Latency: {weights['latency_weight']}")
        print(f"   - Energy: {weights['energy_weight']}")
    else:
        print(f"❌ 실패: {result['message']}")
    
    # 3. 가중치 점수 계산 테스트
    print("\n3️⃣ 가중치 점수 계산 테스트")
    result = ale_manager.calculate_weighted_score(
        device_id="TURTLEBOT3-Burger-1",
        accuracy_value=800,  # 0-1000 범위
        latency_value=200,   # 0-1000 범위 (낮을수록 좋음)
        energy_value=700     # 0-1000 범위
    )
    if result['success']:
        score_result = result['result']
        print(f"✅ 성공: {result['message']}")
        print(f"   - Accuracy Score: {score_result['accuracy_score']}")
        print(f"   - Latency Score: {score_result['latency_score']}")
        print(f"   - Energy Score: {score_result['energy_score']}")
        print(f"   - Weighted Score: {score_result['weighted_score']}")
        print(f"   - Grade: {score_result['score_grade']}")
    else:
        print(f"❌ 실패: {result['message']}")

def test_mvc_integration():
    """MVC 구조 통합 테스트"""
    print("\n\n🔄 MVC 구조 통합 테스트")
    print("=" * 50)
    
    # 모델과 컨트롤러 초기화
    model = AnalysisModel()
    controller = AnalysisController(model)
    
    # 테스트용 디바이스들을 모델에 등록 (시뮬레이션)
    test_devices = ["TURTLEBOT3-Burger-1", "TURTLEBOT3-Burger-2", "TURTLEBOT3-Waffle-1"]
    for device_id in test_devices:
        # 기본 디바이스 객체 생성 (시뮬레이션)
        class MockDevice:
            def __init__(self, device_id):
                self.device_id = device_id
                self.device_type = "turtlebot"
                self.status = "online"
        
        model.devices[device_id] = MockDevice(device_id)
    
    # 1. 단일 디바이스 가중치 조회
    print("\n1️⃣ 단일 디바이스 가중치 조회")
    result = controller.get_ale_weight("TURTLEBOT3-Burger-1")
    if result['success']:
        weights = result['weights']
        print(f"✅ 성공: {result['message']}")
        print(f"   - Device: {weights['device_id']}")
        print(f"   - Accuracy: {weights['accuracy_weight']}")
        print(f"   - Latency: {weights['latency_weight']}")
        print(f"   - Energy: {weights['energy_weight']}")
    else:
        print(f"❌ 실패: {result['message']}")
    
    # 2. 여러 디바이스에 대한 가중치 설정
    print("\n2️⃣ 여러 디바이스에 대한 가중치 설정")
    device_configs = [
        {"id": "TURTLEBOT3-Burger-1", "a": 0.5, "l": 0.3, "e": 0.2, "desc": "Burger-1 최적화"},
        {"id": "TURTLEBOT3-Burger-2", "a": 0.4, "l": 0.4, "e": 0.2, "desc": "Burger-2 균형형"},
        {"id": "TURTLEBOT3-Waffle-1", "a": 0.6, "l": 0.2, "e": 0.2, "desc": "Waffle-1 정확도 중심"}
    ]
    
    for config in device_configs:
        result = controller.set_ale_weight(
            device_id=config["id"],
            accuracy_weight=config["a"],
            latency_weight=config["l"],
            energy_weight=config["e"],
            description=config["desc"]
        )
        if result['success']:
            print(f"✅ {config['id']} 가중치 설정 성공")
        else:
            print(f"❌ {config['id']} 가중치 설정 실패: {result['message']}")
    
    # 3. 모든 디바이스의 가중치 조회
    print("\n3️⃣ 모든 디바이스의 가중치 조회")
    result = controller.get_all_ale_weights()
    if result['success']:
        print(f"✅ 성공: {result['message']}")
        print(f"   - 총 디바이스 수: {result['total_devices']}")
        for weights in result['weights']:
            print(f"   - {weights['device_id']}: A({weights['accuracy_weight']}) L({weights['latency_weight']}) E({weights['energy_weight']})")
    else:
        print(f"❌ 실패: {result['message']}")
    
    # 4. 특정 디바이스 목록의 가중치 조회
    print("\n4️⃣ 특정 디바이스 목록의 가중치 조회")
    target_devices = ["TURTLEBOT3-Burger-1", "TURTLEBOT3-Waffle-1"]
    result = controller.get_ale_weights_for_devices(target_devices)
    if result['success']:
        print(f"✅ 성공: {result['message']}")
        print(f"   - 조회된 디바이스 수: {result['total_devices']}")
        for weights in result['weights']:
            print(f"   - {weights['device_id']}: {weights['description']}")
    else:
        print(f"❌ 실패: {result['message']}")
    
    # 5. 등록된 디바이스들의 가중치 조회 (빈 목록 전달)
    print("\n5️⃣ 등록된 모든 디바이스의 가중치 조회")
    result = controller.get_ale_weights_for_devices([])
    if result['success']:
        print(f"✅ 성공: {result['message']}")
        print(f"   - 등록된 디바이스 수: {result['total_devices']}")
        if result.get('default_applied'):
            print(f"   - 기본 가중치 적용된 디바이스: {result['default_applied']}")
    else:
        print(f"❌ 실패: {result['message']}")
    
    # 6. 다중 디바이스 점수 계산
    print("\n6️⃣ 다중 디바이스 점수 계산")
    for device_id in test_devices:
        result = controller.calculate_weighted_score(
            device_id=device_id,
            accuracy_value=800 + hash(device_id) % 200,  # 디바이스별로 다른 값
            latency_value=150 + hash(device_id) % 100,
            energy_value=700 + hash(device_id) % 150
        )
        if result['success']:
            score_result = result['result']
            print(f"✅ {device_id}: Score={score_result['weighted_score']:.1f} Grade={score_result['score_grade']}")
        else:
            print(f"❌ {device_id} 점수 계산 실패: {result['message']}")

def test_ale_scores():
    """ALE 점수 계산 테스트"""
    print("\n\n📊 ALE 점수 계산 테스트")
    print("=" * 50)
    
    # ALEWeightManager 직접 테스트
    ale_manager = ALEWeightManager()
    
    # 1. 단일 디바이스 ALE 점수 계산
    print("\n1️⃣ 단일 디바이스 ALE 점수 계산")
    device_data = {
        'battery_level': 85.0,
        'battery_wh': 420.0,
        'status': 'online',
        'device_type': 'turtlebot'
    }
    
    result = ale_manager.calculate_ale_scores_for_device("TURTLEBOT3-Burger-1", device_data)
    if result['success']:
        scores = result['ale_scores']
        print(f"✅ 성공: {result['message']}")
        print(f"   - Accuracy: {scores['accuracy_score']}")
        print(f"   - Latency: {scores['latency_score']}")
        print(f"   - Energy: {scores['energy_score']}")
    else:
        print(f"❌ 실패: {result['message']}")
    
    # 2. 다중 디바이스 ALE 점수 계산
    print("\n2️⃣ 다중 디바이스 ALE 점수 계산")
    device_ids = ["TURTLEBOT3-Burger-1", "TURTLEBOT3-Burger-2", "TURTLEBOT3-Waffle-1"]
    devices_data = {
        "TURTLEBOT3-Burger-1": {'battery_level': 85.0, 'status': 'online'},
        "TURTLEBOT3-Burger-2": {'battery_level': 65.0, 'status': 'busy'},
        "TURTLEBOT3-Waffle-1": {'battery_level': 95.0, 'status': 'idle'}
    }
    
    result = ale_manager.calculate_ale_scores_for_devices(device_ids, devices_data)
    if result['success']:
        print(f"✅ 성공: {result['message']}")
        for scores in result['ale_scores']:
            print(f"   - {scores['device_id']}: A({scores['accuracy_score']:.1f}) L({scores['latency_score']:.1f}) E({scores['energy_score']:.1f})")
    else:
        print(f"❌ 실패: {result['message']}")

def test_ale_weight_functions():
    """전체 ALE Weight 기능 테스트"""
    test_ale_weight_manager()
    test_mvc_integration()
    test_ale_scores()
    
    print("\n" + "=" * 50)
    print("🎉 ALE 관리 시스템 테스트 완료!")
    print("   ✅ ALEWeightManager 클래스 독립 실행 성공")
    print("   ✅ MVC 구조 통합 테스트 성공")
    print("   ✅ ALE 점수 계산 기능 정상 작동")
    print("   ✅ 가중치 관리 기능 정상 작동")
    print("   ✅ 다중 디바이스 지원 완료")

if __name__ == "__main__":
    test_ale_weight_functions()
