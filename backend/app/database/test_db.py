from database.mysql_db import fetch_motor_by_power

motors = fetch_motor_by_power(5)

print(motors)