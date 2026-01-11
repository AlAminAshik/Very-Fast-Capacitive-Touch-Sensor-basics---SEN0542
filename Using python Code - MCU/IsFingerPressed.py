import serial
import time

# ========== CONFIG ==========
PORT = 'COM3'        # Change if needed
BAUD = 115200
DID  = 0x00          # MUST be 0x00 (vendor default)
# ============================

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(0.5)

def cmd(cmd_id, data=b''):
    pkt = bytearray(26)
    pkt[0:4] = b'\x55\xAA\x00' + DID.to_bytes(1, 'little')
    pkt[4:6] = cmd_id.to_bytes(2, 'little')
    pkt[6:8] = len(data).to_bytes(2, 'little')
    pkt[8:8+len(data)] = data
    pkt[24:26] = (sum(pkt[:24]) & 0xFFFF).to_bytes(2, 'little')

    ser.write(pkt)

    resp = ser.read(26)
    if len(resp) != 26 or resp[0:2] != b'\xAA\x55':
        return 0xFFFF

    return int.from_bytes(resp[8:10], 'little')


print("Please place your finger on the sensor...")

# Vendor-style polling: GET_IMAGE until success
while True:
    ret = cmd(0x0020)     # CMD_GET_IMAGE
    if ret == 0x0000:
        print("Finger detected.")
        break
    time.sleep(0.25)

ser.close()
