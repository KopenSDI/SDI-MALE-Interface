from flask import jsonify
from models.battery_model import BatteryModel
from typing import Dict, Any
import logging

class BatteryController:
    def __init__(self, battery_model: BatteryModel):
        self.battery_model = battery_model

    def get_all_battery_status(self, lookback: str = "-30m") -> Dict[str, Any]:
        """모든 터틀봇의 배터리 상태 조회"""
        try:
            status_list = self.battery_model.get_all_battery_status(lookback)
            return jsonify({
                'success': True,
                'data': status_list,
                'lookback': lookback,
                'timestamp': self.battery_model._get_current_timestamp()
            })
        except Exception as e:
            logging.error(f"배터리 상태 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'data': []
            }), 500

    def get_battery_by_bot(self, bot_name: str, lookback: str = "-30m") -> Dict[str, Any]:
        """특정 터틀봇의 배터리 상태 조회"""
        try:
            status = self.battery_model.get_battery_status(bot_name, lookback)
            return jsonify({
                'success': True,
                'data': status,
                'lookback': lookback
            })
        except Exception as e:
            logging.error(f"터틀봇 {bot_name} 배터리 상태 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'data': None
            }), 500

    def get_available_bots(self) -> Dict[str, Any]:
        """사용 가능한 터틀봇 목록 조회"""
        try:
            bots = self.battery_model.get_available_bots()
            return jsonify({
                'success': True,
                'data': bots,
                'count': len(bots)
            })
        except Exception as e:
            logging.error(f"터틀봇 목록 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'data': []
            }), 500

    def get_battery_history(self, bot_name: str, hours: int = 24) -> Dict[str, Any]:
        """특정 터틀봇의 배터리 히스토리 조회"""
        try:
            history = self.battery_model.get_battery_history(bot_name, hours)
            return jsonify({
                'success': True,
                'data': history,
                'hours': hours
            })
        except Exception as e:
            logging.error(f"터틀봇 {bot_name} 히스토리 조회 실패: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'data': None
            }), 500 