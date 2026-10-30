#!/usr/bin/env python3
"""Self-contained fixture TUI for trying the skill, not a production UI."""
import os
import select
import sys
import termios
import tty


def display(selected, help_open):
    # Raw mode disables newline translation, so each line needs a carriage return.
    sys.stdout.write("\x1b[2J\x1b[H")
    if help_open:
        sys.stdout.write("\x1b[1;36mHelp\x1b[0m\r\n\r\n  Up/Down: choose item\r\n  ?: help\r\n  Escape: close help\r\n  q: quit\r\n")
    else:
        sys.stdout.write("\x1b[1;36mDashboard\x1b[0m\r\n\r\n")
        for idx, item in enumerate(["Overview", "Reports", "Settings"]):
            label = "> " if idx == selected else "  "
            sys.stdout.write(f"\x1b[{'7' if idx == selected else '0'}m{label}{item}\x1b[0m\r\n")
        sys.stdout.write(f"\r\nSelected: {['Overview', 'Reports', 'Settings'][selected]}\r\n")
        sys.stdout.write("Use Up/Down to navigate. Press ? for help; q to quit.\r\n")
    sys.stdout.flush()


def main():
    if not sys.stdin.isatty():
        raise SystemExit("Run this demo in an interactive terminal")
    saved = termios.tcgetattr(sys.stdin.fileno())
    selected, help_open = 0, False
    try:
        tty.setraw(sys.stdin.fileno())
        display(selected, help_open)
        while True:
            c = os.read(sys.stdin.fileno(), 1)
            if c in (b"q", b"\x03"):
                break
            if c == b"?":
                help_open = True
            elif c == b"\x1b":
                ready, _, _ = select.select([sys.stdin], [], [], 0.08)
                rest = os.read(sys.stdin.fileno(), 1) if ready else b""
                if rest == b"[":
                    key = os.read(sys.stdin.fileno(), 1)
                    if not help_open and key == b"B":
                        selected = min(2, selected + 1)
                    if not help_open and key == b"A":
                        selected = max(0, selected - 1)
                else:
                    help_open = False
            display(selected, help_open)
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved)
        sys.stdout.write("\x1b[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
