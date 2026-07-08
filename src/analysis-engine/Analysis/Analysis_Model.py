from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from influx_reader import InfluxReader
from .ALE_Weight_Manager import ALEWeightManager

class AnalysisModel:
    """
    분석 모델 - 비즈니스 로직과 데이터 처리를 담당
    """
    
    def __init__(self):
        self.devices = {}  # 디바이스 인스턴스들을 저장
        self.analysis_cache = {}  # 분석 결과 캐시
        self.influx_reader = None
        
        # ALE Weight Manager 초기화
        self.ale_weight_manager = ALEWeightManager()
        
        
    def register_device(self, device) -> bool:
        """디바이스 등록"""
        try:
            self.devices[device.device_id] = device
            logging.info(f"디바이스 {device.device_id} 등록 완료")
            return True
        except Exception as e:
            logging.error(f"디바이스 등록 실패: {e}")
            return False
    
    def get_device(self, device_id: str):
        """디바이스 조회"""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> Dict[str, Any]:
        """모든 디바이스 조회"""
        devices_list = []
        for device_id, device in self.devices.items():
            device_info = {
                'device_id': device_id,
                'device_type': device.device_type,
                'model': getattr(device, 'vehicle_type', 'unknown'),
                'location': device.location,
                'status': device.status,
                'last_updated': device.last_updated.isoformat() if device.last_updated else datetime.now().isoformat()
            }
            devices_list.append(device_info)
        
        return {
            'devices': devices_list,
            'total_count': len(devices_list)
        }
    
    def update_device_status_from_influx(self, device_id: str, lookback: str = "-30m") -> bool:
        """InfluxDB에서 디바이스 상태 업데이트"""
        try:
            device = self.get_device(device_id)
            if not device:
                return False
            
            # InfluxReader 인스턴스 생성
            if not self.influx_reader:
                self.influx_reader = InfluxReader()
            
            # InfluxDB에서 배터리 데이터 조회
            wh_value = self.influx_reader.latest_wh(device_id, lookback)
            
            if wh_value is not None:
                # 디바이스에 배터리 정보 업데이트
                device.battery_wh = wh_value
                device.fuel_level = min(100.0, wh_value / 10.0)  # Wh를 기반으로 배터리 레벨 계산
                device.status = "online"
                device.last_updated = datetime.now()
                
                logging.info(f"디바이스 {device_id} InfluxDB 업데이트 완료: {wh_value}Wh")
                return True
            else:
                logging.warning(f"디바이스 {device_id}의 InfluxDB 데이터를 찾을 수 없습니다")
                return False
                
        except Exception as e:
            logging.error(f"InfluxDB 업데이트 실패: {e}")
            return False
    
    def analyze_device_performance(self, device_id: str) -> Dict[str, Any]:
        """디바이스 성능 분석"""
        try:
            device = self.get_device(device_id)
            if not device:
                # 디바이스가 없으면 예시 데이터 반환
                logging.warning(f"디바이스 {device_id}를 찾을 수 없어 예시 데이터를 반환합니다")
                return self._get_example_device_analysis(device_id)
            
            # 캐시에서 분석 결과 확인
            cache_key = f"{device_id}_analysis"
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                # 캐시가 5분 이내라면 사용 (테스트를 위해 짧게)
                if (datetime.now() - cached_result['timestamp']).seconds < 300:
                    return cached_result['data']
            
            # 실제 분석 수행 또는 예시 데이터 생성
            analysis_result = self.get_sample_analysis_data(device_id)
            
            if analysis_result:
                # 결과 캐시에 저장
                self.analysis_cache[cache_key] = {
                    'data': analysis_result,
                    'timestamp': datetime.now()
                }
                return analysis_result
            else:
                return self._get_example_device_analysis(device_id)
            
        except Exception as e:
            logging.error(f"디바이스 성능 분석 실패: {e}")
            return self._get_example_device_analysis(device_id)
    
    def _get_example_device_analysis(self, device_id: str) -> Dict[str, Any]:
        """예시 분석 데이터 반환"""
        import random
        
        performance_score = round(random.uniform(70, 95), 1)
        efficiency_rating = round(random.uniform(65, 90), 1)
        battery_health = round(random.uniform(75, 98), 1)
        
        return {
            'device_id': device_id,
            'performance_score': performance_score,
            'efficiency_rating': efficiency_rating,
            'battery_health': battery_health,
            'summary': f"디바이스 {device_id}는 성능 점수 {performance_score}%로 양호한 상태입니다.",
            'metrics': [
                {'name': 'battery_efficiency', 'value': battery_health, 'unit': '%', 'description': '배터리 효율성'},
                {'name': 'operational_status', 'value': performance_score, 'unit': '%', 'description': '운영 상태'},
                {'name': 'energy_consumption', 'value': round(random.uniform(400, 500), 1), 'unit': 'Wh', 'description': '에너지 소비량'},
                {'name': 'system_health', 'value': efficiency_rating, 'unit': '%', 'description': '시스템 건강도'},
                {'name': 'network_latency', 'value': round(random.uniform(10, 50), 1), 'unit': 'ms', 'description': '네트워크 지연시간'},
                {'name': 'cpu_usage', 'value': round(random.uniform(20, 60), 1), 'unit': '%', 'description': 'CPU 사용률'}
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_fleet_analysis(self) -> Dict[str, Any]:
        """전체 디바이스 플릿 분석"""
        try:
            total_devices = len(self.devices)
            active_devices = 0
            total_performance = 0.0
            total_battery_health = 0.0
            device_analyses = []
            
            for device_id, device in self.devices.items():
                if device.status in ['online', 'active']:
                    active_devices += 1
                
                # 각 디바이스 분석
                device_analysis = self.analyze_device_performance(device_id)
                if device_analysis:
                    device_analyses.append(device_analysis)
                    total_performance += device_analysis['performance_score']
                    total_battery_health += device_analysis['battery_health']
            
            # 평균 계산
            avg_performance = total_performance / len(device_analyses) if device_analyses else 0.0
            avg_battery_health = total_battery_health / len(device_analyses) if device_analyses else 0.0
            
            return {
                'total_devices': total_devices,
                'active_devices': active_devices,
                'average_performance': avg_performance,
                'average_battery_health': avg_battery_health,
                'device_analyses': device_analyses,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"플릿 분석 실패: {e}")
            return None
    
    def _generate_analysis_summary(self, performance_score: float, efficiency_rating: float, battery_health: float) -> str:
        """분석 결과 요약 생성"""
        if performance_score >= 80 and battery_health >= 80:
            return "우수한 상태: 디바이스가 최적의 성능을 보이고 있습니다."
        elif performance_score >= 60 and battery_health >= 60:
            return "양호한 상태: 디바이스가 정상적으로 작동하고 있습니다."
        elif performance_score >= 40 and battery_health >= 40:
            return "주의 필요: 일부 성능 저하가 감지되었습니다."
        else:
            return "점검 필요: 디바이스에 문제가 있을 수 있습니다."
    
    def close_influx_connection(self):
        """InfluxDB 연결 종료"""
        if self.influx_reader:
            self.influx_reader.close()
    
    # ========================================================================================
    # MVC 리팩토링: Model은 순수한 데이터 CRUD 작업만 담당
    # ========================================================================================
    
    def device_exists(self, device_id: str) -> bool:
        """디바이스 존재 여부 확인"""
        return device_id in self.devices
    
    def create_sdi_device(self, device_id: str, device_class_info: dict, location: str = ""):
        """
        클래스 정보를 기반으로 적절한 SD* 디바이스 생성
        자동으로 SDV, SDA, SDI 중에서 선택하여 인스턴스 생성
        """
        try:
            class_type = device_class_info['class_type']
            device_type = device_class_info['device_type']
            model = device_class_info['model']
            sub_type = device_class_info['sub_type']
            
            device = None
            
            # 클래스 타입에 따라 동적으로 적절한 SD* 클래스 생성
            if class_type == 'SDV':
                device = self._create_sdv_device(device_id, device_type, sub_type, location)
            elif class_type == 'SDA':
                device = self._create_sda_device(device_id, device_type, sub_type, location)
            elif class_type == 'SDI':
                device = self._create_sdi_device_base(device_id, device_type, location)
            else:
                logging.warning(f"알 수 없는 클래스 타입 ({class_type}), 기본 SDI 사용")
                device = self._create_sdi_device_base(device_id, device_type, location)
            
            if not device:
                return None
            
            # 공통 속성 설정
            device.model = model
            device.status = "offline"  # 초기 상태
            device.last_updated = datetime.now()
            
            # 클래스별 특화 초기화
            self._initialize_device_by_class(device, class_type, device_class_info)
            
            # 디바이스 저장
            self.devices[device_id] = device
            logging.info(f"{device_id}: {class_type} 디바이스 생성 완료 (타입: {device_type}, 모델: {model})")
            
            return device
            
        except Exception as e:
            logging.error(f"SDI 디바이스 생성 실패 ({device_id}): {e}")
            return None
    
    def _create_sdv_device(self, device_id: str, device_type: str, sub_type: str, location: str):
        """SDV (Smart Device Vehicle) 생성"""
        try:
            from SDI_Devcie.SDV_Device import SDV_Device
            return SDV_Device(device_id, sub_type, location)
        except ImportError:
            logging.warning("SDV_Device import 실패, 기본 디바이스 사용")
            return self._create_basic_device(device_id, device_type, location)
    
    def _create_sda_device(self, device_id: str, device_type: str, sub_type: str, location: str):
        """SDA (Smart Device Air) 생성"""
        try:
            from SDI_Devcie.SDA_Device import SDA_Device
            return SDA_Device(device_id, sub_type, location)
        except ImportError:
            logging.warning("SDA_Device import 실패, 기본 디바이스 사용")
            return self._create_basic_device(device_id, device_type, location)
    
    def _create_sdi_device_base(self, device_id: str, device_type: str, location: str):
        """기본 SDI_Device 생성"""
        try:
            from SDI_Devcie.SDI_Device import SDI_Device
            return SDI_Device(device_id, device_type, location)
        except ImportError:
            logging.warning("SDI_Device import 실패, 기본 디바이스 사용")
            return self._create_basic_device(device_id, device_type, location)
    
    def _initialize_device_by_class(self, device, class_type: str, device_class_info: dict):
        """클래스별 특화 초기화"""
        if class_type == 'SDV':
            # SDV 전용 속성 초기화
            if hasattr(device, 'vehicle_type'):
                device.vehicle_type = device_class_info['model']
            if hasattr(device, 'fuel_level'):
                device.fuel_level = 0.0
            if hasattr(device, 'speed'):
                device.speed = 0.0
            if hasattr(device, 'battery_wh'):
                device.battery_wh = 0.0
                
        elif class_type == 'SDA':
            # SDA 전용 속성 초기화
            if hasattr(device, 'air_type'):
                device.air_type = device_class_info['model']
            if hasattr(device, 'altitude'):
                device.altitude = 0.0
            if hasattr(device, 'battery_level'):
                device.battery_level = 0.0
            if hasattr(device, 'flight_status'):
                device.flight_status = "grounded"
                
    def update_device_data_by_class(self, device_id: str, wh_value: float, class_type: str) -> bool:
        """
        클래스 타입에 맞게 디바이스 데이터 업데이트
        각 SD* 클래스의 특화된 속성들을 적절히 업데이트
        """
        try:
            if device_id not in self.devices:
                logging.error(f"디바이스 {device_id}가 존재하지 않습니다.")
                return False
            
            device = self.devices[device_id]
            
            if class_type == 'SDV':
                return self._update_sdv_device(device, wh_value)
            elif class_type == 'SDA':
                return self._update_sda_device(device, wh_value)
            else:
                return self._update_sdi_device_base(device, wh_value)
                
        except Exception as e:
            logging.error(f"클래스별 디바이스 업데이트 실패 ({device_id}): {e}")
            return False
    
    def _update_sdv_device(self, device, wh_value: float) -> bool:
        """SDV 디바이스 특화 업데이트"""
        try:
            # SDV 전용 배터리/연료 계산
            device.battery_wh = float(wh_value)
            device.fuel_level = min(100.0, (device.battery_wh / 500.0) * 100)  # Wh를 배터리 레벨로 변환
            device.speed = 0.3 if device.battery_wh > 350 else 0.1  # 배터리 상태에 따른 속도
            device.status = "online" if wh_value > 0 else "offline"
            device.last_updated = datetime.now()
            
            # 엔진 상태 업데이트 (있으면)
            if hasattr(device, 'engine_status'):
                device.engine_status = "on" if wh_value > 100 else "off"
            
            logging.debug(f"SDV 업데이트: 배터리={device.battery_wh:.1f}Wh, 레벨={device.fuel_level:.1f}%, 속도={device.speed}")
            return True
            
        except Exception as e:
            logging.error(f"SDV 디바이스 업데이트 실패: {e}")
            return False
    
    def _update_sda_device(self, device, wh_value: float) -> bool:
        """SDA 디바이스 특화 업데이트"""
        try:
            # SDA 전용 배터리/비행 계산
            device.battery_level = min(100.0, (float(wh_value) / 300.0) * 100)  # 드론용 배터리 계산
            device.status = "online" if wh_value > 0 else "offline"
            device.last_updated = datetime.now()
            
            # 비행 상태 업데이트
            if hasattr(device, 'flight_status'):
                if device.battery_level > 20:
                    device.flight_status = "ready" if device.status == "online" else "grounded"
                else:
                    device.flight_status = "low_battery"
            
            # 고도/속도 업데이트 (있으면)
            if hasattr(device, 'altitude'):
                device.altitude = 0.0  # 기본값, 실제 데이터로 대체 필요
            if hasattr(device, 'speed'):
                device.speed = 0.2 if device.battery_level > 30 else 0.0
            
            logging.debug(f"SDA 업데이트: 배터리={device.battery_level:.1f}%, 비행상태={getattr(device, 'flight_status', 'unknown')}")
            return True
            
        except Exception as e:
            logging.error(f"SDA 디바이스 업데이트 실패: {e}")
            return False
    
    def _update_sdi_device_base(self, device, wh_value: float) -> bool:
        """기본 SDI 디바이스 업데이트"""
        try:
            # 기본적인 상태만 업데이트
            device.status = "online" if wh_value > 0 else "offline"
            device.last_updated = datetime.now()
            
            # 배터리 정보가 있으면 업데이트
            if hasattr(device, 'battery_wh'):
                device.battery_wh = float(wh_value)
            
            logging.debug(f"SDI 기본 업데이트: 상태={device.status}")
            return True
            
        except Exception as e:
            logging.error(f"SDI 기본 디바이스 업데이트 실패: {e}")
            return False
    
    
    def update_device_battery_info(self, device_id: str, wh_value: float) -> bool:
        """디바이스 배터리 정보 업데이트 - 순수한 데이터 업데이트만 담당"""
        try:
            if device_id not in self.devices:
                logging.error(f"디바이스 {device_id}가 존재하지 않습니다.")
                return False
            
            device = self.devices[device_id]
            
            # 배터리 정보 업데이트
            device.battery_wh = float(wh_value)
            device.fuel_level = min(100.0, (device.battery_wh / 500.0) * 100)  # Wh를 배터리 레벨로 변환
            device.speed = 0.3 if device.battery_wh > 350 else 0.1  # 배터리 상태에 따른 속도
            device.status = "online" if wh_value > 0 else "offline"
            device.last_updated = datetime.now()
            
            logging.debug(f"{device_id}: 배터리 정보 업데이트 - {device.battery_wh:.1f}Wh, {device.fuel_level:.1f}%, {device.status}")
            return True
            
        except Exception as e:
            logging.error(f"배터리 정보 업데이트 실패 ({device_id}): {e}")
            return False


    # 새로운 분석 엔진 - MALE Mission, Accuracy, Latency, 종합 점수 계산
    
    def analyze_male_mission_data(self, device_id: str, mission_type: str, time_range: str) -> Dict[str, Any]:
        """
        MALE Mission 분석 - 미션 효과성, 성공률 계산
        """
        try:
            device = self.get_device(device_id)
            if not device:
                return None
            
            # 실제로는 InfluxDB나 별도 미션 데이터베이스에서 가져와야 함
            # 여기서는 디바이스 상태를 기반으로 시뮬레이션
            
            mission_records = self._generate_mission_records(device, mission_type, time_range)
            
            # 미션 성공률 계산
            total_missions = len(mission_records)
            successful_missions = len([r for r in mission_records if r['status'] == 'completed' and r['success_score'] >= 70])
            success_rate = (successful_missions / total_missions * 100) if total_missions > 0 else 0.0
            
            # 미션 효과성 계산 (성공 점수 평균)
            effectiveness = sum([r['success_score'] for r in mission_records]) / total_missions if total_missions > 0 else 0.0
            
            # 평균 미션 수행 시간
            avg_duration = sum([r['duration_minutes'] for r in mission_records]) / total_missions if total_missions > 0 else 0.0
            
            return {
                'success_rate': success_rate,
                'effectiveness': effectiveness,
                'avg_duration': avg_duration,
                'records': mission_records
            }
            
        except Exception as e:
            logging.error(f"MALE Mission 분석 실패 ({device_id}): {e}")
            return None
    
    def analyze_accuracy_data(self, device_id: str, accuracy_type: str, time_range: str) -> Dict[str, Any]:
        """
        Accuracy 분석 - 위치 정확도, 목표 도달 정확도 계산
        """
        try:
            device = self.get_device(device_id)
            if not device:
                return None
            
            # 실제로는 GPS 로그나 센서 데이터에서 가져와야 함
            # 여기서는 디바이스 성능을 기반으로 시뮬레이션
            
            accuracy_records = self._generate_accuracy_records(device, accuracy_type, time_range)
            
            # 정확도 퍼센트 계산
            total_records = len(accuracy_records)
            accurate_records = len([r for r in accuracy_records if r['error_distance'] <= 1.0])  # 1m 이하 오차
            accuracy_pct = (accurate_records / total_records * 100) if total_records > 0 else 0.0
            
            # 평균/최대 오차 거리 계산
            errors = [r['error_distance'] for r in accuracy_records]
            avg_error = sum(errors) / len(errors) if errors else 0.0
            max_error = max(errors) if errors else 0.0
            
            return {
                'accuracy_pct': accuracy_pct,
                'avg_error': avg_error,
                'max_error': max_error,
                'records': accuracy_records
            }
            
        except Exception as e:
            logging.error(f"Accuracy 분석 실패 ({device_id}): {e}")
            return None
    
    def analyze_latency_data(self, device_id: str, latency_type: str, time_range: str) -> Dict[str, Any]:
        """
        Latency 분석 - 명령 응답시간, 네트워크 지연 분석
        """
        try:
            device = self.get_device(device_id)
            if not device:
                return None
            
            # 실제로는 네트워크 로그나 명령 실행 로그에서 가져와야 함
            
            latency_records = self._generate_latency_records(device, latency_type, time_range)
            
            # 지연시간 통계 계산
            latencies = [r['latency_ms'] for r in latency_records]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
            max_latency = max(latencies) if latencies else 0.0
            min_latency = min(latencies) if latencies else 0.0
            
            return {
                'avg_latency': avg_latency,
                'max_latency': max_latency,
                'min_latency': min_latency,
                'records': latency_records
            }
            
        except Exception as e:
            logging.error(f"Latency 분석 실패 ({device_id}): {e}")
            return None
    
    def calculate_device_score(self, device_id: str, time_range: str) -> Dict[str, Any]:
        """
        디바이스 종합 점수 계산 - A+, A, B+ 등급 시스템
        """
        try:
            device = self.get_device(device_id)
            if not device:
                return None
            
            # 각 카테고리별 점수 계산
            scores = {}
            
            # 1. Performance Score (성능 점수)
            scores['performance_score'] = self._calculate_performance_score(device)
            
            # 2. Mission Score (미션 점수)
            mission_data = self.analyze_male_mission_data(device_id, "patrol", time_range)
            if mission_data:
                scores['mission_score'] = (mission_data['success_rate'] + mission_data['effectiveness']) / 2
            else:
                scores['mission_score'] = 50.0  # 기본값
            
            # 3. Accuracy Score (정확도 점수)
            accuracy_data = self.analyze_accuracy_data(device_id, "positioning", time_range)
            if accuracy_data:
                scores['accuracy_score'] = accuracy_data['accuracy_pct']
            else:
                scores['accuracy_score'] = 50.0  # 기본값
            
            # 4. Latency Score (지연시간 점수) - 낮을수록 높은 점수
            latency_data = self.analyze_latency_data(device_id, "command", time_range)
            if latency_data and latency_data['avg_latency'] > 0:
                # 100ms 이하면 100점, 1000ms 이상이면 0점으로 변환
                scores['latency_score'] = max(0, min(100, 100 - (latency_data['avg_latency'] - 100) / 10))
            else:
                scores['latency_score'] = 50.0  # 기본값
            
            # 5. Reliability Score (신뢰성 점수)
            scores['reliability_score'] = self._calculate_reliability_score(device)
            
            # 종합 점수 계산 (가중 평균)
            weights = {
                'performance_score': 0.25,
                'mission_score': 0.30,
                'accuracy_score': 0.20,
                'latency_score': 0.15,
                'reliability_score': 0.10
            }
            
            overall_score = sum(scores[key] * weights[key] for key in weights.keys())
            
            # 등급 계산
            grade = self._calculate_grade(overall_score)
            
            # 상세 분석 및 개선 제안
            score_details = self._generate_score_details(scores, device)
            
            return {
                'overall_score': round(overall_score, 1),
                'performance_score': round(scores['performance_score'], 1),
                'mission_score': round(scores['mission_score'], 1),
                'accuracy_score': round(scores['accuracy_score'], 1),
                'latency_score': round(scores['latency_score'], 1),
                'reliability_score': round(scores['reliability_score'], 1),
                'grade': grade,
                'details': score_details
            }
            
        except Exception as e:
            logging.error(f"디바이스 종합 점수 계산 실패 ({device_id}): {e}")
            return None
    
    def _generate_mission_records(self, device, mission_type: str, time_range: str) -> list:
        """미션  시뮬레이션 생성"""
        import random
        from datetime import datetime, timedelta
        
        records = []
        # 배터리 상태에 따라 미션 성과 결정
        battery_factor = getattr(device, 'fuel_level', getattr(device, 'battery_level', 50)) / 100.0
        
        for i in range(10):  # 최근 10개 미션
            duration = random.uniform(15, 120)  # 15-120분
            success_score = max(30, min(100, 60 + battery_factor * 30 + random.uniform(-15, 15)))
            
            records.append({
                'mission_id': f"mission_{device.device_id}_{i+1}",
                'status': 'completed' if success_score >= 50 else 'failed',
                'duration_minutes': round(duration, 1),
                'success_score': round(success_score, 1),
                'start_time': (datetime.now() - timedelta(hours=i*2)).isoformat(),
                'end_time': (datetime.now() - timedelta(hours=i*2) + timedelta(minutes=duration)).isoformat()
            })
        
        return records
    
    def _generate_accuracy_records(self, device, accuracy_type: str, time_range: str) -> list:
        """정확도 기록 시뮬레이션 생성"""
        import random
        
        records = []
        # 디바이스 클래스별 기본 정확도 설정
        device_class = type(device).__name__
        if device_class == "SDV_Device":
            base_accuracy = 0.8  # 터틀봇은 상대적으로 정확
        elif device_class == "SDA_Device":
            base_accuracy = 0.6  # 드론은 바람 등의 영향
        else:
            base_accuracy = 0.7
        
        for i in range(20):  # 20개 측정점
            target_x, target_y = random.uniform(-10, 10), random.uniform(-10, 10)
            
            error_distance = random.uniform(0, 3) * (1 - base_accuracy)
            angle = random.uniform(0, 2 * 3.14159)
            
            actual_x = target_x + error_distance * random.cos(angle)  
            actual_y = target_y + error_distance * random.sin(angle)
            
            records.append({
                'record_id': f"acc_{device.device_id}_{i+1}",
                'target_x': round(target_x, 2),
                'target_y': round(target_y, 2),
                'actual_x': round(actual_x, 2),
                'actual_y': round(actual_y, 2),
                'error_distance': round(error_distance, 2),
                'timestamp': datetime.now().isoformat()
            })
        
        return records
    
    def _generate_latency_records(self, device, latency_type: str, time_range: str) -> list:
        """지연시간 기록 시뮬레이션 생성"""
        import random
        
        records = []
        # 디바이스 상태에 따른 기본 지연시간
        battery_level = getattr(device, 'fuel_level', getattr(device, 'battery_level', 50))
        base_latency = 50 + (100 - battery_level) * 2  # 배터리 낮으면 지연시간 증가
        
        commands = ["move", "rotate", "stop", "status_check", "sensor_read"]
        
        for i in range(15):
            latency = max(10, base_latency + random.uniform(-20, 30))
            
            records.append({
                'record_id': f"lat_{device.device_id}_{i+1}",
                'latency_ms': round(latency, 1),
                'command_type': random.choice(commands),
                'timestamp': datetime.now().isoformat()
            })
        
        return records
    
    def _calculate_performance_score(self, device) -> float:
        """성능 점수 계산"""
        # 배터리 레벨, 속도, 상태 등을 종합적으로 고려
        battery_level = getattr(device, 'fuel_level', getattr(device, 'battery_level', 50))
        speed = getattr(device, 'speed', 0.0)
        
        # 배터리 점수 (60%)
        battery_score = battery_level
        
        # 속도/응답성 점수 (30%)
        speed_score = min(100, speed * 100) if speed > 0 else 50
        
        # 상태 점수 (10%)
        status_score = 100 if device.status == "online" else 20
        
        return battery_score * 0.6 + speed_score * 0.3 + status_score * 0.1
    
    def _calculate_reliability_score(self, device) -> float:
        """신뢰성 점수 계산"""
        # 업타임, 에러율 등을 고려 (현재는 간단히 시뮬레이션)
        import random
        
        # 디바이스 클래스별 기본 신뢰성
        device_class = type(device).__name__
        if device_class == "SDV_Device":
            base_reliability = 85.0
        elif device_class == "SDA_Device":
            base_reliability = 75.0  # 드론은 상대적으로 복잡
        else:
            base_reliability = 80.0
        
        # 배터리 상태가 신뢰성에 영향
        battery_level = getattr(device, 'fuel_level', getattr(device, 'battery_level', 50))
        battery_factor = battery_level / 100.0
        
        return min(100, base_reliability * (0.7 + 0.3 * battery_factor) + random.uniform(-5, 5))
    
    def _calculate_grade(self, overall_score: float) -> str:
        """점수를 등급으로 변환"""
        if overall_score >= 95:
            return "A+"
        elif overall_score >= 90:
            return "A"
        elif overall_score >= 85:
            return "B+"
        elif overall_score >= 80:
            return "B"
        elif overall_score >= 75:
            return "C+"
        elif overall_score >= 70:
            return "C"
        elif overall_score >= 60:
            return "D"
        else:
            return "F"
    

    # 점수 별 피드백 같은 로그를 남기기 위해서 작성 -기철
    def _generate_score_details(self, scores: dict, device) -> list:
     
        details = []
        
        for category, score in scores.items():
            recommendations = []
            
            if category == 'performance_score':
                if score < 70:
                    recommendations.extend([
                        "배터리 충전 필요",
                        "시스템 최적화 검토",
                        "하드웨어 점검 권장"
                    ])
                description = f"전반적인 디바이스 성능: {score:.1f}/100"
                
            elif category == 'mission_score':
                if score < 70:
                    recommendations.extend([
                        "미션 계획 재검토",
                        "경로 최적화 필요",
                        "운영 프로토콜 개선"
                    ])
                description = f"미션 수행 효율성: {score:.1f}/100"
                
            elif category == 'accuracy_score':
                if score < 70:
                    recommendations.extend([
                        "센서 캘리브레이션",
                        "GPS 신호 개선",
                        "환경적 간섭 요소 제거"
                    ])
                description = f"위치 정확도 성능: {score:.1f}/100"
                
            elif category == 'latency_score':
                if score < 70:
                    recommendations.extend([
                        "네트워크 연결 점검",
                        "통신 프로토콜 최적화",
                        "처리 용량 증설 검토"
                    ])
                description = f"응답 속도 성능: {score:.1f}/100"
                
            elif category == 'reliability_score':
                if score < 70:
                    recommendations.extend([
                        "정기 유지보수 강화",
                        "예비 부품 점검",
                        "운영 환경 개선"
                    ])
                description = f"시스템 안정성: {score:.1f}/100"
            
            details.append({
                'category': category.replace('_score', ''),
                'score': round(score, 1),
                'description': description,
                'recommendations': recommendations
            })
        
        return details
    

    
    # ALE Weight 관련 메서드들 - ALEWeightManager 클래스 위임
    def get_ale_weight(self, device_id: str = "") -> Dict[str, Any]:
        """ALE 가중치 조회 (ALEWeightManager 위임)"""
        return self.ale_weight_manager.get_weight(device_id)
    
    def set_ale_weight(self, device_id: str, accuracy_weight: float, latency_weight: float, 
                       energy_weight: float, description: str = "") -> Dict[str, Any]:
        """ALE 가중치 설정 (ALEWeightManager 위임)"""
        return self.ale_weight_manager.set_weight(device_id, accuracy_weight, latency_weight, energy_weight, description)
    
    def calculate_weighted_score(self, device_id: str, accuracy_value: float, latency_value: float, 
                               energy_value: float, time_range: str = "-24h") -> Dict[str, Any]:
        """가중치 적용 점수 계산 (ALEWeightManager 위임)"""
        return self.ale_weight_manager.calculate_weighted_score(device_id, accuracy_value, latency_value, energy_value)