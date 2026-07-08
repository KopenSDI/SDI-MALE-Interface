from .SDI_Device import SDI_Device
from typing import Dict, Any
import logging
from datetime import datetime

class SDA_Device(SDI_Device):
    """
    SDA (Smart Device Air) - 에어 디바이스 클래스
    드론, 비행기 등 공중 관련 디바이스  GPT 피셜이라서 나중에 바꾸어야함
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
