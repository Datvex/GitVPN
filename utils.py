import os
import sys
import subprocess
from rich.console import Console
from rich.text import Text
from rich.align import Align
from themes import THEMES

console = Console()
cur_theme = "Claude"

def set_active_theme(name):
    global cur_theme
    cur_theme = name if name in THEMES else "Claude"

def get_grad(i, length):
    if cur_theme in THEMES:
        theme = THEMES[cur_theme]
    else:
        theme = THEMES["Claude"]
    p, s = theme["p"], theme["s"]
    rel = i / (length - 1) if length > 1 else 0
    r = int(p[0] + (s[0] - p[0]) * rel)
    g = int(p[1] + (s[1] - p[1]) * rel)
    b = int(p[2] + (s[2] - p[2]) * rel)
    return f"rgb({r},{g},{b})"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    art = [
        "██████╗ ██╗████████╗██╗   ██╗██████╗ ███╗   ██╗",
        "██╔════╝ ██║╚══██╔══╝██║   ██║██╔══██╗████╗  ██║",
        "██║  ███╗██║   ██║   ██║   ██║██████╔╝██╔██╗ ██║",
        "██║   ██║██║   ██║   ╚██╗ ██╔╝██╔═══╝ ██║╚██╗██║",
        "╚██████╔╝██║   ██║    ╚████╔╝ ██║     ██║ ╚████║",
        " ╚═════╝ ╚═╝   ╚═╝     ╚═══╝  ╚═╝     ╚═╝  ╚═══╝"
    ]
    tw = max(console.width, 20)
    for line in art:
        t = Text()
        display_line = line[:tw-4]
        for i, char in enumerate(display_line):
            t.append(char, style=f"bold {get_grad(i, len(display_line))}")
        console.print(Align.center(t))

def print_box(text):
    tw = max(console.width, 20)
    lines = str(text).strip().split('\n')
    max_l = max(len(line) for line in lines)
    w = max(min(max_l + 6, tw - 4), 15)
    
    t_edge = Text("┌" + "─" * (w - 2) + "┐")
    for i in range(len(t_edge)):
        t_edge.stylize(f"bold {get_grad(i, len(t_edge))}", i, i+1)
    console.print(Align.center(t_edge))
    
    for line in lines:
        content = line[:w-4].ljust(w-4)
        l_side = Text("│", style=f"bold {get_grad(0, w)}")
        l_side.append(f" {content} ", style="white")
        l_side.append("│", style=f"bold {get_grad(w-1, w)}")
        console.print(Align.center(l_side))
        
    b_edge = Text("└" + "─" * (w - 2) + "┘")
    for i in range(len(b_edge)):
        b_edge.stylize(f"bold {get_grad(i, len(b_edge))}", i, i+1)
    console.print(Align.center(b_edge))

def print_btn(text):
    btn = Text(f"  {text}  ")
    res = Text()
    for i, char in enumerate(btn.plain):
        res.append(char, style=f"bold white on {get_grad(i, len(btn.plain))}")
    console.print(Align.center(res))

def copy_to_clipboard(text):
    try:
        if os.name == 'nt':
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
            p.communicate(text.encode('utf-8'))
            return True
        elif sys.platform == 'darwin':
            p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            p.communicate(text.encode('utf-8'))
            return True
        else:
            for cmd in (['xclip', '-selection', 'clipboard'],
                        ['xsel', '--clipboard', '--input'],
                        ['wl-copy']):
                try:
                    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                    p.communicate(text.encode('utf-8'))
                    return True
                except FileNotFoundError:
                    continue
            return False
    except Exception:
        return False

def input_c(prompt):
    try:
        console.print("  ❯ ", end="", style=f"bold {get_grad(0, 10)}")
        sys.stdout.flush()

        try:
            if os.name == 'nt':
                import msvcrt
                ch = msvcrt.getwch()
                if ch == '\x1b':
                    return "ESC"
                if ch in ('\x00', '\xe0'):
                    msvcrt.getwch()
                    return ""
                if ch in ('\r', '\n'):
                    print()
                    return ""
                sys.stdout.write(ch)
                sys.stdout.flush()
                rest = input()
                return ch + rest
            else:
                import tty, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    return input().strip()
                if ch == '\x1b':
                    print()
                    return "ESC"
                if ch in ('\r', '\n'):
                    print()
                    return ""
                sys.stdout.write(ch)
                sys.stdout.flush()
                rest = input()
                return ch + rest
        except Exception:
            return input().strip()
    except (EOFError, KeyboardInterrupt):
        os._exit(0)

def print_progress(text):
    tw = max(console.width, 20)
    s = str(text)
    pad = max(0, (tw - len(s)) // 2)
    sys.stdout.write("\r" + " " * pad + s + " " * 10)
    sys.stdout.flush()