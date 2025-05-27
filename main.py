from machine import Pin, PWM
import time

# Ορισμός μοτέρ
motor1_for = PWM(Pin(9))
motor1_back = PWM(Pin(8))
motor2_for = PWM(Pin(11))
motor2_back = PWM(Pin(10))

for motor in [motor1_for, motor1_back, motor2_for, motor2_back]:
    motor.freq(1000)

# Αισθητήρες γραμμής
sensor_left = Pin(6, Pin.IN)
sensor_center = Pin(16, Pin.IN)
sensor_right = Pin(2, Pin.IN)

# PID παράμετροι - επιστροφή σε πιο συντηρητικές τιμές
Kp = 10000     # Μεσαία τιμή
Ki = 0         # Αρχικά χωρίς integral
Kd = 1500      # Μεσαίο derivative

# Μεταβλητές PID
previous_error = 0
integral = 0

# Ταχύτητες - πιο συντηρητικές
base_speed = 40000
max_speed = 60000
min_speed = 5000
max_delta_speed = 10000

# Αναζήτηση όταν χαθεί η γραμμή
zigzag_state = 1
zigzag_counter = 0
zigzag_duration = 10
lost_line_counter = 0

# Συνάρτηση ανάγνωσης αισθητήρων
def read_sensors():
    return (1 - sensor_left.value(), 1 - sensor_center.value(), 1 - sensor_right.value())

# Συνάρτηση ρύθμισης μοτέρ
def set_motors(left_speed, right_speed):
    left_speed = max(min_speed, min(left_speed, max_speed))
    right_speed = max(min_speed, min(right_speed, max_speed))
    
    motor2_for.duty_u16(0)
    motor2_back.duty_u16(int(left_speed))
    motor1_for.duty_u16(0)
    motor1_back.duty_u16(int(right_speed))

# Σταμάτημα μοτέρ
def stop_motors():
    for motor in [motor1_for, motor1_back, motor2_for, motor2_back]:
        motor.duty_u16(0)

# Περιορισμός απότομων μεταβολών
def limit_speed_change(current, target):
    if target > current + max_delta_speed:
        return current + max_delta_speed
    elif target < current - max_delta_speed:
        return current - max_delta_speed
    else:
        return target

previous_left_speed = base_speed
previous_right_speed = base_speed

print("Line Follower ξεκινά - Δοκιμή κατεύθυνσης...")

# ===== ΚΥΡΙΟΣ ΒΡΟΧΟΣ =====
while True:
    left, center, right = read_sensors()
    total = left + center + right
    
    # Τερματική γραμμή
    if total == 3:
        stop_motors()
        print("Τερματική γραμμή. Σταμάτησε.")
        break
    
    # Χαμένη γραμμή
    elif total == 0:
        lost_line_counter += 1
        
        if lost_line_counter > 5:  # Περίμενε λίγο πριν ξεκινήσει zigzag
            zigzag_counter += 1
            if zigzag_counter > zigzag_duration:
                zigzag_state *= -1
                zigzag_counter = 0
            
            left_speed = base_speed + (zigzag_state * 15000)
            right_speed = base_speed - (zigzag_state * 15000)
            
            set_motors(left_speed, right_speed)
            print(f"Zigzag αναζήτηση: {zigzag_state}")
        else:
            # Συνέχισε ίσια για λίγο
            set_motors(base_speed, base_speed)
            print("Συνέχεια ίσια...")
        
        time.sleep(0.01)
        continue
    
    # Reset lost counter
    lost_line_counter = 0
    
    # ===== ΑΠΛΟΣ ERROR ΥΠΟΛΟΓΙΣΜΟΣ =====
    error = 0
    
    if left and not center and not right:
        error = 2      # Αριστερά
    elif left and center and not right:
        error = 1      # Ελαφρά αριστερά
    elif not left and center and not right:
        error = 0      # Ευθεία
    elif not left and center and right:
        error = -1     # Ελαφρά δεξιά
    elif not left and not center and right:
        error = -2     # Δεξιά
    elif left and not center and right:
        error = 0      # Διασταύρωση - συνέχισε ίσια
    else:
        error = 0
    
    # Απλός PD έλεγχος (χωρίς integral προς το παρόν)
    derivative = error - previous_error
    pid = (Kp * error) + (Kd * derivative)
    previous_error = error
    
    # ΔΟΚΙΜΗ ΚΑΙ ΤΩΝ ΔΥΟ ΚΑΤΕΥΘΥΝΣΕΩΝ
    # Πρώτα δοκιμάζουμε την αρχική λογική
    left_speed = base_speed - pid
    right_speed = base_speed + pid
    
    # Αν το error είναι θετικό (αριστερά) και η ταχύτητα του αριστερού μοτέρ μειώνεται,
    # τότε το robot θα στρίψει αριστερά (σωστό)
    # Αν όμως πάει λάθος, θα χρειαστεί να αντιστρέψουμε
    
    left_speed = limit_speed_change(previous_left_speed, left_speed)
    right_speed = limit_speed_change(previous_right_speed, right_speed)
    
    set_motors(left_speed, right_speed)
    
    previous_left_speed = left_speed
    previous_right_speed = right_speed
    
    # Εκτενές debug για να καταλάβουμε τι συμβαίνει
    direction = ""
    if error > 0:
        direction = f"ΣΤΡΙΒΩ ΑΡΙΣΤΕΡΑ (L:{int(left_speed)} < R:{int(right_speed)})"
    elif error < 0:
        direction = f"ΣΤΡΙΒΩ ΔΕΞΙΑ (L:{int(left_speed)} > R:{int(right_speed)})"
    else:
        direction = f"ΕΥΘΕΙΑ (L:{int(left_speed)} = R:{int(right_speed)})"
    
    print(f"L:{left} C:{center} R:{right} | Err:{error} | {direction}")
    
    time.sleep(0.01)