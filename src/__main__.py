# 018 - Conways Game of Life
# by Ivan Reshetnikov at https://ivan-reshetnikov.dev, contact at contact@ivan-reshetnikov.dev
# 
# License:
#   This code is released under the MIT License.
#   You are free to use, modify, and distribute this code
#   for personal or commercial purposes, provided that
#   this notice is included in any copies or substantial portions
#   of the software.
#
# Warranty Notice:
#   This software is provided "AS IS", without warranty of any kind,
#   express or implied, including but not limited to the warranties
#   of merchantability, fitness for a particular purpose, and
#   noninfringement. In no event shall the author be liable for any
#   claim, damages, or other liability arising from the use of this software.
# 
# Notes:
#   global-keyword hell, brace your eyes

import os     # Provides: system
import sys    # Provides: stdout
import time   # Provides: sleep
import random # Provides: randint


framebuffer_w: int = 0
framebuffer_h: int = 0
framebuffer: list[bool] = []
staging_framebuffer: list[bool] = []

SEC_TO_MS: float = 1000.0
MS_TO_SEC: float = 0.001
REFRESH_RATE_SEC: float = 128.0 * MS_TO_SEC # ~15 FPS

seed: int = 0
deaths: int = 0
births: int = 0


def term_clear() -> None:
    # TODO: UNIX shell support
    match os.name:
        case "nt": os.system("cls")
        case "posix": os.system("cls")


def term_set_cursor(x: int, y: int) -> None:
    # SEE: ANSI ESC - H
    sys.stdout.write(f"\033[{y+1};{x+1}H")


def set_viewport(w: int, h: int) -> None:
    global framebuffer_w
    global framebuffer_h
    global framebuffer

    term_clear()
    framebuffer_w = w
    framebuffer_h = h

    # Popuplate with 0s
    framebuffer = [False for _ in range(framebuffer_w * framebuffer_h)]
    staging_framebuffer = framebuffer.copy()


def framebuffer_indx(x: int, y: int) -> int:
    global framebuffer_w

    return y * framebuffer_w + x


def framebuffer_get(x: int, y: int) -> bool:
    global framebuffer_w
    global framebuffer_h
    global framebuffer

    # Bounds check
    if x < 0 or x >= framebuffer_w: return False
    if y < 0 or y >= framebuffer_h: return False

    return framebuffer[framebuffer_indx(x, y)]


def framebuffer_set(x: int, y: int, val: bool) -> None:
    global framebuffer_w
    global framebuffer_h
    global framebuffer

    # Bounds check
    if x < 0 or x >= framebuffer_w: return
    if y < 0 or y >= framebuffer_h: return
    
    framebuffer[framebuffer_indx(x, y)] = val


def update() -> None:
    global framebuffer_w, framebuffer_h, framebuffer
    global deaths, births

    staging_framebuffer = framebuffer.copy()

    for y in range(framebuffer_h):
        for x in range(framebuffer_w):
            alive = framebuffer_get(x, y)
            count = sum([
                framebuffer_get(x + dx, y + dy)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if not (dx == 0 and dy == 0) # NOTE(Ivan 25/09/25): Maybe not waste cycles sampling origin twice by unrolling the loop?
            ])

            # NOTE(Ivan 25/09/25): Not using helper function to not waste cycles on bounds checking.
            if alive:
                if count < 2 or count > 3:
                    staging_framebuffer[framebuffer_indx(x, y)] = False
                    deaths += 1
            else:
                if count == 3:
                    staging_framebuffer[framebuffer_indx(x, y)] = True
                    births += 1

    framebuffer[:] = staging_framebuffer


def draw() -> None:
    global framebuffer_w
    global framebuffer_h

    for y in range(framebuffer_h):
        for x in range(framebuffer_w):
            sys.stdout.write("██" if framebuffer_get(x, y) else "  ")
        sys.stdout.write("\n")
    
    # NOTE(Ivan 25/09/25): Windows Terminal as of today does not care about flushing, we'll get tearing and performance hit.
    sys.stdout.flush()


def main() -> None:
    global framebuffer_w
    global framebuffer_h
    global framebuffer
    global seed
    global deaths
    global births

    set_viewport(64, 64)

    seed = random.randint(0, 999999)

    # Populate
    random.seed(seed)
    for y in range(framebuffer_h):
        for x in range(framebuffer_w):
            framebuffer_set(x, y, random.randint(0, 1))

    # Main loop
    while True:
        update()
        term_set_cursor(0, 0)
        draw()
        term_set_cursor(framebuffer_w*2, 0)
        sys.stdout.write(f"Seed: {seed}")
        term_set_cursor(framebuffer_w*2, 1)
        sys.stdout.write(f"Deaths: {deaths}")
        term_set_cursor(framebuffer_w*2, 2)
        sys.stdout.write(f"Births: {births}")

        time.sleep(REFRESH_RATE_SEC)


if __name__ == "__main__":
    main()
