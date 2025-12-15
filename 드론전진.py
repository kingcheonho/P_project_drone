from codrone_edu.drone import *
import time
import pandas as pd

# ==========================================
# [사용자 설정 영역]
# ==========================================
TARGET_BATTERY_LIMIT = 20   # 착륙할 배터리 잔량 (%)
MOVE_THROTTLE = 30          # 이동 속도 (0 ~ 100) - 낮을수록 안정적
MOVE_DURATION = 6.0         # 한 방향으로 이동할 시간 (초)

# [고도 조절 설정]
DESCEND_POWER = -30         # 하강 출력 (음수여야 함, -20 ~ -40 권장)
DESCEND_TIME = 1.5         # 하강할 시간 (초) - 이 시간을 늘리면 더 낮게 내려갑니다.
# ==========================================

# 드론 연결
drone = Drone()
drone.pair()

# --- 데이터를 담을 리스트 ---
log_data = [] 

print("이륙...")
drone.takeoff()
drone.hover(3) # 이륙 후 잠시 자세 잡기

# ---------------------------------------------------------
# [중요] 옵티컬 플로우 인식을 위해 고도 낮추기
# ---------------------------------------------------------
print(f"센서 인식을 위해 고도를 낮춥니다... (Power: {DESCEND_POWER}, Time: {DESCEND_TIME}s)")
drone.set_throttle(DESCEND_POWER) # 하강 출력 설정
drone.move(DESCEND_TIME)          # 설정된 시간만큼 하강
drone.set_throttle(0)             # 하강 멈춤
drone.hover(1)                    # 낮은 고도에서 다시 자세 잡기 (매우 중요)
print("낮은 고도 비행 준비 완료.")
# ---------------------------------------------------------


print(f"=== 데이터 수집 및 왕복 비행 시작 (배터리 제한: {TARGET_BATTERY_LIMIT}%) ===")
print("[Ctrl+C]를 눌러 강제 종료하세요.")

start_time = time.time()
last_time = start_time
last_height = drone.get_height()

# 왕복 이동 변수
direction = 1       # 1: 전진, -1: 후진
last_dir_change_time = time.time()

try:
    while True: 
        current_time = time.time()
        elapsed_time = current_time - start_time
        dt = current_time - last_time 

        # --- 1. 배터리 체크 ---
        soc = drone.get_battery()       
        if soc <= TARGET_BATTERY_LIMIT:
            print(f"배터리 {soc}% 도달. 착륙합니다.")
            break

        # --- 2. 왕복 비행 로직 ---
        # 설정된 시간이 지나면 방향 전환
        if current_time - last_dir_change_time > MOVE_DURATION:
            direction *= -1 
            last_dir_change_time = current_time
            print(f"방향 전환 -> {'후진' if direction == -1 else '전진'}")

        # 피치(전후진) 제어
        drone.set_pitch(MOVE_THROTTLE * direction)
        
        # --- 3. 데이터 센싱 ---
        height = drone.get_height()     
        
        # 옵티컬 플로우 값 (고도가 낮아졌으니 값이 더 잘 나오는지 확인하세요)
        flow_x = drone.get_flow_velocity_x()     
        flow_y = drone.get_flow_velocity_y()     

        if dt > 0:
            vertical_speed = (height - last_height) / dt 
        else:
            vertical_speed = 0

        # [시간, 배터리, 고도, 수직속도, FlowX, FlowY]
        current_row = [round(elapsed_time, 2), soc, height, round(vertical_speed, 1), flow_x, flow_y]
        log_data.append(current_row)
        
        # 모니터링 출력
        dir_str = "Forward" if direction == 1 else "Backward"
        print(f"T:{elapsed_time:.1f} | Bat:{soc}% | Alt:{height}cm | FlowX:{flow_x} | {dir_str}")

        last_time = current_time
        last_height = height

        # 0.1초 동안 명령 수행 (데이터 수집 주기)
        drone.move(0.1) 

except KeyboardInterrupt:
    print("\n사용자 중단 - 착륙 시도")

finally:
    drone.set_pitch(0)
    drone.land()
    drone.close()
    
    # --- 결과 저장 ---
    print("\n" + "="*30)
    print(f"총 {len(log_data)}개의 데이터 샘플 수집")

    if len(log_data) > 0:
        df = pd.DataFrame(log_data, columns=["Time", "Battery", "Height", "V_Speed", "FlowX", "FlowY"])
        print("\nDataFrame Preview:")
        print(df.head())
        
        filename = "drone_low_altitude_data.csv"
        df.to_csv(filename, index=False)
        print(f"파일 저장 완료: {filename}")