import serial
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 115200
DID = 0x01

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(0.3)

def checksum(buf):
    return sum(buf) & 0xFFFF

def cmd(cmd_id):
    pkt = bytearray(26)
    pkt[0:2] = b'\x55\xAA'
    pkt[2] = DID
    pkt[3] = 0x00
    pkt[4:6] = cmd_id.to_bytes(2, 'little')
    pkt[6:8] = (0).to_bytes(2, 'little')
    pkt[24:26] = checksum(pkt[:24]).to_bytes(2, 'little')

    ser.write(pkt)

    # ACK frame
    ack = ser.read(26)
    if len(ack) != 26 or ack[0:2] != b'\xAA\x55':
        return None

    if int.from_bytes(ack[8:10], 'little') != 0:
        return None

    # DATA frame
    time.sleep(0.07)
    hdr = ser.read(8)
    if len(hdr) != 8 or hdr[0:2] != b'\xA5\x5A':
        return None

    data_len = int.from_bytes(hdr[6:8], 'little')
    data = ser.read(data_len + 2)

    return data[:data_len]

# ---- Execute ----
payload = cmd(0x0049)

if payload is None or len(payload) < 4:
    print("Failed to get ID list")
else:
    enroll_count = int.from_bytes(payload[0:2], 'little')
    bitmap = payload[2:]

    enrolled_ids = []
    for byte_index, b in enumerate(bitmap):
        for bit in range(8):
            if b & (1 << bit):
                enrolled_ids.append(byte_index * 8 + bit)

    print(f"Enroll Count = {enroll_count}")
    print("ID =")
    for i in enrolled_ids:
        print(i)

ser.close()
