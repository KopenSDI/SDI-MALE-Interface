from .SDI_Device import SDI_Device
from typing import Dict, Any
import logging
from datetime import datetime
    
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