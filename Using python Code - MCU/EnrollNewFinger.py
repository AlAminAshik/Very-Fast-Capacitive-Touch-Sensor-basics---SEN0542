import serial
import time

# ================= CONFIG =================
PORT = 'COM3'
BAUD = 115200
DID  = 0x00
# =========================================

ser = serial.Serial(PORT, BAUD, timeout=2)
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
        return 0xFFFF, b''

    ret = int.from_bytes(resp[8:10], 'little')
    ln  = int.from_bytes(resp[6:8], 'little') - 2
    return ret, resp[10:10+ln] if ln > 0 else b''


def wait_finger_present():
    while True:
        if cmd(0x0020)[0] == 0x0000:
            return
        time.sleep(0.2)


def wait_finger_removed():
    while True:
        if cmd(0x0021)[0] == 0x0000:
            break
        time.sleep(0.2)

    while cmd(0x0020)[0] == 0x0000:
        time.sleep(0.2)

    time.sleep(0.6)


# ================= ENROLL =================
fid = int(input("Enter fingerprint ID (1–80): "))
print(f"\nEnrolling ID {fid}")

# Start enrollment
cmd(0x0046, fid.to_bytes(2, 'little'))

# -------- First finger --------
print("Place finger (1/3)...")
wait_finger_present()

if cmd(0x0060, b'\x00\x00')[0] != 0x0000:
    print("First template failed")
    exit()

print("Lift finger")
wait_finger_removed()

# -------- Second finger --------
print("Place same finger (2/3)...")
wait_finger_present()

if cmd(0x0060, b'\x01\x00')[0] != 0x0000:
    print("Second template failed")
    exit()

print("Lift finger")
wait_finger_removed()

# -------- Third finger --------
print("Place same finger (3/3)...")
wait_finger_present()

if cmd(0x0060, b'\x02\x00')[0] != 0x0000:
    print("Third template failed")
    exit()

print("Lift finger")
wait_finger_removed()

# -------- Merge (3 templates) --------
if cmd(0x0061, b'\x00\x00\x03\x00')[0] != 0x0000:
    print("Template merge failed")
    exit()

# -------- Store --------
if cmd(0x0040, fid.to_bytes(2, 'little') + b'\x00\x00')[0] != 0x0000:
    print("Store failed")
    exit()

# -------- End --------
cmd(0x0024, b'\x00\x00')

print("Enrollment successful (3-scan)")
ser.close()
