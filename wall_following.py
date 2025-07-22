from controller import Robot
import math

# ฟังก์ชันหลักในการควบคุมหุ่นยนต์
def run_robot(robot):
    # === ค่าคงที่สำหรับการคำนวณ ===
    TIME_STEP = 20          # เวลาในแต่ละรอบการอัปเดตของเซ็นเซอร์และมอเตอร์ (มิลลิวินาที)
    MAX_SPEED = 4           # ความเร็วสูงสุดของล้อ
    WHEEL_RADIUS = 0.02     # รัศมีล้อ (หน่วย: เมตร)
    AXLE_LENGTH = 0.053     # ระยะห่างระหว่างล้อซ้ายและขวา (หน่วย: เมตร)

    # === กำหนดและเปิดใช้งานมอเตอร์ซ้าย/ขวา ===
    left_motor = robot.getDevice('left wheel motor')
    right_motor = robot.getDevice('right wheel motor')
    left_motor.setPosition(float('inf'))  # ให้ล้อหมุนได้อย่างอิสระ (ไม่กำหนดจุดหยุด)
    right_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)           # เริ่มต้นด้วยความเร็ว 0
    right_motor.setVelocity(0.0)

    # === เชื่อมต่อกับเซ็นเซอร์ encoder ที่ล้อทั้งสอง ===
    left_encoder = robot.getDevice('left wheel sensor')
    right_encoder = robot.getDevice('right wheel sensor')
    left_encoder.enable(TIME_STEP)
    right_encoder.enable(TIME_STEP)

    # === เปิดใช้งาน Proximity Sensors เพื่อวัดระยะห่างสิ่งกีดขวาง ===
    ps_front_left = robot.getDevice('ps7')    # ด้านหน้าซ้าย
    ps_front_right = robot.getDevice('ps0')   # ด้านหน้าขวา
    ps_left = robot.getDevice('ps6')          # ด้านข้างซ้าย
    ps_right = robot.getDevice('ps1')         # ด้านข้างขวา

    ps_front_left.enable(TIME_STEP)
    ps_front_right.enable(TIME_STEP)
    ps_left.enable(TIME_STEP)
    ps_right.enable(TIME_STEP)

    # === กำหนดค่าตำแหน่งเริ่มต้น (x, z) และมุม (theta) ===
    x, z, theta = 0.0, 0.0, 0.0          # พิกัดเริ่มต้นของหุ่นยนต์
    prev_left = 0.0                      # ค่าการหมุนของล้อซ้ายก่อนหน้า
    prev_right = 0.0                     # ค่าการหมุนของล้อขวาก่อนหน้า

    print("เริ่มเดินชิดกำแพงซ้าย...")

    # === วนลูปให้หุ่นยนต์ทำงานทุก ๆ TIME_STEP ===
    while robot.step(TIME_STEP) != -1:
        # --- อ่านค่าการหมุนของล้อ ---
        left_pos = left_encoder.getValue()
        right_pos = right_encoder.getValue()

        # --- คำนวณระยะทางที่ล้อแต่ละข้างหมุนไป ---
        d_left = (left_pos - prev_left) * WHEEL_RADIUS
        d_right = (right_pos - prev_right) * WHEEL_RADIUS

        # --- อัปเดตค่าก่อนหน้า ---
        prev_left = left_pos
        prev_right = right_pos

        # --- คำนวณระยะเคลื่อนที่ตรงกลาง และการหมุนตัว (theta) ---
        d_center = (d_left + d_right) / 2.0
        d_theta = (d_right - d_left) / AXLE_LENGTH

        # --- คำนวณตำแหน่งใหม่ของหุ่นยนต์ ---
        theta += d_theta
        x += d_center * math.cos(theta)
        z += d_center * math.sin(theta)

        print(f"Pos: ({x:.3f}, {z:.3f}), Theta: {math.degrees(theta):.1f} deg")

        # --- อ่านค่าจาก Proximity Sensors ---
        front_left = ps_front_left.getValue()
        front_right = ps_front_right.getValue()
        left = ps_left.getValue()
        right = ps_right.getValue()

        print(f"Front Left: {front_left:.2f}, Front Right: {front_right:.2f}")
        print(f"Left: {left:.2f}, Right: {right:.2f}")

        # === เกณฑ์สำหรับการตรวจจับสิ่งกีดขวางและผนัง ===
        front_threshold = 100    # ถ้าค่าเกินนี้แสดงว่ามีสิ่งกีดขวางด้านหน้า
        wall_threshold = 100     # ถ้าค่าต่ำกว่านี้แสดงว่า "ไม่มีผนัง"

        # === ตรรกะการควบคุมการเดินชิดซ้าย ===
        if front_left > front_threshold or front_right > front_threshold:
            # ถ้ามีสิ่งกีดขวางด้านหน้า → เลี้ยวขวา (ขยับล้อซ้ายเร็วกว่า)
            left_speed = MAX_SPEED * 0.4
            right_speed = MAX_SPEED * 0.1
        elif left < wall_threshold:
            # ถ้าไม่มีผนังด้านซ้าย → เลี้ยวซ้ายเข้าไปหา (ขยับล้อขวาเร็วกว่า)
            left_speed = MAX_SPEED * 0.1
            right_speed = MAX_SPEED * 0.4
        else:
            # ถ้าห่างจากผนังพอดี → เดินตรงไปข้างหน้า
            left_speed = MAX_SPEED
            right_speed = MAX_SPEED

        # --- ตั้งค่าความเร็วให้ล้อซ้ายและขวา ---
        left_motor.setVelocity(left_speed)
        right_motor.setVelocity(right_speed)

# === เรียกใช้ฟังก์ชันหลัก เมื่อรันไฟล์นี้โดยตรง ===
if _name_ == "_main_":
    robot = Robot()
    run_robot(robot)