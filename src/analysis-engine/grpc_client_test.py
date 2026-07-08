#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KETI Analysis Engine gRPC Client Test
gRPC 서버 테스트용 클라이언트
"""

import grpc
import analysis_service_pb2 as pb2
import analysis_service_pb2_grpc as pb2_grpc
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisClient:
    def __init__(self, host='localhost', port=50051):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
    
    def connect(self):
        """gRPC 서버에 연결"""
        try:
            self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            self.stub = pb2_grpc.AnalysisServiceStub(self.channel)
            logger.info(f"gRPC 서버에 연결: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"연결 실패: {e}")
            return False
    
    def test_create_turtlebot(self, device_id="test-bot-01", model="TURTLEBOT3-Burger", location="Lab-A"):
        """터틀봇 생성 테스트"""
        try:
            request = pb2.CreateTurtlebotRequest(
                device_id=device_id,
                model=model,
                location=location
            )
            
            response = self.stub.CreateTurtlebot(request)
            logger.info(f"터틀봇 생성 결과: {response.success}, {response.message}")
            
            if response.success and response.device_info:
                logger.info(f"디바이스 정보: ID={response.device_info.device_id}, "
                          f"타입={response.device_info.device_type}, "
                          f"모델={response.device_info.model}")
            
            return response.success
        except Exception as e:
            logger.error(f"터틀봇 생성 실패: {e}")
            return False
    
    def test_get_device_status(self, device_id="test-bot-01"):
        """디바이스 상태 조회 테스트"""
        try:
            request = pb2.GetDeviceStatusRequest(device_id=device_id)
            response = self.stub.GetDeviceStatus(request)
            
            logger.info(f"디바이스 상태 조회 결과: {response.success}, {response.message}")
            
            if response.success and response.status:
                logger.info(f"상태: {response.status.status}, "
                          f"배터리 레벨: {response.status.battery_level}%, "
                          f"배터리 Wh: {response.status.battery_wh}")
            
            return response.success
        except Exception as e:
            logger.error(f"상태 조회 실패: {e}")
            return False
    
    def test_update_from_influx(self, device_id="TURTLEBOT3-Burger-1"):
        """InfluxDB 업데이트 테스트"""
        try:
            request = pb2.UpdateFromInfluxRequest(
                device_id=device_id,
                lookback="-30m"
            )
            
            response = self.stub.UpdateFromInflux(request)
            logger.info(f"InfluxDB 업데이트 결과: {response.success}, {response.message}")
            
            if response.success and response.updated_status:
                logger.info(f"업데이트된 상태: {response.updated_status.status}, "
                          f"배터리 Wh: {response.updated_status.battery_wh}")
            
            return response.success
        except Exception as e:
            logger.error(f"InfluxDB 업데이트 실패: {e}")
            return False
    
    def test_analyze_device(self, device_id="test-bot-01"):
        """디바이스 분석 테스트"""
        try:
            request = pb2.AnalyzeDeviceRequest(device_id=device_id)
            response = self.stub.AnalyzeDevice(request)
            
            logger.info(f"디바이스 분석 결과: {response.success}, {response.message}")
            
            if response.success and response.analysis:
                analysis = response.analysis
                logger.info(f"성능 점수: {analysis.performance_score}")
                logger.info(f"효율성 등급: {analysis.efficiency_rating}")
                logger.info(f"배터리 건강도: {analysis.battery_health}")
                logger.info(f"분석 요약: {analysis.analysis_summary}")
                
                if analysis.metrics:
                    logger.info("세부 메트릭:")
                    for metric in analysis.metrics:
                        logger.info(f"  - {metric.metric_name}: {metric.value} {metric.unit}")
            
            return response.success
        except Exception as e:
            logger.error(f"디바이스 분석 실패: {e}")
            return False
    
    def test_get_all_devices(self):
        """모든 디바이스 조회 테스트"""
        try:
            request = pb2.GetAllDevicesRequest()
            response = self.stub.GetAllDevices(request)
            
            logger.info(f"디바이스 목록 조회 결과: {response.success}, {response.message}")
            
            if response.success and response.devices:
                logger.info(f"총 {len(response.devices)}개의 디바이스:")
                for device in response.devices:
                    logger.info(f"  - {device.device_id} ({device.device_type}): {device.status}")
            
            return response.success
        except Exception as e:
            logger.error(f"디바이스 목록 조회 실패: {e}")
            return False
    
    def test_get_fleet_analysis(self):
        """플릿 분석 테스트"""
        try:
            request = pb2.GetFleetAnalysisRequest()
            response = self.stub.GetFleetAnalysis(request)
            
            logger.info(f"플릿 분석 결과: {response.success}, {response.message}")
            
            if response.success and response.fleet_analysis:
                fleet = response.fleet_analysis
                logger.info(f"총 디바이스: {fleet.total_devices}")
                logger.info(f"활성 디바이스: {fleet.active_devices}")
                logger.info(f"평균 성능: {fleet.average_performance}")
                logger.info(f"평균 배터리 건강도: {fleet.average_battery_health}")
            
            return response.success
        except Exception as e:
            logger.error(f"플릿 분석 실패: {e}")
            return False
    
    def test_male_mission_analysis(self, device_id="TURTLEBOT3-Burger-1"):
        """MALE Mission 분석 테스트"""
        try:
            request = pb2.AnalyzeMaleMissionRequest(
                device_id=device_id,
                mission_type="patrol",
                time_range="-24h"
            )
            
            response = self.stub.AnalyzeMaleMission(request)
            logger.info(f"🎯 MALE Mission 분석 결과: {response.success}, {response.message}")
            
            if response.success and response.analysis:
                analysis = response.analysis
                logger.info(f"미션 성공률: {analysis.mission_success_rate:.1f}%")
                logger.info(f"미션 효과성: {analysis.mission_effectiveness:.1f}%")
                logger.info(f"평균 수행시간: {analysis.average_mission_duration:.1f}분")
                logger.info(f"총 미션 수: {len(analysis.mission_records)}")
            
            return response.success
        except Exception as e:
            logger.error(f"MALE Mission 분석 실패: {e}")
            return False
    
    def test_accuracy_analysis(self, device_id="TURTLEBOT3-Burger-1"):
        """정확도 분석 테스트"""
        try:
            request = pb2.AnalyzeAccuracyRequest(
                device_id=device_id,
                accuracy_type="positioning",
                time_range="-24h"
            )
            
            response = self.stub.AnalyzeAccuracy(request)
            logger.info(f"📍 정확도 분석 결과: {response.success}, {response.message}")
            
            if response.success and response.analysis:
                analysis = response.analysis
                logger.info(f"정확도: {analysis.accuracy_percentage:.1f}%")
                logger.info(f"평균 오차: {analysis.average_error_distance:.2f}m")
                logger.info(f"최대 오차: {analysis.max_error_distance:.2f}m")
                logger.info(f"측정 수: {len(analysis.accuracy_records)}")
            
            return response.success
        except Exception as e:
            logger.error(f"정확도 분석 실패: {e}")
            return False
    
    def test_latency_analysis(self, device_id="TURTLEBOT3-Burger-1"):
        """지연시간 분석 테스트"""
        try:
            request = pb2.AnalyzeLatencyRequest(
                device_id=device_id,
                latency_type="command",
                time_range="-24h"
            )
            
            response = self.stub.AnalyzeLatency(request)
            logger.info(f"⚡ 지연시간 분석 결과: {response.success}, {response.message}")
            
            if response.success and response.analysis:
                analysis = response.analysis
                logger.info(f"평균 지연시간: {analysis.average_latency_ms:.1f}ms")
                logger.info(f"최대 지연시간: {analysis.max_latency_ms:.1f}ms")
                logger.info(f"최소 지연시간: {analysis.min_latency_ms:.1f}ms")
                logger.info(f"측정 수: {len(analysis.latency_records)}")
            
            return response.success
        except Exception as e:
            logger.error(f"지연시간 분석 실패: {e}")
            return False
    
    def test_device_score(self, device_id="TURTLEBOT3-Burger-1"):
        """디바이스 종합 점수 테스트"""
        try:
            request = pb2.GetDeviceScoreRequest(
                device_id=device_id,
                time_range="-24h"
            )
            
            response = self.stub.GetDeviceScore(request)
            logger.info(f"🏆 종합 점수 결과: {response.success}, {response.message}")
            
            if response.success and response.score:
                score = response.score
                logger.info(f"📊 종합 점수: {score.overall_score:.1f}/100 (등급: {score.grade})")
                logger.info(f"   성능: {score.performance_score:.1f}, 미션: {score.mission_score:.1f}")
                logger.info(f"   정확도: {score.accuracy_score:.1f}, 지연시간: {score.latency_score:.1f}")
                logger.info(f"   신뢰성: {score.reliability_score:.1f}")
                
                if score.score_details:
                    logger.info("📋 상세 분석:")
                    for detail in score.score_details[:3]:  # 처음 3개만 출력
                        logger.info(f"   • {detail.category}: {detail.score:.1f}")
                        if detail.recommendations:
                            logger.info(f"     💡 개선안: {detail.recommendations[0]}")
            
            return response.success
        except Exception as e:
            logger.error(f"종합 점수 실패: {e}")
            return False
    
    def test_battery_status(self, device_id="TURTLEBOT3-Burger-1"):
        """배터리 상태 테스트"""
        try:
            request = pb2.GetBatteryStatusRequest(device_id=device_id)
            response = self.stub.GetBatteryStatus(request)
            
            logger.info(f"🔋 배터리 상태 결과: {response.success}, {response.message}")
            
            if response.success and response.battery_status:
                battery = response.battery_status
                logger.info(f"배터리 레벨: {battery.battery_level:.1f}%")
                logger.info(f"배터리 Wh: {battery.battery_wh:.1f}Wh")
                logger.info(f"예상 런타임: {battery.estimated_runtime:.1f}h")
                logger.info(f"건강 상태: {battery.health_status}")
            
            return response.success
        except Exception as e:
            logger.error(f"배터리 상태 실패: {e}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("=== KETI Analysis Engine gRPC Client 테스트 시작 ===")
        
        if not self.connect():
            logger.error("서버 연결 실패. 테스트를 중단합니다.")
            return
        
        # 테스트 시나리오
        tests = [
            ("터틀봇 생성", lambda: self.test_create_turtlebot()),
            ("디바이스 상태 조회", lambda: self.test_get_device_status()),
            ("실제 터틀봇 InfluxDB 업데이트", lambda: self.test_update_from_influx()),
            ("🎯 MALE Mission 분석", lambda: self.test_male_mission_analysis()),
            ("📍 정확도 분석", lambda: self.test_accuracy_analysis()),
            ("⚡ 지연시간 분석", lambda: self.test_latency_analysis()),
            ("🏆 디바이스 종합 점수", lambda: self.test_device_score()),
            ("🔋 배터리 상태", lambda: self.test_battery_status()),
            ("디바이스 분석", lambda: self.test_analyze_device()),
            ("모든 디바이스 조회", lambda: self.test_get_all_devices()),
            ("플릿 분석", lambda: self.test_get_fleet_analysis()),
        ]
        
        success_count = 0
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} 테스트 ---")
            try:
                if test_func():
                    success_count += 1
                    logger.info(f"✅ {test_name} 성공")
                else:
                    logger.warning(f"❌ {test_name} 실패")
            except Exception as e:
                logger.error(f"❌ {test_name} 오류: {e}")
            
            time.sleep(1)  # 테스트 간 간격
        
        logger.info(f"\n=== 테스트 완료: {success_count}/{len(tests)} 성공 ===")
    
    def close(self):
        """연결 종료"""
        if self.channel:
            self.channel.close()
            logger.info("연결 종료")

def main():
    client = AnalysisClient()
    try:
        client.run_all_tests()
    finally:
        client.close()

if __name__ == "__main__":
    main()