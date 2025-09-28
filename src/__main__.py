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

import os     # Provides: system
import sys    # Provides: stdout
import time   # Provides: sleep
import random # Provides: randint

import io_ext


viewport_w: int = 0
viewport_h: int = 0
viewport: list[bool] = []
staging_viewport: list[bool] = []

SEC_TO_MS: float = 1000.0
MS_TO_SEC: float = 0.001
FRAME_DELAY_SEC: float = 64.0 * MS_TO_SEC # ~30 FPS

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
    global viewport_w
    global viewport_h
    global viewport
    global staging_viewport

    term_clear()
    viewport_w = w
    viewport_h = h

    # Popuplate with 0s
    viewport = [False for _ in range(viewport_w * viewport_h)]
    staging_viewport = viewport.copy()


def viewport_indx(x: int, y: int) -> int:
    return y * viewport_w + x


def viewport_get(x: int, y: int) -> bool:
    global viewport

    # Bounds check
    if x < 0 or x >= viewport_w: return False
    if y < 0 or y >= viewport_h: return False

    return viewport[viewport_indx(x, y)]


def viewport_set(x: int, y: int, val: bool) -> None:
    global viewport

    # Bounds check
    if x < 0 or x >= viewport_w: return
    if y < 0 or y >= viewport_h: return
    
    viewport[viewport_indx(x, y)] = val


def update() -> None:
    global viewport
    global deaths
    global births

    staging_viewport = viewport.copy()

    for y in range(viewport_h):
        for x in range(viewport_w):
            alive = viewport_get(x, y)
            count = sum([
                viewport_get(x + dx, y + dy)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if not (dx == 0 and dy == 0) # NOTE(Ivan 25/09/25): Maybe not waste cycles sampling origin twice by unrolling the loop?
            ])

            # NOTE(Ivan 25/09/25): Not using helper function to not waste cycles on bounds checking.
            if alive:
                if count < 2 or count > 3:
                    staging_viewport[viewport_indx(x, y)] = False
                    deaths += 1
            else:
                if count == 3:
                    staging_viewport[viewport_indx(x, y)] = True
                    births += 1

    viewport[:] = staging_viewport


def draw_viewport() -> None:
    # NOTE(Ivan 25/09/28): Language's stdout flushing policy of forcing buffered flushing when reaching a size limit,
    # leads to tearing (Flushing of a partial frame) and a negative performance impact.
    # We will push the output frame to our own buffer and flush it with one call.
    framebuffer: str = ""

    for y in range(viewport_h):
        for x in range(viewport_w):
            framebuffer += "██" if viewport_get(x, y) else "  "
        framebuffer += "\n"
    
    term_set_cursor(0, 0)
    sys.stdout.write(framebuffer)
    sys.stdout.flush()


def main() -> None:
    set_viewport(64, 64)

    # Populate
    seed = random.randint(0, 999999)

    random.seed(seed)
    for y in range(viewport_h):
        for x in range(viewport_w):
            viewport_set(x, y, random.randint(0, 1))

    # Main loop
    while True:
        update()
        draw_viewport()
        term_set_cursor(viewport_w*2, 0)
        sys.stdout.write(f"Seed: {seed}")
        term_set_cursor(viewport_w*2, 1)
        sys.stdout.write(f"Deaths: {deaths}")
        term_set_cursor(viewport_w*2, 2)
        sys.stdout.write(f"Births: {births}")

        term_set_cursor(viewport_w*2, 4)
        sys.stdout.write("Press [ESC] to exit")

        term_set_cursor(0, viewport_h)
        if io_ext.rawin.has_key():
            key: str = io_ext.rawin.read_key()
            match key:
                case io_ext.KEY_ESC:
                    break

        time.sleep(FRAME_DELAY_SEC)


if __name__ == "__main__":
    main()
