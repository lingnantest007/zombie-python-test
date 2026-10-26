# make_assets.py - turns raw_art/ pictures into the files the game uses in assets/
# Run with:  python make_assets.py
# raw_art/ is never changed; we only read from it.
from PIL import Image
import os

os.makedirs("assets", exist_ok=True)


def load(name):
    # open a picture from raw_art/ and make sure it has alpha (transparency)
    return Image.open(os.path.join("raw_art", name + ".png")).convert("RGBA")


# 1. Player faces right in the raw art. Turning it 90 degrees anticlockwise
#    makes it face up (that is the direction it shoots).
player = load("player").rotate(90, expand=True)
player.save("assets/player.png")
print("assets/player.png", player.size, "faces up")

# 2. Zombie and robot also face right. Turning them 90 degrees clockwise
#    makes them face down (that is the direction they walk).
zombie = load("zombie").rotate(-90, expand=True)
zombie.save("assets/zombie.png")
print("assets/zombie.png", zombie.size, "faces down")

robot = load("robot").rotate(-90, expand=True)
robot.save("assets/robot.png")
print("assets/robot.png", robot.size, "faces down")

# 3. Boss: the down-facing zombie, twice as big, with a red tint.
#    We split the image into red/green/blue/alpha and change only the colors,
#    so the transparent background stays transparent.
boss = zombie.resize((zombie.width * 2, zombie.height * 2), Image.LANCZOS)
r, g, b, a = boss.split()
r = r.point(lambda v: min(255, v + 90))   # more red
g = g.point(lambda v: v // 2)             # less green
b = b.point(lambda v: v // 2)             # less blue
boss = Image.merge("RGBA", (r, g, b, a))
boss.save("assets/boss.png")
print("assets/boss.png", boss.size, "big red zombie")

# 4. Ground and wall tiles are already seen from above, so we just copy them.
Image.open("raw_art/grass.png").save("assets/grass.png")
crate = load("crate")
crate.save("assets/crate.png")
print("assets/grass.png and assets/crate.png copied")

print("done - now run: python main.py")
