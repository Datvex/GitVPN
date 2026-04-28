import os
from rich.console import Console
from rich.text import Text
from rich.align import Align
from rich.markup import escape

console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_grad(i, length):
    rel = i / (length - 1) if length > 1 else 0
    if rel < 0.5:
        r, g, b = 255, int(255 - 40 * (rel * 2)), 0
    else:
        r, g, b = int(255 - 116 * ((rel - 0.5) * 2)), int(215 - 146 * ((rel - 0.5) * 2)), int(19 * ((rel - 0.5) * 2))
    return f"rgb({r},{g},{b})"

def print_banner():
    art = [
        "██████╗ ██╗████████╗██╗   ██╗██████╗ ███╗   ██╗",
        "██╔════╝ ██║╚══██╔══╝██║   ██║██╔══██╗████╗  ██║",
        "██║  ███╗██║   ██║   ██║   ██║██████╔╝██╔██╗ ██║",
        "██║   ██║██║   ██║   ╚██╗ ██╔╝██╔═══╝ ██║╚██╗██║",
        "╚██████╔╝██║   ██║    ╚████╔╝ ██║     ██║ ╚████║",
        "╚═════╝ ╚═╝   ╚═╝     ╚═══╝  ╚═╝     ╚═╝  ╚═══╝"
    ]
    for line in art:
        t = Text()
        for i, char in enumerate(line):
            t.append(char, style=f"bold {get_grad(i, len(line))}")
        console.print(Align.center(t))

def print_box(text):
    lines = text.strip().split('\n')
    w = max(len(line) for line in lines) + 4
    t_edge = Text("┌" + "─" * (w - 2) + "┐")
    for i in range(len(t_edge)): t_edge.stylize(f"bold {get_grad(i, len(t_edge))}", i, i+1)
    console.print(Align.center(t_edge))
    for line in lines:
        l_side = Text("│", style=f"bold {get_grad(0, w)}")
        l_side.append(f" {line.ljust(w-4)} ", style="white")
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
    console.print(Align.center(f"[bold rgb(255,215,0)]{prompt}[/]"), end="")
    return input(" ")

def pause():
    print_btn("Нажмите Enter...")
    input()