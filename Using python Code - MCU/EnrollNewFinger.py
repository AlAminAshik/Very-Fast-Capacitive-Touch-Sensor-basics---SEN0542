import serial
import time

SERIAL_PORT = 'COM3'      # Change to your USB-TTL port
BAUD_RATE = 115200
DID = 0x01                # Try 0x00 if no response

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
time.sleep(0.3)

def cmd(cmd_id, data=b''):
    packet = bytearray(26)
    packet[0:4] = b'\x55\xAA\x00' + DID.to_bytes(1, 'little')
    packet[4:6] = cmd_id.to_bytes(2, 'little')
    packet[6:8] = len(data).to_bytes(2, 'little')
    packet[8:8+len(data)] = data
    packet[24:26] = (sum(packet[:24]) & 0xFFFF).to_bytes(2, 'little')
    ser.write(packet)
    resp = ser.read(26)
    if len(resp) < 26 or resp[0:2] != b'\xAA\x55':
        return 0xFF, b''
    ret = int.from_bytes(resp[8:10], 'little')
    data_len = int.from_bytes(resp[6:8], 'little') - 2
    return ret, resp[10:10+data_len] if data_len > 0 else b''

# Prompt for ID
try:
    fid = int(input("Enter the fingerprint ID to enroll (1-80): "))
    if not 1 <= fid <= 80:
        print("ID must be between 1 and 80")
        ser.close()
        exit()
except:
    print("Invalid input")
    ser.close()
    exit()

print(f"Enrolling fingerprint for ID: {fid}")

# Force delete if ID exists (to avoid duplication errors)
del_data = fid.to_bytes(2, 'little') + fid.to_bytes(2, 'little')
ret, _ = cmd(0x0040, del_data)
if ret == 0x0000:
    print("Existing template deleted")
else:
    print(f"Delete returned 0x{ret:04X} - continuing")

# Single press enrollment (reliable for this module)
print("Press finger firmly in the center and keep it steady...")

while True:
    ret, _ = cmd(0x0021)
    if ret == 0x0000:
        break
    time.sleep(0.3)

time.sleep(1.0)  # Stabilize

# Capture image with retries
for _ in range(10):
    ret, _ = cmd(0x0020)
    if ret == 0x0000:
        break
    time.sleep(1.0)

if ret != 0x0000:
    print(f"Image capture failed (error 0x{ret:04X})")
    ser.close()
    exit()

# Generate template in buffer 0 (valid for ID809)
ret, _ = cmd(0x0060, b'\x00\x00')
if ret != 0x0000:
    print(f"Template generation failed (error 0x{ret:04X}) - try better finger placement")
    ser.close()
    exit()

print("Lift finger now.")
time.sleep(4)

# Store from buffer 0 to ID
store_data = b'\x00\x00' + fid.to_bytes(2, 'little')
ret, _ = cmd(0x0062, store_data)
if ret == 0x0000:
    print(f"Enrollment successful! Fingerprint stored as ID {fid}")
else:
    print(f"Store failed (error code: 0x{ret:04X})")

ser.close()