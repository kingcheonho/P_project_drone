from codrone_edu.drone import *
import time

# 드론 연결
drone = Drone()
drone.pair()

# --- 데이터를 담을 Array (리스트) 초기화 ---
log_data = [] 

print("이륙")
drone.takeoff()
drone.hover(3)

print("=== 데이터 수집 시작 ===")
print("[Ctrl+C]를 눌러 종료하세요.")

start_time = time.time()
last_time = start_time
last_height = drone.get_height()

try:
    while True: # 사용자가 멈출 때까지 무한 루프
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        dt = current_time - last_time 

        # --- 데이터 센싱 ---
        soc = drone.get_battery()       
        height = drone.get_height()     
        
        # 이름 바뀐 함수 적용
        flow_x = drone.get_flow_velocity_x()     
        flow_y = drone.get_flow_velocity_y()     

        if dt > 0:
            vertical_speed = (height - last_height) / dt 
        else:
            vertical_speed = 0

        # [시간, 배터리, 고도, 수직속도, FlowX, FlowY]
        current_row = [round(elapsed_time, 2), soc, height, round(vertical_speed, 1), flow_x, flow_y]
        log_data.append(current_row)
        
        # 모니터링용 출력
        print(f"Time:{elapsed_time:.1f} | Bat:{soc}% | Alt:{height} | Data Count:{len(log_data)}")

        last_time = current_time
        last_height = height

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n착륙")
    drone.land()

finally:
    drone.close()
    
    # --- 파일 저장 대신 화면에 출력 ---
    print("\n" + "="*30)
    print("Format: [Time, Battery, Height, V_Speed, FlowX, FlowY]")
    print("="*30)

    print(log_data)
    
    print("="*30)
    print(f"총 {len(log_data)}개의 데이터 샘플이 수집완료")