import os
import sys
from rich.console import Console
from rich.text import Text
from rich.align import Align
from themes import THEMES

console = Console()
cur_theme = "Claude"

def set_active_theme(name):
    global cur_theme
    cur_theme = name if name in THEMES else "Cyberpunk"

def get_grad(i, length):
    theme = THEMES[cur_theme] if cur_theme in THEMES else THEMES["Claude"]
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
    tw = console.width
    for line in art:
        t = Text()
        display_line = line[:tw-4]
        for i, char in enumerate(display_line):
            t.append(char, style=f"bold {get_grad(i, len(display_line))}")
        console.print(Align.center(t))

def print_box(text):
    tw = console.width
    lines = str(text).strip().split('\n')
    max_l = max(len(line) for line in lines)
    w = min(max_l + 6, tw - 4)
    if w < 10: w = 10
    
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

def input_c(prompt):
    try:
        prompt_text = Text(str(prompt) + " ", style="bold white")
        console.print(Align.center(prompt_text), end="")
        return input().strip()
    except:
        os._exit(0)