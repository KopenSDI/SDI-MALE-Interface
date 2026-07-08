from models.sdi_device import SDV_Device
from typing import Dict, Any, Optional
from datetime import datetime
import logging

class TurtleBot(SDV_Device):
    """
    TurtleBot 클래스 - SDV_Device를 상속받는 터틀봇 전용 클래스
    터틀봇의 특화된 기능과 데이터를 관리
    """
    
    def __init__(self, device_id: str, turtlebot_model: str, location: str = ""):
        # SDV_Device 초기화 (vehicle_type을 "TurtleBot"으로 설정)
        super().__init__(device_id, "TurtleBot", location)
        
        # 터틀봇 특화 속성들
        self.turtlebot_model = turtlebot_model  # Burger, Waffle 등
        self.battery_level = 0.0
        self.battery_wh = 0.0
        self.linear_velocity = 0.0  # m/s
        self.angular_velocity = 0.0  # rad/s
        self.motor_status = "stopped"
        self.sensor_data = {
            'lidar': {'status': 'inactive', 'range': 0.0},
            'camera': {'status': 'inactive', 'frame_rate': 0},
            'imu': {'status': 'inactive', 'orientation': {'x': 0, 'y': 0, 'z': 0}},
            'odometry': {'status': 'inactive', 'position': {'x': 0, 'y': 0, 'z': 0}}
        }
        self.task_status = "idle"
        self.navigation_status = "idle"
        self.emergency_stop = False
        self.ros_status = "disconnected"
        
    def get_device_info(self) -> Dict[str, Any]:
        """터틀봇 디바이스 정보 반환"""
        info = super().get_device_info()
        info.update({
            'turtlebot_model': self.turtlebot_model,
            'battery_level': self.battery_level,
            'battery_wh': self.battery_wh,
            'motor_status': self.motor_status,
            'task_status': self.task_status,
            'navigation_status': self.navigation_status,
            'emergency_stop': self.emergency_stop,
            'ros_status': self.ros_status,
            'sensor_count': len(self.sensor_data)
        })
        return info
    
    def get_status_data(self) -> Dict[str, Any]:
        """터틀봇 상태 데이터 반환"""
        return {
            'device_id': self.device_id,
            'battery_level': self.battery_level,
            'battery_wh': self.battery_wh,
            'linear_velocity': self.linear_velocity,
            'angular_velocity': self.angular_velocity,
            'motor_status': self.motor_status,
            'task_status': self.task_status,
            'navigation_status': self.navigation_status,
            'emergency_stop': self.emergency_stop,
            'ros_status': self.ros_status,
            'sensor_data': self.sensor_data,
            'gps_coordinates': self.gps_coordinates,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_status(self, status_data: Dict[str, Any]) -> bool:
        """터틀봇 상태 업데이트"""
        try:
            # 기본 비히클 속성 업데이트
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
            
            # 터틀봇 특화 속성 업데이트
            if 'battery_level' in status_data:
                self.battery_level = float(status_data['battery_level'])
            if 'battery_wh' in status_data:
                self.battery_wh = float(status_data['battery_wh'])
            if 'linear_velocity' in status_data:
                self.linear_velocity = float(status_data['linear_velocity'])
            if 'angular_velocity' in status_data:
                self.angular_velocity = float(status_data['angular_velocity'])
            if 'motor_status' in status_data:
                self.motor_status = status_data['motor_status']
            if 'task_status' in status_data:
                self.task_status = status_data['task_status']
            if 'navigation_status' in status_data:
                self.navigation_status = status_data['navigation_status']
            if 'emergency_stop' in status_data:
                self.emergency_stop = bool(status_data['emergency_stop'])
            if 'ros_status' in status_data:
                self.ros_status = status_data['ros_status']
            if 'sensor_data' in status_data:
                self.sensor_data.update(status_data['sensor_data'])
            
            self.status = "online"
            self.last_updated = datetime.now()
            return True
        except Exception as e:
            logging.error(f"터틀봇 상태 업데이트 실패: {e}")
            return False
    
    def get_battery_status(self) -> Dict[str, Any]:
        """배터리 상태 반환"""
        return {
            'level': self.battery_level,
            'wh': self.battery_wh,
            'status': self._get_battery_status_level(),
            'estimated_runtime': self._estimate_runtime()
        }
    
    def get_movement_status(self) -> Dict[str, Any]:
        """이동 상태 반환"""
        return {
            'linear_velocity': self.linear_velocity,
            'angular_velocity': self.angular_velocity,
            'motor_status': self.motor_status,
            'emergency_stop': self.emergency_stop
        }
    
    def get_sensor_status(self) -> Dict[str, Any]:
        """센서 상태 반환"""
        return {
            'sensors': self.sensor_data,
            'active_sensors': [name for name, data in self.sensor_data.items() 
                             if data['status'] == 'active']
        }
    
    def get_navigation_status(self) -> Dict[str, Any]:
        """네비게이션 상태 반환"""
        return {
            'task_status': self.task_status,
            'navigation_status': self.navigation_status,
            'ros_status': self.ros_status,
            'gps_coordinates': self.gps_coordinates
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
    
    def _estimate_runtime(self) -> Optional[float]:
        """예상 런타임 계산 (분 단위)"""
        if self.battery_level <= 0:
            return None
        
        # 배터리 레벨과 현재 사용량을 기반으로 예상 런타임 계산
        # 실제 구현에서는 더 정확한 알고리즘 사용
        if self.battery_level > 80:
            return 120.0  # 2시간
        elif self.battery_level > 50:
            return 60.0   # 1시간
        elif self.battery_level > 20:
            return 20.0   # 20분
        else:
            return 5.0    # 5분
    
    def set_emergency_stop(self, emergency: bool) -> None:
        """비상 정지 설정"""
        self.emergency_stop = emergency
        if emergency:
            self.motor_status = "emergency_stop"
            self.task_status = "emergency"
        self.last_updated = datetime.now()
    
    def update_sensor_data(self, sensor_name: str, sensor_data: Dict[str, Any]) -> None:
        """특정 센서 데이터 업데이트"""
        if sensor_name in self.sensor_data:
            self.sensor_data[sensor_name].update(sensor_data)
            self.sensor_data[sensor_name]['status'] = 'active'
            self.last_updated = datetime.now()
    
    def get_ros_topic_data(self) -> Dict[str, Any]:
        """ROS 토픽 데이터 형식으로 반환"""
        return {
            '/battery_state': {
                'level': self.battery_level,
                'wh': self.battery_wh
            },
            '/cmd_vel': {
                'linear': {'x': self.linear_velocity, 'y': 0, 'z': 0},
                'angular': {'x': 0, 'y': 0, 'z': self.angular_velocity}
            },
            '/odom': {
                'position': self.sensor_data['odometry']['position'],
                'orientation': self.sensor_data['imu']['orientation']
            },
            '/scan': {
                'ranges': self.sensor_data['lidar']['range'] if self.sensor_data['lidar']['status'] == 'active' else []
            }
        } 