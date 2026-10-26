# GAME.md — Zombie Cannon (design doc)

A tiny roguelike shooter inspired by 向僵尸开炮. One screen, mouse only, ~3 minute runs.

## Core loop
1. Zombies walk down from the top of the screen.
2. The player stands near the bottom and shoots bullets upward **automatically** (no fire button).
3. The player drags left/right to dodge and aim.
4. Dead zombies drop XP gems; collecting gems fills an XP bar.
5. On level up: game pauses, show 3 random upgrade cards, tap one, resume.
6. At ~3 minutes one BOSS appears. Kill it = win. Player HP reaches 0 = lose.

## Win / lose
- **Win:** kill the boss (boss appears at 180 s).
- **Lose:** HP reaches 0. Zombies that reach the player line deal 10 damage and die.

## Controls
- **Desktop**: the cannon follows the mouse pointer left/right (no button needed).
- **Touch**: drag a finger; the cannon follows it.
- That is all. Shooting and picking up gems are automatic.

## Screen (390 × 700, portrait)
- Top: HP bar (left), timer (center), XP bar + level number (right).
- Field: zombies walking down, bullets going up, XP gems on the ground.
- Bottom: the player (cannon), moves only left/right.
- Overlays: start screen ("Tap to start"), upgrade choice (3 cards), win, lose (tap to restart).

## Zombies & boss (numbers)
| Item | Value |
|---|---|
| Zombie HP | 3 + (minute × 3) |
| Zombie speed | 60 px/s, +10 px/s per minute |
| Spawn rate | 1 every 1.5 s, −0.15 s per level (min 0.5 s) |
| Zombie damage to player | 10 |
| Player HP | 100 |
| XP to next level | 5 × level gems (each zombie = 1 gem) |
| Boss HP | 500, slow (40 px/s), spawns at 180 s |
| Bullet damage | base 2 |
| Fire rate | base 3 shots/s |

## Upgrades (pick 1 of 3 random, on level up)
1. **Double shot** — fire 2 bullets at once.
2. **Rapid fire** — fire rate +30%.
3. **Heavy bullets** — bullet damage +1.
4. **Piercing** — bullets pass through 1 more zombie.
5. **Wide barrel** — bullets spread in a fan (3 at ±10°, counts with Double shot).
6. **Medic** — heal 30 HP now.
7. **Magnet** — gems fly toward the player from farther away.
8. **Slow field** — zombies walk 15% slower (stacks up to 3 times).

## Build order (keep it small — target ~20 min of code)
1. Window, player follows mouse x, async main loop.
2. Bullets + auto fire; zombies spawn + walk down; bullet hits zombie.
3. XP gems + level-up pause + 3 cards (text-only cards are fine at first).
4. HP, zombie reaching the line, timer, boss, win/lose screens.
5. Art from assets/ replaces colored rectangles.

## Out of scope (do not build now)
Weapons other than the cannon, meta-currency, multiple maps, sound, pygbag upload.
