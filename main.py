# Zombie Cannon - built from GAME.md
# Run with:  python main.py
import pygame
import asyncio
import random

W, H = 390, 700
FPS = 60

# colors
BLACK = (15, 15, 25)
WHITE = (240, 240, 240)
RED = (210, 60, 60)
GREEN = (70, 190, 90)
BLUE = (80, 140, 255)
YELLOW = (250, 210, 60)
GRAY = (90, 90, 110)

UPGRADES = [
    ("Double shot", "Fire 2 bullets at once"),
    ("Rapid fire", "Fire rate +30%"),
    ("Heavy bullets", "Bullet damage +1"),
    ("Piercing", "Bullets hit 1 more zombie"),
    ("Wide barrel", "Add 2 angled side bullets"),
    ("Medic", "Heal 30 HP now"),
    ("Magnet", "Gems fly to you from farther"),
    ("Slow field", "Zombies 15% slower (max 3)"),
]

ART = {}        # pictures, loaded once at startup
GROUND = None   # grass tiled to cover the whole screen
WALL_Y = H - 64  # y of the top edge of the crate wall


def load_assets():
    global ART, GROUND
    for name in ("player", "zombie", "robot", "boss", "crate"):
        ART[name] = pygame.image.load("assets/" + name + ".png").convert_alpha()
    grass = pygame.image.load("assets/grass.png").convert()
    GROUND = pygame.Surface((W, H))
    for y in range(0, H, 64):
        for x in range(0, W, 64):
            GROUND.blit(grass, (x, y))


def blit_center(screen, img, x, y):
    # draw a picture with its middle at (x, y)
    screen.blit(img, (x - img.get_width() / 2, y - img.get_height() / 2))


class Bullet:
    def __init__(self, x, y, dx, dy, dmg, pierce):
        self.x, self.y, self.dx, self.dy = x, y, dx, dy
        self.dmg = dmg
        self.pierce = pierce


class Zombie:
    def __init__(self, x, hp, speed, boss=False, kind="zombie"):
        self.x = x
        self.y = -40
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.boss = boss
        self.kind = kind  # "zombie" or "robot" (robot = fast but weaker)


class Gem:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Float:
    # a little text that floats upward and disappears (damage numbers)
    def __init__(self, x, y, text, color):
        self.x, self.y, self.text, self.color = x, y, text, color
        self.ttl = 0.7


SOUNDS = {}


def load_sounds():
    try:
        pygame.mixer.init()
    except pygame.error:
        return  # no sound device: the game still works silently
    for name in ("shoot", "hit", "levelup", "gameover"):
        SOUNDS[name] = pygame.mixer.Sound("sounds/" + name + ".wav")


def play(name):
    if name in SOUNDS:
        SOUNDS[name].play()


class Game:
    def __init__(self):
        self.state = "start"  # start, play, upgrade, win, lose
        self.reset()

    def reset(self):
        self.px = W // 2
        self.py = H - 70
        self.hp = 100
        self.time = 0.0
        self.bullets = []
        self.zombies = []
        self.gems = []
        self.fire_timer = 0.0
        self.spawn_timer = 0.0
        self.level = 1
        self.xp = 0
        self.cards = []
        self.has_double = False
        self.has_wide = False
        self.fire_rate = 3.0
        self.dmg = 2
        self.pierce = 0
        self.magnet_r = 60
        self.slow_stacks = 0
        self.boss_alive = False
        self.boss_spawned = False
        self.shake = 0.0
        self.floats = []

    def minute(self):
        return int(self.time // 60)

    def zombie_hp(self):
        return 3 + self.minute() * 3

    def zombie_speed(self):
        s = 60 + 10 * self.minute()
        return s * (0.85 ** self.slow_stacks)

    def spawn_gap(self):
        return max(0.5, 1.5 - 0.15 * (self.level - 1))

    def xp_needed(self):
        return 5 * self.level

    def start_upgrade(self):
        self.state = "upgrade"
        self.cards = random.sample(UPGRADES, 3)
        play("levelup")

    def apply_upgrade(self, name):
        if name == "Double shot":
            self.has_double = True
        elif name == "Rapid fire":
            self.fire_rate *= 1.3
        elif name == "Heavy bullets":
            self.dmg += 1
        elif name == "Piercing":
            self.pierce += 1
        elif name == "Wide barrel":
            self.has_wide = True
        elif name == "Medic":
            self.hp = min(100, self.hp + 30)
        elif name == "Magnet":
            self.magnet_r = 160
        elif name == "Slow field":
            self.slow_stacks = min(3, self.slow_stacks + 1)

    def shoot(self):
        speed = 500
        forward = [("straight", 0.0)]
        if self.has_wide:
            forward += [("angle", -0.18), ("angle", 0.18)]
        count = 2 if self.has_double else 1
        for kind, a in forward:
            for i in range(count):
                off = (i - (count - 1) / 2) * 14
                self.bullets.append(
                    Bullet(self.px + off, self.py - 20,
                           speed * a, -speed, self.dmg, self.pierce))
        play("shoot")

    def update(self, dt):
        self.time += dt

        # the cannon follows the mouse pointer (on a phone: follows the finger)
        mx = pygame.mouse.get_pos()[0]
        self.px = max(25, min(W - 25, mx))

        # auto fire
        self.fire_timer += dt
        if self.fire_timer >= 1 / self.fire_rate:
            self.fire_timer = 0
            self.shoot()

        # spawn zombies (stop normal spawns when boss is out)
        if not self.boss_spawned:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_gap():
                self.spawn_timer = 0
                kind = "robot" if random.random() < 0.25 else "zombie"
                hp = self.zombie_hp()
                speed = self.zombie_speed()
                if kind == "robot":
                    hp = max(1, int(hp * 0.7))
                    speed *= 1.3
                self.zombies.append(
                    Zombie(random.randint(30, W - 30), hp, speed, kind=kind))
            if self.time >= 180:
                self.boss_spawned = True
                self.boss_alive = True
                self.zombies.append(Zombie(W // 2, 500, 40, boss=True))

        # bullets
        for b in self.bullets:
            b.x += b.dx * dt
            b.y += b.dy * dt
        self.bullets = [b for b in self.bullets if b.y > -10 and 0 < b.x < W]

        # zombies walk down
        player_line = self.py - 10
        for z in self.zombies:
            z.y += z.speed * dt
            if z.y >= player_line:
                z.dead = True
                dmg = 30 if z.boss else 10
                self.hp -= dmg
                self.shake = 0.25  # small screen shake when the wall is hit
                self.floats.append(Float(z.x, player_line - 30, f"-{dmg}", RED))
                if self.hp <= 0:
                    self.state = "lose"
                    play("gameover")
        self.zombies = [z for z in self.zombies if not getattr(z, "dead", False)]

        # bullet vs zombie
        for b in self.bullets:
            for z in self.zombies:
                r = 45 if z.boss else 18
                if abs(b.x - z.x) < r and abs(b.y - z.y) < r:
                    z.hp -= b.dmg
                    self.floats.append(Float(z.x, z.y - r, str(b.dmg), YELLOW))
                    play("hit")
                    b.pierce -= 1
                    if b.pierce < 0:
                        b.dead = True
                    if z.hp <= 0 and not getattr(z, "dead", False):
                        z.dead = True
                        if z.boss:
                            self.boss_alive = False
                            self.state = "win"
                            play("levelup")  # happy sound for the win too
                        else:
                            self.gems.append(Gem(z.x, z.y))
                    if getattr(b, "dead", False):
                        break
        self.bullets = [b for b in self.bullets if not getattr(b, "dead", False)]
        self.zombies = [z for z in self.zombies if not getattr(z, "dead", False)]

        # gems: float down slowly, fly to player inside magnet radius
        for g in self.gems:
            g.y += 40 * dt
            dx, dy = self.px - g.x, self.py - g.y
            if dx * dx + dy * dy < self.magnet_r ** 2:
                dist = max(1, (dx * dx + dy * dy) ** 0.5)
                g.x += dx / dist * 300 * dt
                g.y += dy / dist * 300 * dt
            if abs(dx) < 20 and abs(dy) < 20:
                g.dead = True
                self.xp += 1
                if self.xp >= self.xp_needed():
                    self.xp -= self.xp_needed()
                    self.level += 1
                    self.start_upgrade()
            elif g.y > H + 20:
                g.dead = True
        self.gems = [g for g in self.gems if not getattr(g, "dead", False)]

        # shake and floating numbers
        self.shake = max(0.0, self.shake - dt)
        for f in self.floats:
            f.y -= 50 * dt
            f.ttl -= dt
        self.floats = [f for f in self.floats if f.ttl > 0]

    def draw(self, screen, fonts):
        font, big = fonts
        screen.blit(GROUND, (0, 0))
        if self.state == "start":
            panel = pygame.Surface((W, 200))
            panel.set_alpha(180)
            panel.fill(BLACK)
            screen.blit(panel, (0, 200))
            screen.blit(big.render("ZOMBIE CANNON", True, YELLOW),
                        (W // 2 - big.size("ZOMBIE CANNON")[0] // 2, 220))
            screen.blit(font.render("Move the mouse (or finger) to aim.", True, WHITE),
                        (30, 290))
            screen.blit(font.render("Tap to start", True, GREEN), (150, 340))
            return

        # field
        for z in self.zombies:
            r = 45 if z.boss else 18
            img = ART["boss"] if z.boss else ART[z.kind]
            blit_center(screen, img, z.x, z.y)
            pygame.draw.rect(screen, BLACK, (z.x - r, z.y - r - 10, r * 2, 4))
            pygame.draw.rect(screen, RED,
                             (z.x - r, z.y - r - 10, int(r * 2 * z.hp / z.max_hp), 4))
        for b in self.bullets:
            pygame.draw.circle(screen, YELLOW, (int(b.x), int(b.y)), 4)
        for g in self.gems:
            pygame.draw.rect(screen, BLUE, (g.x - 5, g.y - 5, 10, 10))
        for f in self.floats:
            txt = font.render(f.text, True, f.color)
            screen.blit(txt, (f.x - txt.get_width() / 2, f.y))

        # crate wall the zombies must not reach
        for x in range(0, W, 64):
            screen.blit(ART["crate"], (x, WALL_Y))

        # player (cannon on the wall)
        blit_center(screen, ART["player"], self.px, self.py)

        # top bars: HP, timer, XP
        pygame.draw.rect(screen, (60, 20, 20), (10, 10, 120, 12))
        pygame.draw.rect(screen, RED, (10, 10, int(120 * self.hp / 100), 12))
        m, s = divmod(int(180 - self.time), 60)
        if self.boss_spawned:
            t_text = "BOSS!"
        else:
            t_text = f"{m}:{s:02d}"
        screen.blit(font.render(t_text, True, WHITE), (W // 2 - 15, 8))
        pygame.draw.rect(screen, (20, 30, 70), (W - 130, 10, 120, 12))
        pygame.draw.rect(screen, BLUE,
                         (W - 130, 10, int(120 * self.xp / self.xp_needed()), 12))
        screen.blit(font.render(f"Lv {self.level}", True, WHITE), (W - 130, 26))

        if self.state == "upgrade":
            overlay = pygame.Surface((W, H))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            screen.blit(big.render("LEVEL UP!", True, YELLOW), (100, 150))
            screen.blit(font.render("Tap a card to choose:", True, WHITE), (120, 200))
            for i, (name, desc) in enumerate(self.cards):
                rect = pygame.Rect(30, 240 + i * 110, W - 60, 90)
                pygame.draw.rect(screen, GRAY, rect, border_radius=10)
                screen.blit(font.render(name, True, YELLOW), (rect.x + 15, rect.y + 15))
                screen.blit(font.render(desc, True, WHITE), (rect.x + 15, rect.y + 45))
        elif self.state in ("win", "lose"):
            text = "YOU WIN!" if self.state == "win" else "GAME OVER"
            color = GREEN if self.state == "win" else RED
            screen.blit(big.render(text, True, color),
                        (W // 2 - big.size(text)[0] // 2, 300))
            screen.blit(font.render("Tap to play again", True, WHITE), (130, 360))

    def card_rects(self):
        return [pygame.Rect(30, 240 + i * 110, W - 60, 90) for i in range(3)]


async def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Zombie Cannon")
    load_assets()
    load_sounds()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 26)
    big = pygame.font.SysFont(None, 44)
    canvas = pygame.Surface((W, H))  # we draw here, then move it for the shake
    game = Game()

    while True:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "start":
                    game.state = "play"
                elif game.state in ("win", "lose"):
                    game.reset()
                    game.state = "play"
                elif game.state == "upgrade":
                    for i, rect in enumerate(game.card_rects()):
                        if rect.collidepoint(event.pos):
                            game.apply_upgrade(game.cards[i][0])
                            game.state = "play"
        if game.state == "play":
            game.update(dt)
        game.draw(canvas, (font, big))
        # screen shake: move the whole picture a few pixels while shake > 0
        ox = oy = 0
        if game.shake > 0:
            ox = random.randint(-4, 4)
            oy = random.randint(-4, 4)
        screen.fill(BLACK)
        screen.blit(canvas, (ox, oy))
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
