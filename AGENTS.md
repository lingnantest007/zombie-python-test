# Python game — project rules (CDT501 Lecture 9)

## What this project is
A small game for beginners, written in Python with pygame-ce.
It runs with `python main.py` on a laptop. The window is portrait, 390 x 700 px,
like a phone. Later we will also put it on the web with pygbag.

## Rules for the agent
- Main code in one file: main.py. Use pygame-ce (`import pygame`). The main loop must be
  `async def main()` with `await asyncio.sleep(0)` once per frame, so pygbag can run it in a browser.
- No other libraries, except Pillow for image work. Ask before installing anything else.
- It must work with the mouse only (and a finger on a touch screen).
- Pictures live in assets/. Never change, move or delete anything in raw_art/.
- After every change, tell me how to check it.
- Explain what you did in simple English: I am learning to program.
- Do not run git commit unless I ask you to.
