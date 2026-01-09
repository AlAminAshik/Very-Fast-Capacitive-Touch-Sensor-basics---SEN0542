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

# Prompt for ID to delete
try:
    fid = int(input("Enter the fingerprint ID to delete (1-80): "))
    if not 1 <= fid <= 80:
        print("ID must be between 1 and 80")
        ser.close()
        exit()
except:
    print("Invalid input")
    ser.close()
    exit()

print(f"Attempting to delete single fingerprint ID: {fid}")

# Correct way to delete a single specific ID
del_data = fid.to_bytes(2, 'little') + fid.to_bytes(2, 'little')  # startID = fid, endID = fid

ret, _ = cmd(0x0044, del_data)

if ret == 0x0000:
    print(f"Successfully deleted ID {fid}")
elif ret == 0x0012:
    print(f"Delete returned 0x0012: No fingerprint stored at ID {fid} (template empty)")
else:
    print(f"Delete failed (error code: 0x{ret:04X})")

ser.close()