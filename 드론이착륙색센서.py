from codrone_edu.drone import *
import time

# 1. 드론 객체 생성 및 페어링
drone = Drone()
#drone.pair()

print("드론 연결 완료. 배터리:", drone.get_battery())

# 전진 속도와 시간 설정
MOVE_SPEED = 20   # 속도 (0~100)
MOVE_TIME = 0.5     # 이동 시간 (초)

# 카운트 변수는 while 문 밖에서 초기화해야 계속 숫자가 올라갑니다.
count = 0 
total_distance = 0
total_optical_distance = 0

try:
    while True:
        count += 1 # 횟수 증가
        print(f"\n=== [ {count} 번째 탐사 시작 ] ===")
        drone.pair()

        # ----------------------------------------
        # 1. 이륙 (Takeoff)
        # ----------------------------------------
        print("🛫 이륙합니다.")
        drone.takeoff()
        drone.hover(1) # 안정화 대기

        # ----------------------------------------
        # 2. 앞으로 전진 (Forward)
        # ----------------------------------------
        print(f"⏩ 앞으로 {MOVE_TIME}초간 전진합니다.")
        
        # 이동 전 위치 저장 (Optical Flow)
        start_x = drone.get_pos_x()
        
        drone.set_pitch(MOVE_SPEED) # 앞으로 기울기 설정
        drone.move(MOVE_TIME)       # 설정된 시간만큼 이동
        
        # 이동 후 정지 (관성 제어)
        drone.set_pitch(0)          # 기울기 초기화 (필수)
        drone.hover(1)              # 잠깐 제자리 비행하여 멈춤
        
        # 이동 후 위치 저장 및 거리 계산
        end_x = drone.get_pos_x()
        optical_distance = end_x - start_x
        
        # 거리 계산 (속도 * 시간 - 이론값)
        current_distance = MOVE_SPEED * MOVE_TIME
        
        # 누적 거리 업데이트
        total_distance += current_distance
        total_optical_distance += optical_distance
        
        print(f"📏 이론 거리: {current_distance:.2f} (누적: {total_distance:.2f})")
        print(f"📷 광류 거리: {optical_distance:.2f}cm (누적: {total_optical_distance:.2f}cm)")

        # ----------------------------------------
        # 3. 착륙 (Land)
        # ----------------------------------------
        print("🛬 착륙합니다.")
        drone.land()

        # ----------------------------------------
        # 4. 색상 탐지 (Detect Color) - 수정됨
        # ----------------------------------------
        print("🎨 착륙 완료. 2초간 0.1초 간격으로 색상을 탐지합니다...")
        
        # 2초 동안 0.1초 간격으로 반복하므로 약 20회 반복 (20 * 0.1 = 2.0초)
        for j in range(30):
            # 요청하신 대로 get_colors() 사용
            detected_color = drone.get_colors()
            print(f"   [{j+1}/30] 감지된 색상: {detected_color}")
            
            # 0.1초 대기
            time.sleep(0.1)
        
        # 다음 반복 전 잠시 대기
        print(f"=== [ {count} 번째 탐사 종료 ] ===\n")
        time.sleep(1)
        drone.close()

except KeyboardInterrupt:
    print("\n\n⚠️ Ctrl+C가 감지되었습니다! 비상 착륙 및 종료 절차를 시작합니다.")
    # 공중에 떠 있을 수 있으므로 착륙 명령을 한 번 더 보냅니다.
    drone.land()

except Exception as e:
    print("오류 발생:", e)

finally:
    # 종료 시 반드시 연결 해제
    print("드론 연결을 해제합니다.")
    drone.close()