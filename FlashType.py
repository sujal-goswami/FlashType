# I am building a WPM (words per minute) command line typeing test program.
# I am using curses to build the program.

import curses
import random
import textwrap
import time
from curses import wrapper

MAX_SPEED = 0

def start_screen(stdscr):
    stdscr.clear()
   
    stdscr.addstr(curses.LINES // 2 - 3, curses.COLS // 2 - 10, "Welcome to Flash⚡Type!")
    stdscr.addstr(curses.LINES // 2 - 2, curses.COLS // 2 - 5, "")
    stdscr.addstr(curses.LINES // 2 - 1, curses.COLS // 2 - 10, "Press any key to start")

    stdscr.refresh()
    stdscr.getkey()


def load_text():
	with open("Text.txt", "r") as f:
		lines = f.readlines()
		return random.choice(lines).strip()


def wrap_text(text, width):
    wrapped_text = textwrap.wrap(text, width)
    wrapped_text = "\n".join(wrapped_text)
    return wrapped_text


def display_text(stdscr, target_text, current_text, wpm=0):
    target_text = textwrap.wrap(target_text, 50)

    for i, line in enumerate(target_text):
        stdscr.addstr(i, curses.COLS // 2 - 30, "".join(line))

    stdscr.addstr(5, curses.COLS // 2 - 30, f"WPM: {wpm}")

    i = 0
    col = curses.COLS // 2 - 30
    
    for indx, char in enumerate(current_text):
        if char == "\n":
            i += 1
            col = curses.COLS // 2 - 30
        else:
            if char == target_text[i][indx]:
                stdscr.addstr(i, col, char, curses.color_pair(1))
            else:
                stdscr.addstr(i, col, char, curses.color_pair(2))    

            col += 1
            

def typing_test(stdscr):
    target_text = load_text()
    current_text = []
    wpm = 0
    accuracy = 0
    start_time = time.time()
    stdscr.nodelay(True)

    while True:
        time_elapsed = max(time.time() - start_time, 1)
        wpm = round(len(current_text) / 5 / time_elapsed * 60)

        stdscr.clear()
        display_text(stdscr, target_text, current_text, wpm)
        stdscr.refresh()

        if len(current_text) == len(target_text):
            stdscr.nodealy(False)
            break

        try:
            key = stdscr.getkey()
        except:
            continue

        if key == chr(27):
            break
        
        if key in ("KEY_ENTER", "\n"):
            current_text.append("\n")

        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(current_text) > 0:
                current_text.pop()

        elif len(current_text) < len(target_text):
             current_text.append(key)    


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    start_screen(stdscr)
    while True:
        typing_test(stdscr)
        key = stdscr.getkey()

        if key == chr(27):
            break


wrapper(main)