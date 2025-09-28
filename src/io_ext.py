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

import sys
import os


rawin = None

KEY_ESC: str = "\x1b"


if os.name == "nt":
    import msvcrt

    class RawInput:
        def read_key(self) -> str:
            ch = msvcrt.getch()
            
            # Handle special keys (arrows, function keys) which start with 0xe0 or 0x00
            if ch in {b'\x00', b'\xe0'}:
                # Consume the second byte and ignore it for simplicity
                # We could map these special keys to uinque names later, i.e. <UP> <ESC> <F1> <RETURN>

                cmd = msvcrt.getch()
                print(cmd)
                return ""
            try:
                return ch.decode("utf-8")
            except UnicodeDecodeError:
                return ""
        
        def has_key(self) -> bool:
            return msvcrt.kbhit()

    rawin = RawInput()

elif os.name == "posix":
    import tty
    import termios
    import select

    class RawInput:
        def __init__(self):
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)

        def __enter__(self):
            # Class getting registered
            # Switch STDIN to raw mode

            tty.setraw(self.fd)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Class getting deregistered
            # Restore original terminal settings, from STDIN being in raw-mode 

            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

        def read_key(self) -> str:
            # Return next character byte as unicode string
            # NOTE(Ivan 25/09/28): What to do with special keys, like in Windows implementation?
            ch = os.read(self.fd, 1)
            try:
                return ch.decode("utf-8")
            except UnicodeDecodeError:
                return ""
        
        def has_key(self) -> bool:
            dr, _, _ = select.select([self.fd], [], [], 0)
            return bool(dr)

    rawin = RawInput()
