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
    return ret, b''

print("Deleting ALL stored fingerprints from the module...")

# Correct data for delete all: startID=1 (0x01 0x00), endID=80 (0x50 0x00)
del_all_data = b'\x01\x00\x50\x00'

ret, _ = cmd(0x0044, del_all_data)

if ret == 0x0000:
    print("All fingerprints deleted successfully!")
elif ret == 0x0012:
    print("No fingerprints were stored (module already empty)")
else:
    print(f"Delete all failed (error code: 0x{ret:04X})")

ser.close()