# KETI Analysis Engine with gRPC & REST Support (both possible)
from AnalysisEngine import KETI_AnalysisEngine
from Rest.rest_server import RestServer
import threading
import time
import argparse
import logging
import os
import sys
import signal

# 사용 예:
# 1) gRPC만:  python3 main.py --grpc --grpc-port 50051
# 2) REST만:  python3 main.py --rest --rest-port 5000
# 3) 둘다:   python3 main.py --both --grpc-port 50051 --rest-port 5000
# (스케줄러는 REST 5000에 붙으므로 실제 운영은 --both 권장)

def main():
    parser = argparse.ArgumentParser(description="KETI Analysis Engine")
    parser.add_argument("--name", default="KETI-AnalysisEngine", help="Engine name")

    # 실행 모드
    parser.add_argument("--grpc", action="store_true", help="Run gRPC server mode")
    parser.add_argument("--rest", action="store_true", help="Run REST API server mode")
    parser.add_argument("--both", action="store_true", help="Run BOTH gRPC and REST servers")

    # 포트 분리 옵션
    parser.add_argument("--port", type=int, default=50051, help="(deprecated) Server port (use --grpc-port/--rest-port)")
    parser.add_argument("--grpc-port", type=int, default=50051, help="gRPC server port")
    parser.add_argument("--rest-port", type=int, default=5000, help="REST server port")

    parser.add_argument("--test", action="store_true", help="Run test mode only")
    args = parser.parse_args()

    # 하위호환: --port가 명시됐고 새 옵션 안 썼다면 gRPC포트로 사용
    if "--grpc-port" not in sys.argv and "--rest-port" not in sys.argv and "--port" in sys.argv:
        args.grpc_port = args.port

    # 로그
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # 엔진 준비
    engine = KETI_AnalysisEngine(args.name)
    print(f"Engine Name: {engine.get_EngineName()}")

    # 종료 핸들러
    shutdown = {"flag": False}
    def handle_sigint(signum, frame):
        shutdown["flag"] = True
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)

    if args.test:
        print("테스트 모드로 실행")
        engine.test_run()
        return

    # gRPC/REST/엔진 스레드 핸들
    grpc_server = None
    rest_server = None
    engine_thread = None

    def start_engine_thread():
        t = threading.Thread(target=engine.run, name="engine-loop", daemon=True)
        t.start()
        return t

    def stop_all():
        try:
            if rest_server is not None:
                print("REST 서버 중지 시도...")
                rest_server.stop()
        except Exception as e:
            print(f"REST 서버 중지 중 예외: {e}")
        try:
            if grpc_server is not None:
                print("gRPC 서버 중지 시도...")
                engine.view.stop_grpc_server()
        except Exception as e:
            print(f"gRPC 서버 중지 중 예외: {e}")
        try:
            print("분석 엔진 중지 시도...")
            engine.stop()
        except Exception as e:
            print(f"엔진 중지 중 예외: {e}")

    try:
        # ---------------------------
        # BOTH 모드: gRPC + REST 동시 구동
        # ---------------------------
        if args.both or (args.grpc and args.rest):
            print(f"[BOTH] gRPC({args.grpc_port}) + REST({args.rest_port}) 서버 모드로 실행")
            try:
                # gRPC 시작
                grpc_server = engine.view.start_grpc_server(args.grpc_port)
                print(f"gRPC 분석 서버가 포트 {args.grpc_port}에서 시작되었습니다.")
            except Exception as e:
                print(f"gRPC 서버 시작 실패: {e}")
                raise

            try:
                # REST 시작 (수정된 부분)
                rest_thread = engine.view.start_rest_server_in_thread(port=args.rest_port)
                # 'rest_server' 변수는 더 이상 클래스 인스턴스가 아니지만, 
                # 스레드 객체를 이용해 실행 여부를 확인할 수 있습니다.
                rest_server = rest_thread 
                print(f"REST API 서버가 포트 {args.rest_port}에서 시작되었습니다.")
            except Exception as e:
                print(f"REST 서버 시작 실패: {e}")
                raise

            # 엔진 루프 시작
            engine_thread = start_engine_thread()
            print("분석 엔진과 두 서버가 동시에 실행됩니다. (Ctrl+C로 종료)")

            # 메인 루프: 종료 신호 대기
            while not shutdown["flag"]:
                time.sleep(1)

            print("\n서버 중지 중...")
            stop_all()
            if engine_thread:
                engine_thread.join(timeout=5)
            print("서버 종료")
            return

        # ---------------------------
        # gRPC 전용
        # ---------------------------
        elif args.grpc:
            print(f"gRPC 서버 모드로 실행 (포트: {args.grpc_port})")
            try:
                grpc_server = engine.view.start_grpc_server(args.grpc_port)
                print(f"gRPC 분석 서버가 포트 {args.grpc_port}에서 시작되었습니다.")
                print("분석 엔진과 gRPC 서버가 동시에 실행됩니다. (Ctrl+C로 종료)")
                engine_thread = start_engine_thread()
                engine.view.wait_for_termination()
            except KeyboardInterrupt:
                print("\n서버 중지 중...")
            except Exception as e:
                print(f"gRPC 서버 시작 실패: {e}")
                import traceback; traceback.print_exc()
            finally:
                stop_all()
                if engine_thread:
                    engine_thread.join(timeout=5)
                print("서버 종료")
            return

        # ---------------------------
        # REST 전용
        # ---------------------------
        elif args.rest:
            print(f"REST API 서버 모드로 실행 (포트: {args.rest_port})")
            try:
                rest_server = RestServer(engine.controller, args.rest_port)
                rest_server.start()
                print(f"REST API 서버가 포트 {args.rest_port}에서 시작되었습니다.")
                print("분석 엔진과 REST API 서버가 동시에 실행됩니다. (Ctrl+C로 종료)")
                engine_thread = start_engine_thread()
                while not shutdown["flag"] and rest_server.is_running():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n서버 중지 중...")
            except Exception as e:
                print(f"REST 서버 시작 실패: {e}")
                import traceback; traceback.print_exc()
            finally:
                stop_all()
                if engine_thread:
                    engine_thread.join(timeout=5)
                print("서버 종료")
            return

        # ---------------------------
        # 아무 플래그도 없으면 기존 일반 모드
        # ---------------------------
        else:
            print("일반 모드로 실행 (서버 미구동, 엔진 루프만)")
            engine_thread = start_engine_thread()
            try:
                while not shutdown["flag"]:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                print("\n서버 중지 중...")
                stop_all()
                if engine_thread:
                    engine_thread.join(timeout=5)
                print("서버 종료")

    except KeyboardInterrupt:
        print("\n서버 중지 중(KeyboardInterrupt)...")
        stop_all()
        if engine_thread:
            engine_thread.join(timeout=5)
        print("서버 종료")


if __name__ == "__main__":
    main()
