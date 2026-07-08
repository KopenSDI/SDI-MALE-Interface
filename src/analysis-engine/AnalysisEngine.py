import threading
import time
import os
import logging
from typing import Optional
import argparse
from influx_reader import InfluxReader, BOTS

from Analysis.Analysis_Model import AnalysisModel
from Analysis.Analysis_Controller import AnalysisController
from Analysis.Analysis_View import AnalysisView

default_bot = os.getenv("BOT")  # 환경변수 BOT이 있으면 기본값으로 사용

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s") # 로그용 -> DEBUG는 안보이는 로그여서  DEBUG할려면 코드 수정하셔야해요요


# Singleton 패턴으로 KETI_AnalysisEngine 클래스 정의
class KETI_AnalysisEngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    # value는 Thread 로할까 고민중 아직 get_EngineName 
    def __init__(self, value=None):
        if not hasattr(self, 'initialized'):
            self.engine_Name = value
            self.initialized = True
            self._running = False
            
            # MVC 컴포넌트 직접 생성 - 필수 컴포넌트!
            print("🔧 MVC 컴포넌트 초기화 중...")
            self.model = AnalysisModel()
            self.controller = AnalysisController(self.model)
            self.view = AnalysisView(self.controller)
            print("✅ MVC 컴포넌트 생성 완료!")

    def get_EngineName(self):
        return self.engine_Name
    
    def test_update_from_influx(self):
        print(f"{self.engine_Name} InfluxDB 데이터 조회 및 디바이스 업데이트 중!!!")
        print(f"controllerrrrr{self.controller}")
        reader = InfluxReader()
        try:
            bots = BOTS
            results = []
            for bot in bots:
                val = reader.latest_wh(bot, lookback="-30m")
                results.append({"bot": bot, "wh": val})
            print("InfluxDB 조회 결과:", results)
            
            # Controller를 통해 디바이스 업데이트 
            result = self.controller.update_devices_from_influx(results)
            if result['success']:
                print(f"✅ 디바이스 처리 완료: {result['message']}")
                print(f"   업데이트: {result['updated_devices']}")
                print(f"   생성: {result['created_devices']}")
                if result['failed_devices']:
                    print(f"   실패: {result['failed_devices']}")
            else:
                print(f"❌ 디바이스 처리 실패: {result['message']}")
                
        finally:
            reader.close()
        print(f"{self.engine_Name} 데이터 업데이트 완료")
    
    
    def compare_etcd_vs_k8s(self, namespace="default"):
        """etcd와 Kubernetes API 비교"""
        try:
            compare_result = self.controller.compare_etcd_vs_k8s_api(namespace)
            if compare_result['success']:
                comparison = compare_result['comparison']
                print(f"🔍 etcd vs K8s API 비교 ({namespace}):")
                print(f"   etcd Pod 수: {comparison.get('etcd_count', 0)}")
                print(f"   K8s API Pod 수: {comparison.get('api_count', 0)}")
                print(f"   동기화 상태: {'✅ 일치' if comparison.get('sync_status') == 'SYNCED' else '⚠️ 불일치'}")
                
                if comparison.get('sync_status') != 'SYNCED':
                    if comparison.get('etcd_only'):
                        print(f"   etcd에만 있음: {comparison['etcd_only']}")
                    if comparison.get('api_only'):
                        print(f"   K8s API에만 있음: {comparison['api_only']}")
                        
            else:
                print(f"❌ etcd vs K8s 비교 실패: {compare_result.get('message', 'unknown')}")
        except Exception as e:
            print(f"❌ etcd vs K8s 비교 중 오류: {e}")
    


    def show_startup_banner(self):
        """시작 배너 및 상태 표시"""
        print(f"\n{'='*70}")
        print(f"🚀 {self.engine_Name} 실시간 모니터링 시스템")
        print(f"{'='*70}")
        print(f"📊 기능:")
        print(f"   • 디바이스 상태 관리")
        print(f"   • MALE 메트릭 분석")
        print(f"{'='*70}")
        print(f"{'='*70}\n")
    
    def show_monitoring_summary(self, loop_count):
        """주기적 모니터링 요약 표시"""
        print(f"\n{'='*50}")
        print(f"📊 모니터링 요약 (루프 #{loop_count})")
        print(f"{'='*50}")
        
        # 전체 Pod 요약
        try:
            summary_result = self.controller.get_pod_summary()
            if summary_result['success']:
                summary = summary_result['summary']
                print(f"🔍 Pod 현황:")
                print(f"   총 Pod: {summary.get('total_pods', 0)}")
                print(f"   실행 중: {summary.get('running_pods', 0)}")
                print(f"   분석 완료: {summary.get('analyzed_pods', 0)}")
                print(f"   평균 MALE 점수: {summary.get('average_male_score', 0):.1f}")
        except Exception as e:
            print(f"❌ Pod 요약 조회 실패: {e}")
        
       
        
        print(f"{'='*50}")
    
    def run(self):
        self._running = True
        
        # 시작 배너 표시
        self.show_startup_banner()
        
        loop_count = 0
        etcd_detail_interval = 3  # 3번의 루프마다 상세 etcd 분석
        summary_interval = 6     # 6번의 루프마다 요약 표시
        
        while self._running:
            current_time = time.strftime("%H:%M:%S")
            print(f"\n⏰ [{current_time}] {self.engine_Name} 모니터링 루프 #{loop_count + 1}")
            
            print(f"📈 InfluxDB 데이터 업데이트...")# test인 이유는 현재 인플럭스디비에서 호출을 2개정적으로 함. 키값전체를 넣는코드가 필요함함
            self.test_update_from_influx()
            
            # GRPC 동작전에 로컬테스트용코드 ... 
            print(f"🔍 ALE 점수 조회 테스트...")
            self.test_get_ale_weight()
            
            # 주기적 요약 표시 (60초마다 - 6번의 루프마다)
            if loop_count % summary_interval == 0 and loop_count > 0:
                self.show_monitoring_summary(loop_count + 1)
            
            loop_count += 1
            time.sleep(60)  # 10초마다 모니터링 

    
    def test_get_ale_weight(self):
        """GetALEWeight 함수 로컬 호출 테스트"""
        try:
            # Analysis_View의 GetALEWeight 메서드를 직접 호출 (gRPC 없이)
            # request와 context는 None으로 전달 (실제로는 사용하지 않음)
            result = self.view.GetALEWeight(None, None)
            
            if isinstance(result, dict) and result.get('success', False):
                ale_scores = result.get('ale_scores', {})
                total_devices = result.get('total_devices', 0)
                
                print(f"   ✅ ALE 점수 조회 성공: {total_devices}개 디바이스")
                
                # 각 디바이스의 ALE 점수 출력
                for device_id, scores in ale_scores.items():
                    accuracy = scores.get('accuracy_score', 0.0)
                    latency = scores.get('latency_score', 0.0)
                    energy = scores.get('energy_score', 0.0)
                    print(f"      📱 {device_id}: A({accuracy:.1f}) L({latency:.1f}) E({energy:.1f})")
            else:
                message = result.get('message', '알 수 없는 오류') if isinstance(result, dict) else str(result)
                print(f"   ⚠️ ALE 점수 조회 실패: {message}")
                
        except Exception as e:
            print(f"   ❌ ALE 점수 조회 중 오류: {e}")
    
    def test_run(self):
        print(f"🧪 {self.engine_Name} 테스트 모드")
        
        # 1. 기본 InfluxDB 테스트
        print(f"\n1. InfluxDB 연결 테스트")
        self.test_update_from_influx()
    
        print(f"\n✅ 테스트 완료")
    
    def stop(self):
        self._running = False
        # etcd 분석기 리소스 정리
        if hasattr(self.controller, 'close_etcd_analyzer'):
            self.controller.close_etcd_analyzer()