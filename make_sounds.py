# make_sounds.py - creates the short sound effects in sounds/ as .wav files
# Uses only the Python standard library. Run with:  python make_sounds.py
import wave
import math
import random
import struct
import os

SR = 22050  # samples per second
os.makedirs("sounds", exist_ok=True)


def save(name, samples):
    # write a list of numbers from -1.0 to 1.0 into a 16-bit mono wav file
    data = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
    with wave.open(os.path.join("sounds", name + ".wav"), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(data)
    print("sounds/" + name + ".wav")


def tone(freq, dur, vol=0.5, decay=6.0):
    # a pure note that fades out quickly
    out = []
    n = int(SR * dur)
    for i in range(n):
        t = i / SR
        out.append(vol * math.sin(2 * math.pi * freq * t) * math.exp(-decay * t))
    return out


def sweep(f1, f2, dur, vol=0.5, decay=12.0):
    # a note whose pitch slides from f1 down to f2 (classic laser "pew")
    out = []
    n = int(SR * dur)
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = f1 + (f2 - f1) * t
        phase += 2 * math.pi * freq / SR
        out.append(vol * math.sin(phase) * math.exp(-decay * (i / SR)))
    return out


def noise(dur, vol=0.4, decay=30.0):
    # short burst of random static, good for impacts
    out = []
    n = int(SR * dur)
    for i in range(n):
        t = i / SR
        out.append(vol * random.uniform(-1, 1) * math.exp(-decay * t))
    return out


def mix(a, b):
    # overlay two sounds (used for the hit: thump + crackle)
    out = []
    for i in range(max(len(a), len(b))):
        sa = a[i] if i < len(a) else 0.0
        sb = b[i] if i < len(b) else 0.0
        out.append(sa + sb)
    return out


# shooting: quick falling "pew"
save("shoot", sweep(880, 220, 0.07, vol=0.25))

# hit: small thump plus crackle
save("hit", mix(noise(0.06, vol=0.35), tone(140, 0.06, vol=0.4, decay=25)))

# level up: three rising happy notes
save("levelup", tone(523, 0.09, 0.4) + tone(659, 0.09, 0.4) + tone(784, 0.14, 0.45, decay=4))

# game over: three falling sad notes
save("gameover", tone(392, 0.18, 0.4, decay=4) + tone(311, 0.18, 0.4, decay=4)
     + tone(233, 0.35, 0.45, decay=3))

print("done - now run: python main.py")
