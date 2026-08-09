import atexit
import base64
import os
import shutil
import subprocess
import sys
import textwrap
import time
import unicodedata

C_BLUE = "\033[38;2;0;175;255m"
C_YELLOW = "\033[38;2;248;246;117m"
C_GRAY = "\033[38;2;110;110;110m"
C_WHITE = "\033[38;2;210;210;210m"
C_DARK_GRAY = "\033[38;2;80;80;80m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"
C_BG_INPUT = "\033[48;2;45;45;45m"
C_LOGO = "\033[38;2;248;246;117m"
C_LOGO_SHADOW = "\033[38;2;90;90;40m"

COLOR_NORMAL = {
    "blue": "\033[38;2;0;175;255m",
    "yellow": "\033[38;2;248;246;117m",
    "gray": "\033[38;2;110;110;110m",
    "white": "\033[38;2;210;210;210m",
    "dark_gray": "\033[38;2;80;80;80m",
    "bold": "\033[1m",
    "bg_input": "\033[48;2;45;45;45m",
}

COLOR_DIM = {
    "blue": "\033[38;2;0;65;95m",
    "yellow": "\033[38;2;95;94;45m",
    "gray": "\033[38;2;42;42;42m",
    "white": "\033[38;2;78;78;78m",
    "dark_gray": "\033[38;2;28;28;28m",
    "bold": "",
    "bg_input": "\033[48;2;22;22;22m",
}

old_mode_in = None
old_mode_out = None
win32_available = False
win_mouse_left_down = False
_input_queue = []

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32

    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    ENABLE_WINDOW_INPUT = 0x0008
    ENABLE_MOUSE_INPUT = 0x0010
    ENABLE_QUICK_EDIT_MODE = 0x0040
    ENABLE_EXTENDED_FLAGS = 0x0080
    ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    KEY_EVENT = 0x0001
    MOUSE_EVENT = 0x0002
    MOUSE_MOVED = 0x0001
    DOUBLE_CLICK = 0x0002
    MOUSE_WHEELED = 0x0004
    MOUSE_HWHEELED = 0x0008
    FROM_LEFT_1ST_BUTTON_PRESSED = 0x0001

    VK_BACK = 0x08
    VK_RETURN = 0x0D
    VK_ESCAPE = 0x1B
    VK_UP = 0x26
    VK_DOWN = 0x28
    VK_C = 0x43

    LEFT_CTRL_PRESSED = 0x0008
    RIGHT_CTRL_PRESSED = 0x0004

    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class KEY_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("bKeyDown", wintypes.BOOL),
            ("wRepeatCount", wintypes.WORD),
            ("wVirtualKeyCode", wintypes.WORD),
            ("wVirtualScanCode", wintypes.WORD),
            ("uChar", wintypes.WCHAR),
            ("dwControlKeyState", wintypes.DWORD)
        ]

    class MOUSE_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("dwMousePosition", COORD),
            ("dwButtonState", wintypes.DWORD),
            ("dwControlKeyState", wintypes.DWORD),
            ("dwEventFlags", wintypes.DWORD)
        ]

    class EVENT_UNION(ctypes.Union):
        _fields_ = [
            ("KeyEvent", KEY_EVENT_RECORD),
            ("MouseEvent", MOUSE_EVENT_RECORD)
        ]

    class INPUT_RECORD(ctypes.Structure):
        _fields_ = [
            ("EventType", wintypes.WORD),
            ("Event", EVENT_UNION)
        ]

    hStdIn = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    hStdOut = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(hStdIn, ctypes.byref(mode)):
        old_mode_in = mode.value
        new_mode = mode.value
        new_mode &= ~ENABLE_QUICK_EDIT_MODE
        new_mode &= ~ENABLE_VIRTUAL_TERMINAL_INPUT
        new_mode |= ENABLE_EXTENDED_FLAGS
        new_mode |= ENABLE_MOUSE_INPUT
        new_mode |= ENABLE_WINDOW_INPUT
        kernel32.SetConsoleMode(hStdIn, new_mode)
        win32_available = True

    mode_out = ctypes.c_uint32()
    if kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode_out)):
        old_mode_out = mode_out.value
        kernel32.SetConsoleMode(hStdOut, mode_out.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)

    kernel32.GetNumberOfConsoleInputEvents.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.GetNumberOfConsoleInputEvents.restype = wintypes.BOOL
    kernel32.ReadConsoleInputW.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(INPUT_RECORD),
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD)
    ]
    kernel32.ReadConsoleInputW.restype = wintypes.BOOL
    kernel32.FlushConsoleInputBuffer.argtypes = [wintypes.HANDLE]
    kernel32.FlushConsoleInputBuffer.restype = wintypes.BOOL

def enable_ansi():
    if sys.platform == "win32" and old_mode_out is None:
        try:
            import ctypes
            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                ctypes.windll.kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass
    elif sys.platform != "win32":
        sys.stdout.write("\033[?1049h\033[2J")
        sys.stdout.flush()

def restore_console():
    try:
        sys.stdout.write(
            f"{C_RESET}"
            "\033[?1006l\033[?1015l\033[?1003l"
            "\033[?1002l\033[?1000l\033[?25h"
        )
        if sys.platform != "win32":
            sys.stdout.write("\033[?1049l")
        sys.stdout.flush()
    except Exception:
        pass

    if sys.platform == "win32" and old_mode_in is not None:
        kernel32.SetConsoleMode(hStdIn, old_mode_in)
        if old_mode_out is not None:
            kernel32.SetConsoleMode(hStdOut, old_mode_out)

atexit.register(restore_console)

def set_color_mode(dimmed=False):
    global C_BLUE, C_YELLOW, C_GRAY, C_WHITE, C_DARK_GRAY, C_BOLD, C_BG_INPUT
    palette = COLOR_DIM if dimmed else COLOR_NORMAL
    C_BLUE = palette["blue"]
    C_YELLOW = palette["yellow"]
    C_GRAY = palette["gray"]
    C_WHITE = palette["white"]
    C_DARK_GRAY = palette["dark_gray"]
    C_BOLD = palette["bold"]
    C_BG_INPUT = palette["bg_input"]

class RawInput:
    def __enter__(self):
        if sys.platform != "win32":
            import tty
            import termios
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
        return self

    def __exit__(self, *args):
        if sys.platform != "win32":
            import termios
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

def char_width(ch):
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1

def text_width(text):
    return sum(char_width(ch) for ch in str(text))

def truncate_text(text, max_len):
    text = str(text)
    if max_len <= 0:
        return ""
    if text_width(text) <= max_len:
        return text
    if max_len <= 3:
        return "." * max_len
    result = ""
    width = 0
    for ch in text:
        current = char_width(ch)
        if width + current > max_len - 3:
            break
        result += ch
        width += current
    return result + "..."

def get_term_size():
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class COORD(ctypes.Structure):
                _fields_ = [
                    ("X", ctypes.c_short),
                    ("Y", ctypes.c_short),
                ]

            class SMALL_RECT(ctypes.Structure):
                _fields_ = [
                    ("Left", ctypes.c_short),
                    ("Top", ctypes.c_short),
                    ("Right", ctypes.c_short),
                    ("Bottom", ctypes.c_short),
                ]

            class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
                _fields_ = [
                    ("dwSize", COORD),
                    ("dwCursorPosition", COORD),
                    ("wAttributes", wintypes.WORD),
                    ("srWindow", SMALL_RECT),
                    ("dwMaximumWindowSize", COORD),
                ]

            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            info = CONSOLE_SCREEN_BUFFER_INFO()

            if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
                handle,
                ctypes.byref(info)
            ):
                columns = info.srWindow.Right - info.srWindow.Left + 1
                lines = info.srWindow.Bottom - info.srWindow.Top + 1

                if columns > 0 and lines > 0:
                    return os.terminal_size((columns, lines))
        except Exception:
            pass

    try:
        return os.get_terminal_size(sys.stdout.fileno())
    except (OSError, ValueError):
        return shutil.get_terminal_size(fallback=(80, 24))

def get_term_width():
    return get_term_size().columns

def get_layout():
    terminal_width = get_term_width()
    block_width = max(20, min(terminal_width - 4, 76))
    margin = " " * max(0, (terminal_width - block_width) // 2)
    return terminal_width, block_width, margin

def clear_screen(lines=18):
    sys.stdout.write(f"{C_RESET}\033[H\033[0J")
    try:
        terminal_height = get_term_size().lines
        padding = max(0, (terminal_height - lines) // 2)
        if padding:
            sys.stdout.write(f"\033[{padding}B")
    except OSError:
        pass
    sys.stdout.flush()

def print_wrapped_text(text, margin, width, color=C_GRAY):
    lines = textwrap.wrap(
        str(text),
        width=max(10, width),
        break_long_words=False,
        break_on_hyphens=False
    )
    for line in lines or [""]:
        print(f"{margin}{color}{line}{C_RESET}")

_LOGO_RUNS = [
    [("▄",7),(" ",3),("▄",5),(" ",1),("▄",9),(" ",1),("▄",4),(" ",2),("▄",4),(" ",1),("▄",7),(" ",3),("▄",3),(" ",4),("▄",3)],
    [("█",3),("▀",5),(" ",2),("▀",1),("█",3),("▀",1),(" ",1),("▀",3),("█",3),("▀",3),(" ",1),("▀",1),("█",3),(" ",2),("█",3),("▀",1),(" ",1),("█",3),("▀",2),("█",3),("▄",1),(" ",1),("█",4),("▄",1),(" ",2),("█",3)],
    [("█",3),(" ",8),("█",3),(" ",5),("█",3),(" ",5),("█",3),(" ",2),("█",3),(" ",2),("█",3),("▄",2),("█",3),("▀",1),(" ",1),("█",3),("▀",1),("█",2),("▄",1),("█",3)],
    [("█",3),(" ",2),("█",3),("▀",1),(" ",2),("█",3),(" ",5),("█",3),(" ",5),("█",3),("▄",2),("█",3),(" ",2),("█",3),("▀",5),(" ",2),("█",3),(" ",1),("▀",2),("█",4)],
    [("▀",1),("█",6),("▀",1),(" ",2),("▄",1),("█",3),("▄",1),(" ",4),("█",3),(" ",5),("▀",2),("█",4),("▀",2),(" ",2),("█",3),(" ",7),("█",3),(" ",3),("▀",1),("█",3)],
    [(" ",1),("▀",6),(" ",3),("▀",5),(" ",4),("▀",3),(" ",7),("▀",4),(" ",4),("▀",3),(" ",7),("▀",3),(" ",4),("▀",3)]
]

def draw_logo():
    logo = ["".join(ch * n for ch, n in line) for line in _LOGO_RUNS]

    def decode_half_blocks(lines):
        width = max(text_width(line) for line in lines)
        pixels = []
        for line in lines:
            line = line.ljust(width)
            upper = []
            lower = []
            for char in line:
                upper.append(char in ("▀", "█"))
                lower.append(char in ("▄", "█"))
            pixels.append(upper)
            pixels.append(lower)
        return pixels, width

    def color_code(color, background=False):
        prefix = 48 if background else 38
        return f"\033[{prefix};2;{color[0]};{color[1]};{color[2]}m"

    def render_pair(upper, lower):
        if upper is None and lower is None:
            return " "
        if upper == lower:
            return f"{color_code(upper)}█{C_RESET}"
        if upper is None:
            return f"{color_code(lower)}▄{C_RESET}"
        if lower is None:
            return f"{color_code(upper)}▀{C_RESET}"
        return (
            f"{color_code(upper)}"
            f"{color_code(lower, background=True)}"
            f"▀{C_RESET}"
        )

    if C_YELLOW == COLOR_DIM["yellow"]:
        logo_color = (95, 94, 45)
        shadow_color = (34, 34, 16)
    else:
        logo_color = (248, 246, 117)
        shadow_color = (90, 90, 40)

    source, logo_width = decode_half_blocks(logo)
    pixel_height = len(source) + 1
    composed = []

    for y in range(pixel_height):
        row = []
        for x in range(logo_width):
            has_logo = y < len(source) and source[y][x]
            has_shadow = y > 0 and source[y - 1][x]
            if has_logo:
                row.append(logo_color)
            elif has_shadow:
                row.append(shadow_color)
            else:
                row.append(None)
        composed.append(row)

    terminal_width = get_term_width()
    margin = " " * max(0, (terminal_width - logo_width) // 2)

    print()
    for y in range(0, pixel_height, 2):
        upper = composed[y]
        lower = (
            composed[y + 1]
            if y + 1 < pixel_height
            else [None] * logo_width
        )
        rendered = "".join(
            render_pair(upper[x], lower[x])
            for x in range(logo_width)
        ).rstrip()
        print(f"{margin}{rendered}{C_RESET}")
    print()

def draw_header(margin, width, title):
    spaces = " " * max(1, width - text_width(title) - 3)
    print(
        f"{margin}{C_WHITE}{C_BOLD}{title}{C_RESET}"
        f"{spaces}{C_GRAY}esc{C_RESET}\n"
    )

def draw_menu_item(margin, number, text):
    print(f"{margin}{C_YELLOW}{number}{C_RESET}  {C_WHITE}{text}{C_RESET}")

def draw_sys_item(margin, width, label, value):
    prefix = f"{label}   "
    displayed = truncate_text(value, max(1, width - text_width(prefix)))
    print(f"{margin}{C_WHITE}{prefix}{C_RESET}{C_GRAY}{displayed}{C_RESET}")

def print_tip(text, margin, width, label="Tip"):
    lines = textwrap.wrap(
        str(text),
        width=max(10, width - 6),
        break_long_words=False,
        break_on_hyphens=False
    )
    if lines:
        print(f"\n{margin}{C_YELLOW}● {label}{C_RESET} {C_GRAY}{lines[0]}{C_RESET}")
        for line in lines[1:]:
            print(f"{margin}      {C_GRAY}{line}{C_RESET}")
    print()

def pad_text(text, width):
    return str(text) + " " * max(0, width - text_width(text))

def flush_input_events():
    global win_mouse_left_down, _input_queue
    win_mouse_left_down = False
    if sys.platform == "win32" and win32_available:
        kernel32.FlushConsoleInputBuffer(hStdIn)
    elif sys.platform == "win32":
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getwch()
        except Exception:
            pass
    else:
        _input_queue.clear()
        try:
            import select
            while True:
                r, _, _ = select.select([sys.stdin], [], [], 0)
                if not r:
                    break
                os.read(sys.stdin.fileno(), 4096)
        except Exception:
            pass

def parse_vt_sequence(seq):
    if seq == "\x1b[A":
        return "UP"
    if seq == "\x1b[B":
        return "DOWN"
    if seq == "\x1b[C":
        return "RIGHT"
    if seq == "\x1b[D":
        return "LEFT"
    if seq == "\x1bOM":
        return "ENTER"
    if seq == "\x1bOJ":
        return "ENTER"
    if seq.startswith("\x1b[<") and seq.endswith(("M", "m")):
        parts = seq[3:-1].split(";")
        if len(parts) == 3:
            try:
                cb = int(parts[0])
                cx = int(parts[1])
                cy = int(parts[2])
                final = seq[-1]
                if cb & 64:
                    return "IGNORE"
                if final == "M":
                    if cb & 32:
                        return ("HOVER", cx, cy)
                    if (cb & 3) == 0:
                        return ("CLICK", cx, cy)
                    return ("HOVER", cx, cy)
                elif final == "m":
                    return "IGNORE"
                return "IGNORE"
            except ValueError:
                pass
    if seq.startswith("\x1b[M") and len(seq) >= 6:
        try:
            cb = ord(seq[3]) - 32
            cx = ord(seq[4]) - 32
            cy = ord(seq[5]) - 32
            if cb & 64:
                return "IGNORE"
            if cb & 32:
                return ("HOVER", cx, cy)
            if (cb & 3) == 0:
                return ("CLICK", cx, cy)
            return ("HOVER", cx, cy)
        except Exception:
            pass
    return "IGNORE"

def get_win32_event():
    global win_mouse_left_down
    count = wintypes.DWORD()
    if not kernel32.GetNumberOfConsoleInputEvents(hStdIn, ctypes.byref(count)):
        time.sleep(0.01)
        return None
    if count.value == 0:
        time.sleep(0.01)
        return None
    record = INPUT_RECORD()
    read = wintypes.DWORD()
    while count.value > 0:
        if not kernel32.ReadConsoleInputW(hStdIn, ctypes.byref(record), 1, ctypes.byref(read)):
            time.sleep(0.01)
            return None
        kernel32.GetNumberOfConsoleInputEvents(hStdIn, ctypes.byref(count))
        if record.EventType == KEY_EVENT:
            key = record.Event.KeyEvent
            if not key.bKeyDown:
                continue
            vk = key.wVirtualKeyCode
            ch = key.uChar
            ctrl = key.dwControlKeyState & (LEFT_CTRL_PRESSED | RIGHT_CTRL_PRESSED)
            if ctrl and vk == VK_C:
                raise KeyboardInterrupt
            if vk == VK_ESCAPE:
                return "ESC"
            if vk == VK_RETURN:
                return "ENTER"
            if vk == VK_BACK:
                return "BACKSPACE"
            if vk == VK_UP:
                return "UP"
            if vk == VK_DOWN:
                return "DOWN"
            if ch and ch not in ("\x00", "\r", "\n", "\b", "\x1b"):
                return ch
        elif record.EventType == MOUSE_EVENT:
            mouse = record.Event.MouseEvent
            x = int(mouse.dwMousePosition.X) + 1
            y = int(mouse.dwMousePosition.Y) + 1
            flags = mouse.dwEventFlags
            left_down = bool(mouse.dwButtonState & FROM_LEFT_1ST_BUTTON_PRESSED)
            if flags == MOUSE_MOVED:
                win_mouse_left_down = left_down
                return ("HOVER", x, y)
            if flags == 0:
                if left_down and not win_mouse_left_down:
                    win_mouse_left_down = True
                    return ("CLICK", x, y)
                if not left_down:
                    win_mouse_left_down = False
                    return "IGNORE"
            if flags in (DOUBLE_CLICK, MOUSE_WHEELED, MOUSE_HWHEELED):
                return "IGNORE"
    return None

def get_event():
    global _input_queue
    if sys.platform == "win32" and win32_available:
        return get_win32_event()
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch == "\x1b":
                time.sleep(0.08)
                seq = "\x1b"
                while msvcrt.kbhit():
                    seq += msvcrt.getwch()
                if seq == "\x1b":
                    return "ESC"
                return parse_vt_sequence(seq)
            if ch in ("\r", "\n"):
                return "ENTER"
            if ch == "\b":
                return "BACKSPACE"
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch in ("\x00", "\xe0"):
                if msvcrt.kbhit():
                    ch2 = msvcrt.getwch()
                    if ch2 == "H":
                        return "UP"
                    if ch2 == "P":
                        return "DOWN"
                    if ch2 == "K":
                        return "LEFT"
                    if ch2 == "M":
                        return "RIGHT"
                return "IGNORE"
            return ch
        time.sleep(0.01)
        return None
    import select
    if not _input_queue:
        r, _, _ = select.select([sys.stdin], [], [], 0.05)
        if r:
            try:
                data = os.read(sys.stdin.fileno(), 4096).decode("utf-8", errors="replace")
                _input_queue.extend(list(data))
            except Exception:
                pass
    if not _input_queue:
        return None
    ch = _input_queue.pop(0)
    if ch == "\x1b":
        seq = "\x1b"
        if not _input_queue:
            r2, _, _ = select.select([sys.stdin], [], [], 0.18)
            if r2:
                try:
                    data = os.read(sys.stdin.fileno(), 4096).decode("utf-8", errors="replace")
                    _input_queue.extend(list(data))
                except Exception:
                    pass
        if _input_queue and _input_queue[0] in ("[", "O", "]"):
            seq += _input_queue.pop(0)
            while True:
                if not _input_queue:
                    r3, _, _ = select.select([sys.stdin], [], [], 0.03)
                    if r3:
                        try:
                            data = os.read(sys.stdin.fileno(), 4096).decode("utf-8", errors="replace")
                            _input_queue.extend(list(data))
                        except Exception:
                            pass
                    else:
                        break
                if _input_queue:
                    next_ch = _input_queue.pop(0)
                    seq += next_ch
                    if next_ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~Mm":
                        break
                else:
                    break
            if seq.startswith("\x1b[200~"):
                pasted = []
                while True:
                    if not _input_queue:
                        r4, _, _ = select.select([sys.stdin], [], [], 0.03)
                        if r4:
                            try:
                                data = os.read(sys.stdin.fileno(), 4096).decode("utf-8", errors="replace")
                                _input_queue.extend(list(data))
                            except Exception:
                                pass
                    if not _input_queue:
                        break
                    c = _input_queue.pop(0)
                    pasted.append(c)
                    if "".join(pasted).endswith("\x1b[201~"):
                        text = "".join(pasted)[:-6]
                        _input_queue = list(text) + _input_queue
                        return "IGNORE"
            return parse_vt_sequence(seq)
        return "ESC"
    if ch in ("\n", "\r"):
        return "ENTER"
    if ch in ("\x7f", "\b"):
        return "BACKSPACE"
    if ch == "\x03":
        raise KeyboardInterrupt
    if ch == "\x04":
        raise EOFError
    return ch

def show_floating_modal(title, items, bg_draw_func):
    flush_input_events()
    max_len = text_width(title) + 10
    for item in items:
        length = text_width(item["label"]) + (text_width(item.get("shortcut", "")) + 4 if item.get("shortcut") else 0)
        max_len = max(max_len, length)
    mw = min(80, max(40, max_len + 6))
    mh = len(items) + 4
    
    sys.stdout.write("\033[?1000h\033[?1002h\033[?1003h\033[?1015h\033[?1006h\033[?25l")
    sys.stdout.flush()
    
    try:
        selectable = [i for i, it in enumerate(items) if it["type"] == "item"]
        if not selectable:
            return None
        sel_pos = 0
        last_size = (-1, -1)
        force_redraw = True
        sx = 1
        sy = 1

        def draw_dimmed_background():
            try:
                set_color_mode(True)
                bg_draw_func()
            finally:
                set_color_mode(False)

        def update_hover_selection(my):
            nonlocal sel_pos, force_redraw
            best_dist = 99999
            best_idx = sel_pos
            for i_sel, row_idx in enumerate(selectable):
                item_y = sy + 2 + row_idx
                dist = abs(my - item_y)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i_sel
            if best_idx != sel_pos:
                sel_pos = best_idx
                force_redraw = True

        with RawInput():
            while True:
                tw = get_term_width()
                th = get_term_size().lines
                if (tw, th) != last_size:
                    draw_dimmed_background()
                    last_size = (tw, th)
                    force_redraw = True
                if force_redraw:
                    sx = max(1, (tw - mw) // 2)
                    sy = max(1, (th - mh) // 2)
                    title_part = f"  {title}"
                    esc_part = "esc  "
                    spaces = " " * max(0, mw - text_width(title_part) - text_width(esc_part))
                    sys.stdout.write(f"\033[{sy};{sx}H")
                    sys.stdout.write(
                        f"\033[48;2;30;30;30m"
                        f"\033[38;2;210;210;210m{title_part}"
                        f"{spaces}"
                        f"\033[38;2;110;110;110m{esc_part}"
                        f"\033[0m"
                    )
                    sys.stdout.write(f"\033[{sy + 1};{sx}H\033[48;2;30;30;30m{' ' * mw}\033[0m")
                    for i, item in enumerate(items):
                        sys.stdout.write(f"\033[{sy + 2 + i};{sx}H")
                        is_sel = selectable[sel_pos] == i
                        if item["type"] == "category":
                            line = pad_text(f"  {item['label']}", mw)
                            sys.stdout.write(
                                f"\033[48;2;30;30;30m"
                                f"\033[38;2;0;175;255m{line}"
                                f"\033[0m"
                            )
                        else:
                            bg = "\033[48;2;248;246;117m" if is_sel else "\033[48;2;30;30;30m"
                            fg = "\033[38;2;0;0;0m" if is_sel else "\033[38;2;210;210;210m"
                            s_fg = "\033[38;2;80;80;80m" if is_sel else "\033[38;2;110;110;110m"
                            lbl = item["label"]
                            sh = item.get("shortcut", "")
                            sp = max(0, mw - text_width(lbl) - text_width(sh) - 4)
                            sys.stdout.write(f"{bg}{fg}  {lbl}{' ' * sp}{s_fg}{sh}  \033[0m")
                    sys.stdout.write(f"\033[{sy + 2 + len(items)};{sx}H\033[48;2;30;30;30m{' ' * mw}\033[0m")
                    sys.stdout.write(f"\033[{sy + 3 + len(items)};{sx}H\033[48;2;30;30;30m{' ' * mw}\033[0m")
                    sys.stdout.flush()
                    force_redraw = False
                ev = get_event()
                if ev:
                    if ev == "UP":
                        sel_pos = (sel_pos - 1) % len(selectable)
                        force_redraw = True
                    elif ev == "DOWN":
                        sel_pos = (sel_pos + 1) % len(selectable)
                        force_redraw = True
                    elif ev in ("LEFT", "RIGHT", "IGNORE"):
                        continue
                    elif ev == "ESC":
                        return None
                    elif ev == "ENTER":
                        return items[selectable[sel_pos]]["id"]
                    elif isinstance(ev, tuple):
                        action, mx, my = ev
                        if action == "HOVER":
                            update_hover_selection(my)
                        elif action == "CLICK":
                            update_hover_selection(my)
                            if sx <= mx < sx + mw and sy <= my < sy + mh:
                                row = my - sy - 2
                                if 0 <= row < len(items) and items[row]["type"] == "item":
                                    return items[row]["id"]
                            else:
                                return None
    finally:
        sys.stdout.write("\033[?1006l\033[?1015l\033[?1003l\033[?1002l\033[?1000l\033[0m")
        sys.stdout.flush()

def kilo_input(prompt, redraw_callback):
    chars = []
    try:
        sys.stdout.write(f"{C_RESET}\033[?25l")
        tw, bw, m = redraw_callback()

        def draw_prompt():
            prefix = f" {prompt} "
            avail = max(1, bw - text_width(prefix))
            disp = "".join(chars)
            if text_width(disp) > avail:
                while text_width(disp) > avail - 3 and disp:
                    disp = disp[1:]
                disp = "..." + disp
            spaces = max(0, bw - text_width(prefix) - text_width(disp))
            box_render = (
                f"\r{m}{C_BLUE}▌"
                f"{C_BG_INPUT}{C_GRAY}{prefix}"
                f"{C_WHITE}{disp}"
                f"{' ' * spaces}{C_RESET}"
            )
            sys.stdout.write(box_render)
            if spaces > 0:
                sys.stdout.write(f"\033[{spaces}D")
            sys.stdout.flush()

        draw_prompt()
        sys.stdout.write(f"{C_WHITE}\033[?25h")
        sys.stdout.flush()
        last_size = get_term_size()
        with RawInput():
            while True:
                ev = get_event()
                curr_size = get_term_size()
                if curr_size != last_size:
                    last_size = curr_size
                    sys.stdout.write(f"{C_RESET}\033[?25l")
                    tw, bw, m = redraw_callback()
                    sys.stdout.write(f"{C_WHITE}\033[?25h")
                    draw_prompt()
                if ev in ("LEFT", "RIGHT", "UP", "DOWN", "IGNORE"):
                    continue
                if ev == "ESC":
                    sys.stdout.write(f"{C_RESET}\033[?25l")
                    return "esc"
                if ev == "ENTER":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    sys.stdout.write(f"{C_RESET}\033[?25l")
                    return "".join(chars)
                if ev == "BACKSPACE":
                    if chars:
                        chars.pop()
                        draw_prompt()
                elif isinstance(ev, str) and len(ev) == 1:
                    chars.append(ev)
                    draw_prompt()
    except KeyboardInterrupt:
        sys.stdout.write(f"{C_RESET}\033[?1049l\033[?25h\n")
        sys.stdout.flush()
        sys.exit(0)
    except EOFError:
        sys.stdout.write(f"{C_RESET}\033[?25l")
        sys.stdout.flush()
        return "esc"

def _try_clipboard_cmd(cmd, text):
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.communicate(text.encode('utf-8'))
        return p.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False

def copy_to_clipboard(text):
    try:
        if os.name == 'nt':
            return _try_clipboard_cmd(['clip'], text)
        if sys.platform == 'darwin':
            return _try_clipboard_cmd(['pbcopy'], text)
        for cmd in (['termux-clipboard-set'],
                    ['xclip', '-selection', 'clipboard'],
                    ['xsel', '--clipboard', '--input'],
                    ['wl-copy']):
            if _try_clipboard_cmd(cmd, text):
                return True
        data = base64.b64encode(text.encode('utf-8')).decode('ascii')
        sys.stdout.write(f"\033]52;c;{data}\033\\")
        sys.stdout.flush()
        return True
    except Exception:
        return False

def print_status(text, margin):
    print(f"{margin}{C_GRAY}{text}{C_RESET}")