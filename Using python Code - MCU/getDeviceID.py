import serial
import time

PORT = 'COM3'
BAUD = 115200
DID  = 0x00

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
        return None

    return resp

print("Device Information\n")

# ---- Device ID ----
resp = cmd(0x0024)
if resp:
    print(f"Device ID Success           ID : {resp[8]}")
else:
    print("Device ID Failed")

ser.close()
