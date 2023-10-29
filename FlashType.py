import curses
import random
import textwrap
import time
import requests
import platform
from curses import wrapper

MAX_SPEED = 0


art = """
                                                    ______________
                                                   /             /
                                                  /             /
                                                 /              ____
                                                 _____             /
                                                    /         /    /
                                                   /         /    /
                                                  /         /    /
                                                 /         /____/
                                                 \        /
                                                  \      /
                                                   \    / 
                                                    \  /
                                                     \/           
"""


def start_screen(stdscr):
    stdscr.clear()
    custom_banner = """
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @______  _       ___   _____  _   _   _____ __   ________  _____ @
    @|  ___|| |     / _ \ /  ___|| | | | |_   _|\ \ / /| ___ \|  ___|@
    @| |_   | |    / /_\ \\ `--. | |_| |   | |   \ V / | |_/ /| |__  @
    @|  _|  | |    |  _  | `--. \|  _  |   | |    \ /  |  __/ |  __| @
    @| |    | |____| | | |/\__/ /| | | |   | |    | |  | |    | |___ @
    @\_|    \_____/\_| |_/\____/ \_| |_/   \_/    \_/  \_|    \____/ @
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    """
    custom_banner_lines = custom_banner.strip().split('\n')
    banner_height = len(custom_banner_lines)
    banner_width = max(len(line) for line in custom_banner_lines)

    start_x = (curses.COLS - banner_width) // 2
    start_y = (curses.LINES - banner_height) // 2

    for i, line in enumerate(custom_banner_lines):
        stdscr.addstr(start_y + i, start_x, line)

    # Add a custom title
    title = "Flash⚡Type"
    title_x = (curses.COLS - len(title)) // 2
    stdscr.addstr(start_y + banner_height + 1, title_x,
                  title, curses.color_pair(5) | curses.A_BOLD)

    # Additional information or instructions can be added here
    instructions = "Press any key to start"
    instructions_x = (curses.COLS - len(instructions)) // 2
    stdscr.addstr(start_y + banner_height + 3,
                  instructions_x, instructions, curses.A_BOLD)

    stdscr.refresh()
    stdscr.getch()


def load_text(desired_length=300):
    accumulated_text = ""
    try:
        while len(accumulated_text) < desired_length:
            response = requests.get("https://api.quotable.io/random")
            if response.status_code != 200:
                raise Exception()
            data = response.json()
            if platform.system() == "Windows":
                data['content'] = data['content'].replace('\'', ' ')
            accumulated_text += data['content'] + " "
    except:
        with open('Text.txt', 'r') as f:
            accumulated_text = f.read().replace('\n', ' ')
    return accumulated_text


def wrap_text(text, width):
    wrapped_text = textwrap.wrap(text, width)
    return wrapped_text


def display_text(stdscr, Type_win, target_text, current_text, wpm=0, accuracy=0):
    Type_win_height, Type_win_width = Type_win.getmaxyx()

    target_text = wrap_text(target_text, Type_win_width-10)
    for i, line in enumerate(target_text):
        Type_win.addstr(2+i, 5, line)

    Type_win.addstr(Type_win_height - 2, Type_win_width //
                    2 - 10, f"WPM: {wpm}")
    Type_win.addstr(Type_win_height - 2, Type_win_width //
                    2, f"Accuracy: {accuracy}%")

    target_text = ";".join(target_text)

    col = 5
    indx = 0

    for i, char in enumerate(current_text):
        if target_text[i] == ";":
            col = 5
            indx += 1
        else:
            if char == target_text[i]:
                Type_win.addstr(indx+2, col, char, curses.color_pair(1))
            else:
                Type_win.addstr(indx+2, col, char, curses.color_pair(2))
            col += 1


def typing_test(stdscr, typing_window):
    target_text = load_text()
    current_text = []
    wpm = 0
    accuracy = 0
    correct = 0
    index = 0
    start_time = time.time()
    typing_window.nodelay(True)

    while True:
        time_elapsed = max(time.time() - start_time, 1)
        wpm = round(len(current_text) / 5 / time_elapsed * 60)
        if len(current_text) > 0:
            correct = sum([1 for i in range(len(current_text))
                          if current_text[i] == target_text[i]])
            accuracy = round(correct / len(current_text) * 100)

        if len(current_text) == len(target_text):
            return wpm, accuracy

        display_text(stdscr, typing_window, target_text,
                     current_text, wpm, accuracy)
        typing_window.refresh()

        if len(current_text) == len(target_text):
            typing_window.nodealy(False)
            break

        try:
            key = typing_window.getkey()
        except Exception as e:
            continue

        if key == chr(27):
            return wpm, accuracy

        if key in ("KEY_ENTER", "\n"):
            current_text.append("\n")

        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(current_text) > 0:
                current_text.pop()

        elif len(current_text) < len(target_text):
            current_text.append(key)


def result_screen(stdscr, typing_window, wpm, accuracy):
    height, width = typing_window.getmaxyx()
    typing_window.clear()
    typing_window.border()
    typing_window.addstr(2, width // 2 - 3, "Results", curses.color_pair(4))
    typing_window.addstr(height - 5, width // 2 - 11,
                         f"WPM: {wpm}", curses.A_STANDOUT)
    typing_window.addstr(height - 5, width // 2 + 1,
                         f"Accuracy: {accuracy}%", curses.A_STANDOUT)
    typing_window.addstr(height - 2, curses.COLS // 2 - 25,
                         "Press Space bar to start again 🔁")
    typing_window.refresh()

    typing_window.nodelay(1)  # Set typing window to non-blocking mode
    while True:
        key = typing_window.getch()
        if key == ord(" "):  # Check if space bar was pressed
            return True
        elif key != -1:  # Check if any other key was pressed
            return False


def main(stdscr):
    content = load_text()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    start_screen(stdscr)

    while True:
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr(5, curses.COLS // 2 - 5,
                      "Flash⚡Type", curses.color_pair(5))
        stdscr.refresh()
        Typing_window = curses.newwin(
            curses.LINES - 20, curses.COLS - 20, 10, 10)
        Typing_window.border()
        wpm, accuracy = typing_test(stdscr, Typing_window)
        retry = result_screen(stdscr, Typing_window, wpm, accuracy)
        if retry:
            continue
        else:
            break


if __name__ == "__main__":
    wrapper(main)
