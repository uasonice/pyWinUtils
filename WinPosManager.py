#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import threading
import tkinter as tk
import WinPosCore as wp
import SysTrayIcon as tray
import system_hotkey


# init global var.
class WinPosManager:
    def __init__(self):
        self.root = tk.Tk()

    def get_root(self):
        if self.root is 0:
            self.root = tk.Tk()
        return self.root

    def destroy(self):
        if self.root is not 0:
            self.root.destroy()
            self.root = 0

    @property
    def ui_load(self):
        root = self.get_root()
        my_width = 200
        my_height = 200
        margin_x = 100
        margin_y = 100
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        my_x = screen_width - my_width - margin_x
        my_y = screen_height - my_height - margin_y
        print("X:Y(%d:%d) - width x height: (%dx%d)" % (my_x, my_y, screen_width, screen_height))

        root.title("WinPosManager")
        root.geometry("%dx%d+%d+%d" % (my_width, my_height, my_x, my_y))

        lbl = tk.Label(root, text="Windows Position Manager")
        lbl.pack()

        btn = tk.Button(root, text="Save", width=20, command=lambda: button_pressed('save'))
        btn.pack()

        btn2 = tk.Button(root, text="Load", width=20, command=lambda: button_pressed('load'))
        btn2.pack()

        btn3 = tk.Button(root, text="Show", width=20, command=lambda: button_pressed('show'))
        btn3.pack()

        btn4 = tk.Button(root, text="Exit", width=20, command=lambda: self.destroy())
        btn4.pack()

        root.protocol("WM_DELETE_WINDOW", ui_on_closing)
        return root


def button_pressed(cmd):
    wp.main(["WinPosCore", cmd])


def ui_on_closing():
    global win_mgr
    print("UI close event")
    win_mgr.destroy()


def ui_show():
    global win_mgr
    root = win_mgr.ui_load
    root.mainloop()


def tray_menu():
    import itertools, glob

    icons = itertools.cycle(glob.glob('data/*.ico'))
    hover_text = "WinPosMgr"
    menu_options = (
        ('Show', None, lambda sys_tray: ui_show()),
        ('Save', None, lambda sys_tray: button_pressed('save')),
        ('Load', None, lambda sys_tray: button_pressed('load')),
    )

    def bye(sys_trayIcon):
        global win_mgr
        print('Bye, then.')
        win_mgr.destroy()

    tray.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)


win_mgr = WinPosManager()


if __name__ == '__main__':
    hk = system_hotkey.SystemHotkey()
    try:
        hk.register(('super', 'control', 'z'), callback=lambda e: button_pressed('load'))
        hk.register(('super', 'control', 'x'), callback=lambda e: button_pressed('save'))
    except :
        print("already run this program")
        sys.exit(0)

    # app = threading.Thread(target=ShowUI)
    # app.start()
    tray_menu()
