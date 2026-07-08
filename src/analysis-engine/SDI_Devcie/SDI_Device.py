from typing import Dict, Any
import logging
from datetime import datetime

class SDI_Device:
    """
    SDI (Smart Device Interface) - 스마트 디바이스 기본 클래스
    모든 스마트 디바이스의 기본 인터페이스
    """
    
    def __init__(self, device_id: str, device_type: str, location: str = ""):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.status = "offline"
        self.last_updated = datetime.now()
        
    def get_basic_info(self) -> Dict[str, Any]:
        """기본 디바이스 정보 반환"""
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'location': self.location,
            'status': self.status,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
        
    def get_device_info(self) -> Dict[str, Any]:
        """디바이스 정보 반환 (서브클래스에서 구현)"""
        return self.get_basic_info()
        
    def get_status_data(self) -> Dict[str, Any]:
        """상태 데이터 반환 (서브클래스에서 구현)"""
        return {
            'device_id': self.device_id,
            'status': self.status,
            'timestamp': datetime.now().isoformat()
        }
        
    def update_status(self, status_data: Dict[str, Any]) -> bool:
        """상태 업데이트 (서브클래스에서 구현)"""
        try:
            self.status = status_data.get('status', self.status)
            self.last_updated = datetime.now()
            return True
        except Exception as e:
            logging.error(f"상태 업데이트 실패: {e}")
            return False