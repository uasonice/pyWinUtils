#!/usr/bin/python
# -*- coding: utf8 -*-
import datetime
import sys
import threading
import tkinter as tk
import WinPosCore as wp
import SysTrayIcon as tray
import system_hotkey


# init global var.
class WinPosManager:
    root: tk.Tk
    profile_name: tk.StringVar
    data: wp.WinData

    # log message
    wg_log_msg: tk.Text

    def __init__(self):
        self.root = tk.Tk()
        self.profile_name = tk.StringVar()
        self.removed = False
        self.is_load = False
        self.wg_log_msg = tk.Text(height=3)

    def get_root(self):
        if self.root is 0:
            self.root = tk.Tk()
        return self.root

    def destroy(self):
        if self.root is 0: return
        if self.removed is False:
            self.root.withdraw()
            print("UI withdraw")
            return
        self.root.destroy()
        self.root = 0

    def set_data(self, data: wp.WinData):
        assert isinstance(data, object)
        self.data = data
        data.init2()
        self.config_load()

    def config_load(self):
        self.profile_name.set(self.data.get_profile_name)
        #print("coredata: profile(%s)" % self.data.get_profile_name)
        #print("config_load: profile(%s)" % (self.profile_name.get()))

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

        btn = tk.Button(root, text="Save", width=20, command=lambda: button_pressed(self, 'save'))
        btn.pack()

        btn2 = tk.Button(root, text="Load", width=20, command=lambda: button_pressed(self, 'load'))
        btn2.pack()

        btn3 = tk.Button(root, text="Show", width=20, command=lambda: button_pressed(self, 'show'))
        btn3.pack()

        btn4 = tk.Button(root, text="Exit", width=20, command=lambda: self.destroy())
        btn4.pack()

        root.protocol("WM_DELETE_WINDOW", ui_on_closing)
        return root

    def ui_load2(self):
        root = self.get_root()
        self.config_load()
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

        if self.is_load is True:
            print("UI redraw")
            root.deiconify()
            return
        self.is_load = True

        lbl = tk.Label(root, text="Windows Position Manager")
        lbl.pack()

        frame1 = tk.Frame(root)
        frame1.pack(fill=tk.X)
        lbl1 = tk.Label(frame1, text="Profile: ", width=6)
        lbl1.pack(side=tk.LEFT, padx=2, pady=2)

        entry1 = tk.Entry(frame1, width=13, textvariable=self.profile_name)
        entry1.pack(fill=tk.X, padx=10, expand=True)

        frame2 = tk.Frame(root)
        frame2.pack(fill=tk.X)
        btn = tk.Button(frame2, text="Save", width=20, command=lambda: button_pressed(self, 'save'))
        btn.pack()
        btn2 = tk.Button(frame2, text="Load", width=20, command=lambda: button_pressed(self, 'load'))
        btn2.pack()

        frame3 = tk.Frame(root)
        frame3.pack(fill=tk.X)
        btn3 = tk.Button(frame3, text="Show", width=12, command=lambda: button_pressed(self, 'show'))
        btn3.pack(side=tk.LEFT, padx=2, pady=2)
        btn4 = tk.Button(frame3, text="Exit", width=12, command=lambda: self.destroy())
        btn4.pack(fill=tk.X, padx=2, expand=True)

        frame4 = tk.Frame(root)
        frame4.pack(fill=tk.BOTH)
        #wg_log_msg = tk.Text(frame4, height=3, state=tk.DISABLED)
        self.wg_log_msg.master = frame4
        self.wg_log_msg.pack()
        #scroll4 = tk.Scrollbar(frame4)
        #scroll4.pack(side=tk.RIGHT, fill=tk.Y)
        #self.wg_log_msg.pack(side=tk.LEFT, fill=tk.Y)
        #scroll4.config(command=self.wg_log_msg.yview)
        #self.wg_log_msg.config(yscrollcommand=scroll4.set)

        root.protocol("WM_DELETE_WINDOW", ui_on_closing)
        return root

    def set_log_message(self, msg, cmd = 'insert'):
        if cmd == 'insert':
            now = datetime.datetime.now()
            #str_time = now.strftime("%Y%m%d %H:%M")
            str_time = now.strftime("%H:%M:%S")
            self.wg_log_msg.config(state=tk.NORMAL)
            self.wg_log_msg.insert(tk.END, "\n%s %s" % (str_time, msg))
            self.wg_log_msg.see(tk.END)
            self.wg_log_msg.config(state=tk.DISABLED)
        elif cmd == 'clear':
            self.wg_log_msg.delete(0, tk.END)


#    @data.setter
#    def data(self, value):
#        self._data = value


def button_pressed(mgr, cmd):
    str = mgr.profile_name.get()
    if str == "": str = "data"
    print("profile: %s" % str)
    mgr.set_log_message("%s %s" % (cmd, str))
    mgr.data.set_profile_name(str)
    wp.winpos_main(mgr.data, cmd)
    #wp.main(["WinPosCore", cmd])


def ui_on_closing():
    global win_mgr
    print("UI close event")
    win_mgr.destroy()


def ui_show():
    global win_mgr
    #root = win_mgr.ui_load()
    root = win_mgr.ui_load2()
    root.mainloop()


def tray_menu():
    import itertools, glob

    icons = itertools.cycle(glob.glob('data/*.ico'))
    hover_text = "WinPosMgr"
    menu_options = (
        ('Show', None, lambda sys_tray: ui_show()),
        ('Save', None, lambda sys_tray: button_pressed(win_mgr, 'save')),
        ('Load', None, lambda sys_tray: button_pressed(win_mgr, 'load')),
    )

    def bye(sys_trayIcon):
        global win_mgr
        print('Bye, then.')
        win_mgr.destroy()

    tray.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)


win_mgr = WinPosManager()
win_mgr.set_data(wp.WinData())

if __name__ == '__main__':
    hk = system_hotkey.SystemHotkey()
    try:
        hk.register(('super', 'control', 'z'), callback=lambda e: button_pressed(win_mgr, 'load'))
        hk.register(('super', 'control', 'x'), callback=lambda e: button_pressed(win_mgr, 'save'))
    except :
        print("already run this program")
        sys.exit(0)

    # app = threading.Thread(target=ShowUI)
    # app.start()
    tray_menu()
    win_mgr.removed = True
    win_mgr.data.save_config()
