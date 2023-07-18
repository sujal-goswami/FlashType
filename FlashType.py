

import curses
import random
import textwrap
import time
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
    # stdscr.addstr(0, 0, art, curses.A_BOLD)
    stdscr.addstr(curses.LINES // 2 - 5 - 2  , curses.COLS // 2 - 5, "Welcome to")
    stdscr.addstr(curses.LINES // 2 - 3 - 2, curses.COLS // 2 - 5, "Flash⚡Type!", curses.color_pair(5))
    # stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 5, "")
    stdscr.addstr(curses.LINES // 2 - 1 - 2, curses.COLS // 2 - 11, "Press any key to start")
    stdscr.addstr(curses.LINES // 2 - 1 , 5, art, curses.color_pair(5))

    stdscr.refresh()
    stdscr.getkey()


def load_text():
    with open("Text.txt", "r") as f:
        content = f.read().replace("\n", " ")
    return content
     

def wrap_text(text, width):
    wrapped_text = textwrap.wrap(text, width)
    return wrapped_text


def display_text(stdscr, Type_win, target_text, current_text, wpm=0, accuracy=0):
    Type_win_height, Type_win_width = Type_win.getmaxyx()

    target_text = wrap_text(target_text, Type_win_width-10)
    for i, line in enumerate(target_text):
        Type_win.addstr(2+i, 5, line)

    Type_win.addstr(Type_win_height - 2, Type_win_width // 2 - 10, f"WPM: {wpm}")
    Type_win.addstr(Type_win_height - 2, Type_win_width // 2 , f"Accuracy: {accuracy}%")

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
            correct = sum([1 for i in range(len(current_text)) if current_text[i] == target_text[i]])
            accuracy = round(correct / len(current_text) * 100)


        if len(current_text) == len(target_text):
            return wpm, accuracy

        display_text(stdscr, typing_window, target_text, current_text, wpm , accuracy)
        typing_window.refresh()

        if len(current_text) == len(target_text):
            typing_window.nodealy(False)
            break

        try:
            key = typing_window.getkey()
        except:
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
    typing_window.addstr(2  , width // 2 - 3, "Results", curses.color_pair(4))
    typing_window.addstr(height - 5, width // 2 - 11, f"WPM: {wpm}", curses.A_STANDOUT)
    typing_window.addstr(height - 5, width // 2 + 1, f"Accuracy: {accuracy}%", curses.A_STANDOUT)
    typing_window.addstr(height - 2, curses.COLS // 2 - 25, "Press Space bar to start again 🔁")
    typing_window.refresh()

    typing_window.nodelay(1)  # Set typing window to non-blocking mode
    while True:
        key = typing_window.getch()
        if key == ord(" "):  # Check if space bar was pressed
            return True
        elif key != -1:  # Check if any other key was pressed
            return False

def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    start_screen(stdscr)
    
    while True:
        stdscr.clear()
        stdscr.refresh()
        content = load_text()
        stdscr.addstr(5 , curses.COLS // 2 - 5, "Flash⚡Type", curses.color_pair(5))
        stdscr.refresh()
        Typing_window = curses.newwin(curses.LINES - 20, curses.COLS - 20, 10, 10)
        Typing_window.border()
        wpm , accuracy = typing_test(stdscr, Typing_window)
        retry = result_screen(stdscr, Typing_window, wpm, accuracy)
        if retry:
            continue
        else:
            break
        

wrapper(main)