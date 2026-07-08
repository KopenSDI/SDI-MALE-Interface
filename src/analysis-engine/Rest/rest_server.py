from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import logging
from datetime import datetime

class RestServer:
    def __init__(self, analysis_controller, port=5000):
        self.analysis_controller = analysis_controller
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # CORS 허용
        self._setup_routes()
        self._running = False
        
    def _setup_routes(self):
        """REST API 라우트 설정"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """헬스 체크 엔드포인트"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'analysis-engine-rest'
            })
        
        @self.app.route('/api/scores', methods=['GET'])
        def get_scores():
            """SDI 스케줄러용 점수 조회 API"""
            try:
                # GetALEWeight 메서드 호출 (533라인)
                result = self.analysis_controller.get_ale_scores_for_devices([])
                
                if result.get('success', False):
                    # 첫 번째 디바이스의 점수를 기본값으로 사용
                    if result.get('ale_scores') and len(result['ale_scores']) > 0:
                        first_score = result['ale_scores'][0]
                        return jsonify({
                            'success': True,
                            'accuracy_score': int(first_score.get('accuracy_score', 50)),
                            'latency_score': int(first_score.get('latency_score', 50)),
                            'energy_score': int(first_score.get('energy_score', 50)),
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        # 기본값 반환
                        return jsonify({
                            'success': True,
                            'accuracy_score': 50,
                            'latency_score': 50,
                            'energy_score': 50,
                            'timestamp': datetime.now().isoformat()
                        })
                else:
                    return jsonify({
                        'success': False,
                        'message': result.get('message', '점수 조회 실패'),
                        'accuracy_score': 50,
                        'latency_score': 50,
                        'energy_score': 50
                    }), 500
                    
            except Exception as e:
                logging.error(f"GetScores API error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'accuracy_score': 50,
                    'latency_score': 50,
                    'energy_score': 50
                }), 500
        
        @self.app.route('/api/ale-weights', methods=['GET'])
        def get_ale_weights():
            """ALE 가중치 조회 API"""
            try:
                device_id = request.args.get('device_id', '')
                device_ids = request.args.getlist('device_ids')
                
                result = self.analysis_controller.get_ale_scores_for_devices(device_ids)
                
                return jsonify(result)
                
            except Exception as e:
                logging.error(f"GetALEWeights API error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error: {str(e)}'
                }), 500
        
        @self.app.route('/api/device-score', methods=['GET'])
        def get_device_score():
            """디바이스 점수 조회 API"""
            try:
                device_id = request.args.get('device_id', 'default')
                service_type = request.args.get('service_type', 'ml-inference')
                
                result = self.analysis_controller.get_device_score(device_id, service_type)
                
                return jsonify(result)
                
            except Exception as e:
                logging.error(f"GetDeviceScore API error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error: {str(e)}'
                }), 500
        
        @self.app.route('/api/devices', methods=['GET'])
        def get_all_devices():
            """모든 디바이스 조회 API"""
            try:
                result = self.analysis_controller.get_all_devices()
                return jsonify(result)
                
            except Exception as e:
                logging.error(f"GetAllDevices API error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error: {str(e)}'
                }), 500
        
        @self.app.route('/api/device/<device_id>/status', methods=['GET'])
        def get_device_status(device_id):
            """디바이스 상태 조회 API"""
            try:
                result = self.analysis_controller.get_device_status(device_id)
                return jsonify(result)
                
            except Exception as e:
                logging.error(f"GetDeviceStatus API error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error: {str(e)}'
                }), 500
        
        @self.app.route('/api/device/<device_id>/analyze', methods=['POST'])
        def analyze_device(device_id):
            """디바이스 분석 API"""
            try:
                result = self.analysis_controller.analyze_device_performance(device_id)
                return jsonify(result)
                
            except Exception as e:
                logging.error(f"AnalyzeDevice API error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Error: {str(e)}'
                }), 500
    
    def start(self):
        """REST 서버 시작"""
        if not self._running:
            self._running = True
            threading.Thread(target=self._run_server, daemon=True).start()
            logging.info(f"REST 서버가 포트 {self.port}에서 시작되었습니다.")
    
    def _run_server(self):
        """서버 실행"""
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
        except Exception as e:
            logging.error(f"REST 서버 실행 오류: {e}")
            self._running = False
    
    def stop(self):
        """REST 서버 중지"""
        self._running = False
        logging.info("REST 서버가 중지되었습니다.")
    
    def is_running(self):
        """서버 실행 상태 확인"""
        return self._running



