import serial
import time

SERIAL_PORT = 'COM3'      # Change to your USB-TTL port, e.g. '/dev/ttyUSB0'
BAUD_RATE = 115200
DID = 0x01                # Usually 0x01, try 0x00 if no response

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
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

print("Press the finger")
while True:
    ret, _ = cmd(0x0021)            # Finger detect
    if ret == 0x0000:
        ret, _ = cmd(0x0020)        # Get image
        if ret == 0x0000:
            ret, _ = cmd(0x0060, b'\x00\x00')  # Generate template in buffer 0
            if ret == 0x0000:
                ret, data = cmd(0x0063, b'\x00\x00\x01\x00\x50\x00')  # Search ID 1-80
                if ret == 0x0000 and len(data) >= 2:
                    id_match = int.from_bytes(data[:2], 'little')
                    print(f"Finger matches stored ID: {id_match}")
                else:
                    print("No match")
            else:
                print("No match")
        #print("Press the finger")
    time.sleep(0.1)

ser.close()