from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

class SDI_Device(ABC):
    """
    SDI (Smart Device Interface) 기본 클래스
    모든 스마트 디바이스의 기본 인터페이스를 정의
    """
    
    def __init__(self, device_id: str, device_type: str, location: str = ""):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.status = "offline"
        self.last_updated = datetime.now()
        self.metadata = {}
        
    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """디바이스 정보 반환 - 하위 클래스에서 구현"""
        pass
    
    @abstractmethod
    def get_status_data(self) -> Dict[str, Any]:
        """디바이스 상태 데이터 반환 - 하위 클래스에서 구현"""
        pass
    
    @abstractmethod
    def update_status(self, status_data: Dict[str, Any]) -> bool:
        """디바이스 상태 업데이트 - 하위 클래스에서 구현"""
        pass
    
    def get_basic_info(self) -> Dict[str, Any]:
        """기본 디바이스 정보 반환"""
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'location': self.location,
            'status': self.status,
            'last_updated': self.last_updated.isoformat()
        }
    
    def set_location(self, location: str) -> None:
        """디바이스 위치 설정"""
        self.location = location
        self.last_updated = datetime.now()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """메타데이터 설정"""
        self.metadata[key] = value
        self.last_updated = datetime.now()
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """메타데이터 조회"""
        return self.metadata.get(key)


class SDR_Device(SDI_Device):
    """
    SDR (Smart Device Robot) - 로봇 디바이스 클래스
    터틀봇 등 로봇 관련 디바이스
    """
    
    def __init__(self, device_id: str, robot_type: str, location: str = ""):
        super().__init__(device_id, "robot", location)
        self.robot_type = robot_type
        self.battery_level = 0.0
        self.battery_wh = 0.0
        self.motor_status = "stopped"
        self.sensor_data = {}
        self.task_status = "idle"
        
    def get_device_info(self) -> Dict[str, Any]:
        """로봇 디바이스 정보 반환"""
        info = self.get_basic_info()
        info.update({
            'robot_type': self.robot_type,
            'battery_level': self.battery_level,
            'battery_wh': self.battery_wh,
            'motor_status': self.motor_status,
            'task_status': self.task_status,
            'sensor_count': len(self.sensor_data)
        })
        return info
    
    def get_status_data(self) -> Dict[str, Any]:
        """로봇 상태 데이터 반환"""
        return {
            'device_id': self.device_id,
            'battery_level': self.battery_level,
            'battery_wh': self.battery_wh,
            'motor_status': self.motor_status,
            'task_status': self.task_status,
            'sensor_data': self.sensor_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_status(self, status_data: Dict[str, Any]) -> bool:
        """로봇 상태 업데이트"""
        try:
            if 'battery_level' in status_data:
                self.battery_level = float(status_data['battery_level'])
            if 'battery_wh' in status_data:
                self.battery_wh = float(status_data['battery_wh'])
            if 'motor_status' in status_data:
                self.motor_status = status_data['motor_status']
            if 'task_status' in status_data:
                self.task_status = status_data['task_status']
            if 'sensor_data' in status_data:
                self.sensor_data.update(status_data['sensor_data'])
            
            self.status = "online"
            self.last_updated = datetime.now()
            return True
        except Exception as e:
            logging.error(f"로봇 상태 업데이트 실패: {e}")
            return False
    
    def get_battery_status(self) -> Dict[str, Any]:
        """배터리 상태 반환"""
        return {
            'level': self.battery_level,
            'wh': self.battery_wh,
            'status': self._get_battery_status_level()
        }
    
    def _get_battery_status_level(self) -> str:
        """배터리 상태 레벨 반환"""
        if self.battery_level > 80:
            return "high"
        elif self.battery_level > 50:
            return "medium"
        elif self.battery_level > 20:
            return "low"
        else:
            return "critical"


class SDA_Device(SDI_Device):
    """
    SDA (Smart Device Air) - 에어 디바이스 클래스
    드론, 비행기 등 공중 관련 디바이스
    """
    
    def __init__(self, device_id: str, air_type: str, location: str = ""):
        super().__init__(device_id, "air", location)
        self.air_type = air_type
        self.altitude = 0.0
        self.speed = 0.0
        self.battery_level = 0.0
        self.gps_coordinates = {"lat": 0.0, "lng": 0.0}
        self.flight_status = "grounded"
        
    def get_device_info(self) -> Dict[str, Any]:
        """에어 디바이스 정보 반환"""
        info = self.get_basic_info()
        info.update({
            'air_type': self.air_type,
            'altitude': self.altitude,
            'speed': self.speed,
            'battery_level': self.battery_level,
            'flight_status': self.flight_status,
            'gps_coordinates': self.gps_coordinates
        })
        return info
    
    def get_status_data(self) -> Dict[str, Any]:
        """에어 디바이스 상태 데이터 반환"""
        return {
            'device_id': self.device_id,
            'altitude': self.altitude,
            'speed': self.speed,
            'battery_level': self.battery_level,
            'flight_status': self.flight_status,
            'gps_coordinates': self.gps_coordinates,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_status(self, status_data: Dict[str, Any]) -> bool:
        """에어 디바이스 상태 업데이트"""
        try:
            if 'altitude' in status_data:
                self.altitude = float(status_data['altitude'])
            if 'speed' in status_data:
                self.speed = float(status_data['speed'])
            if 'battery_level' in status_data:
                self.battery_level = float(status_data['battery_level'])
            if 'flight_status' in status_data:
                self.flight_status = status_data['flight_status']
            if 'gps_coordinates' in status_data:
                self.gps_coordinates.update(status_data['gps_coordinates'])
            
            self.status = "online"
            self.last_updated = datetime.now()
            return True
        except Exception as e:
            logging.error(f"에어 디바이스 상태 업데이트 실패: {e}")
            return False
    
    def get_flight_info(self) -> Dict[str, Any]:
        """비행 정보 반환"""
        return {
            'altitude': self.altitude,
            'speed': self.speed,
            'flight_status': self.flight_status,
            'gps_coordinates': self.gps_coordinates
        }


class SDV_Device(SDI_Device):
    """
    SDV (Smart Device Vehicle) - 비히클 디바이스 클래스
    자동차, 트럭 등 지상 이동체
    """
    
    def __init__(self, device_id: str, vehicle_type: str, location: str = ""):
        super().__init__(device_id, "vehicle", location)
        self.vehicle_type = vehicle_type
        self.speed = 0.0
        self.fuel_level = 0.0
        self.engine_status = "off"
        self.odometer = 0.0
        self.gps_coordinates = {"lat": 0.0, "lng": 0.0}
        
    def get_device_info(self) -> Dict[str, Any]:
        """비히클 디바이스 정보 반환"""
        info = self.get_basic_info()
        info.update({
            'vehicle_type': self.vehicle_type,
            'speed': self.speed,
            'fuel_level': self.fuel_level,
            'engine_status': self.engine_status,
            'odometer': self.odometer,
            'gps_coordinates': self.gps_coordinates
        })
        return info
    
    def get_status_data(self) -> Dict[str, Any]:
        """비히클 상태 데이터 반환"""
        return {
            'device_id': self.device_id,
            'speed': self.speed,
            'fuel_level': self.fuel_level,
            'engine_status': self.engine_status,
            'odometer': self.odometer,
            'gps_coordinates': self.gps_coordinates,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_status(self, status_data: Dict[str, Any]) -> bool:
        """비히클 상태 업데이트"""
        try:
            if 'speed' in status_data:
                self.speed = float(status_data['speed'])
            if 'fuel_level' in status_data:
                self.fuel_level = float(status_data['fuel_level'])
            if 'engine_status' in status_data:
                self.engine_status = status_data['engine_status']
            if 'odometer' in status_data:
                self.odometer = float(status_data['odometer'])
            if 'gps_coordinates' in status_data:
                self.gps_coordinates.update(status_data['gps_coordinates'])
            
            self.status = "online"
            self.last_updated = datetime.now()
            return True
        except Exception as e:
            logging.error(f"비히클 상태 업데이트 실패: {e}")
            return False
    
    def get_vehicle_status(self) -> Dict[str, Any]:
        """비히클 상태 반환"""
        return {
            'speed': self.speed,
            'fuel_level': self.fuel_level,
            'engine_status': self.engine_status,
            'odometer': self.odometer,
            'gps_coordinates': self.gps_coordinates
        } 