#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import tkinter as tk
import ctypes
import WinPosCore as wp
import SysTrayIcon as tray
import system_hotkey

def button_pressed(cmd):
    wp.main(["winpos", cmd])

def LoadUI(root: tk.Tk):
    root.title("WinPosManager")
    root.geometry("300x200")

    lbl = tk.Label(root, text="Windows Position Manager")
    lbl.pack()

    btn = tk.Button(root, text="Save", width=20, command=lambda:button_pressed('save'))
    btn.pack()

    btn2 = tk.Button(root, text="Load", width=20, command=lambda:button_pressed('load'))
    btn2.pack()

    btn3 = tk.Button(root, text="Show", width=20, command=lambda:button_pressed('show'))
    btn3.pack()
    return root

def ShowUI():
    root = LoadUI()
    root.mainloop()

def TrayMenu():
    import itertools, glob

    icons = itertools.cycle(glob.glob('data/*.ico'))
    hover_text = "WinPosMgr"
    menu_options = (
        ('Show', None, lambda sysTray:ShowUI()),
        ('Save', None, lambda sysTray:button_pressed('save')),
        ('Load', None, lambda sysTray:button_pressed('load')),
    )
    def bye(sysTrayIcon): print('Bye, then.')

    tray.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)

if __name__ == '__main__':
    hk = system_hotkey.SystemHotkey()
    try:
        hk.register(('super', 'control', 'z'), callback=lambda e:button_pressed('load'))
        hk.register(('super', 'control', 'x'), callback=lambda e: button_pressed('save'))
    except :
        print("already run this program")
        sys.exit(0)

    TrayMenu()
