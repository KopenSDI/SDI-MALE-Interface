from typing import List, Dict, Any, Optional
from services.influx_service import InfluxService
import logging

class BatteryModel:
    def __init__(self, influx_service: InfluxService):
        self.influx_service = influx_service

    def get_battery_status(self, bot_name: str, lookback: str = "-30m") -> Dict[str, Any]:
        """특정 터틀봇의 배터리 상태 조회"""
        wh = self.influx_service.get_latest_battery_status(bot_name, lookback)
        
        return {
            'bot': bot_name,
            'wh': wh,
            'status': self._get_battery_status_level(wh),
            'percentage': self._calculate_battery_percentage(wh),
            'last_updated': self._get_current_timestamp()
        }

    def get_all_battery_status(self, lookback: str = "-30m") -> List[Dict[str, Any]]:
        """모든 터틀봇의 배터리 상태 조회"""
        return self.influx_service.get_all_bots_battery_status(lookback)

    def get_battery_history(self, bot_name: str, hours: int = 24) -> Dict[str, Any]:
        """특정 터틀봇의 배터리 히스토리 조회"""
        history = self.influx_service.get_battery_history(bot_name, hours)
        
        return {
            'bot': bot_name,
            'history': history,
            'summary': self._calculate_history_summary(history),
            'hours': hours
        }

    def get_available_bots(self) -> List[str]:
        """사용 가능한 터틀봇 목록 조회"""
        return self.influx_service.get_available_bots()

    def _get_battery_status_level(self, wh: Optional[float]) -> str:
        """배터리 잔량에 따른 상태 레벨 반환"""
        if wh is None:
            return 'unknown'
        elif wh > 400:
            return 'high'
        elif wh > 300:
            return 'medium'
        elif wh > 200:
            return 'low'
        else:
            return 'critical'

    def _calculate_battery_percentage(self, wh: Optional[float]) -> Optional[float]:
        """배터리 잔량을 퍼센트로 변환 (500Wh를 100%로 가정)"""
        if wh is None:
            return None
        # 500Wh를 100%로 가정
        max_wh = 500.0
        percentage = (wh / max_wh) * 100
        return round(percentage, 1)

    def _calculate_history_summary(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """히스토리 데이터의 요약 정보 계산"""
        if not history:
            return {
                'count': 0,
                'avg_wh': None,
                'min_wh': None,
                'max_wh': None,
                'trend': 'unknown'
            }

        wh_values = [item['wh'] for item in history if item['wh'] is not None]
        
        if not wh_values:
            return {
                'count': len(history),
                'avg_wh': None,
                'min_wh': None,
                'max_wh': None,
                'trend': 'unknown'
            }

        avg_wh = sum(wh_values) / len(wh_values)
        min_wh = min(wh_values)
        max_wh = max(wh_values)

        # 트렌드 계산 (최근 3개 데이터 포인트 기준)
        trend = 'stable'
        if len(wh_values) >= 3:
            recent_avg = sum(wh_values[-3:]) / 3
            older_avg = sum(wh_values[:3]) / 3
            if recent_avg > older_avg + 10:
                trend = 'increasing'
            elif recent_avg < older_avg - 10:
                trend = 'decreasing'

        return {
            'count': len(history),
            'avg_wh': round(avg_wh, 1),
            'min_wh': round(min_wh, 1),
            'max_wh': round(max_wh, 1),
            'trend': trend
        }

    def _get_current_timestamp(self) -> str:
        """현재 시간을 ISO 형식으로 반환"""
        from datetime import datetime
        return datetime.now().isoformat() 