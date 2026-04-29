import os
import sys
from rich.console import Console
from rich.text import Text
from rich.align import Align
from themes import THEMES

console = Console()
cur_theme = "Cyberpunk"

def set_active_theme(name):
    global cur_theme
    cur_theme = name

def get_grad(i, length):
    theme = THEMES.get(cur_theme, THEMES["Cyberpunk"])
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
        "╚═════╝ ╚═╝   ╚═╝     ╚═══╝  ╚═╝     ╚═╝  ╚═══╝"
    ]
    tw = console.width
    for line in art:
        t = Text()
        display_line = line[:tw-2] if len(line) > tw else line
        for i, char in enumerate(display_line):
            t.append(char, style=f"bold {get_grad(i, len(display_line))}")
        console.print(Align.center(t))

def print_box(text):
    tw = console.width
    lines = text.strip().split('\n')
    max_l = max(len(line) for line in lines)
    w = min(max_l + 4, tw - 2)
    
    t_edge = Text("┌" + "─" * (w - 2) + "┐")
    for i in range(len(t_edge)): t_edge.stylize(f"bold {get_grad(i, len(t_edge))}", i, i+1)
    console.print(Align.center(t_edge))
    
    for line in lines:
        content = line[:w-4].ljust(w-4)
        l_side = Text("│", style=f"bold {get_grad(0, w)}")
        l_side.append(f" {content} ", style="white")
        l_side.append("│", style=f"bold {get_grad(w, w)}")
        console.print(Align.center(l_side))
        
    b_edge = Text("└" + "─" * (w - 2) + "┘")
    for i in range(len(b_edge)): b_edge.stylize(f"bold {get_grad(i, len(b_edge))}", i, i+1)
    console.print(Align.center(b_edge))

def print_btn(text):
    btn = Text(f"  {text}  ")
    res = Text()
    for i, char in enumerate(btn.plain):
        res.append(char, style=f"bold black on {get_grad(i, len(btn.plain))}")
    console.print(Align.center(res))

def input_c(prompt):
    try:
        console.print(Align.center(f"[bold {get_grad(0,10)}]{prompt}[/]"), end="")
        return input(" ")
    except KeyboardInterrupt:
        os._exit(0)

def pause():
    print_btn("Нажмите Enter...")
    try: input()
    except KeyboardInterrupt: os._exit(0)