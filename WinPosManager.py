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
    m_width: int
    m_height: int
    m_margin_x: int
    m_margin_y: int

    # log message
    wg_log_msg: tk.Text

    def __init__(self):
        self.root = tk.Tk()
        self.profile_name = tk.StringVar()
        self.removed = False
        self.is_load = False
        self.wg_log_msg = tk.Text()
        self.m_width = 200
        self.m_height = 200
        self.m_margin_x = 100
        self.m_margin_y = 100

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
        self.config_save()
        self.root.destroy()
        self.root = 0

    def set_data(self, data: wp.WinData):
        assert isinstance(data, object)
        self.data = data
        conf = data.init2()
        self.config_load(conf)

    def config_load(self, conf: dict=None):
        self.profile_name.set(self.data.get_profile_name)
        if conf and conf.get('manager'):
            pos = conf['manager']['pos']
            self.m_width =  pos['w']
            self.m_height = pos['h']
            self.m_margin_x = pos['margin_x']
            self.m_margin_y = pos['margin_y']
        #print("coredata: profile(%s)" % self.data.get_profile_name)
        #print("config_load: profile(%s)" % (self.profile_name.get()))

    def config_save(self):
        # check change config
        if self.data.change_config is False: return
        conf = {'pos': {
            'w': self.m_width,
            'h': self.m_height,
            'margin_x': self.m_margin_x,
            'margin_y': self.m_margin_y,
        }}
        self.data.save_config(p_conf=conf)

    def ui_load(self):
        root = self.get_root()
        self.m_width = 200
        self.m_height = 200
        self.m_margin_x = 100
        self.m_margin_y = 100
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        my_x = screen_width - self.m_width - self.m_margin_x
        my_y = screen_height - self.m_height - self.m_margin_y
        print("X:Y(%d:%d) - width x height: (%dx%d)" % (my_x, my_y, screen_width, screen_height))

        root.title("WinPosManager")
        root.geometry("%dx%d+%d+%d" % (self.m_width, self.m_height, my_x, my_y))

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

        root.protocol("WM_DELETE", self.ui_on_closing)
        return root

    @staticmethod
    def ui_on_closing():
        print("UI close event")
        win_mgr.destroy()

    @staticmethod
    def ui_on_move(event):
        #print("UI move event")
        root = win_mgr.get_root()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        now_width = root.winfo_width()
        now_height = root.winfo_height()
        now_x = root.winfo_x()
        now_y = root.winfo_y()
        now_margin_x = screen_width - now_width - now_x
        now_margin_y = screen_height - now_height - now_y
        if win_mgr.m_margin_x != now_margin_x:
            win_mgr.m_margin_x = now_margin_x
            win_mgr.data.change_config = True
        if win_mgr.m_margin_y != now_margin_y:
            win_mgr.m_margin_y = now_margin_y
            win_mgr.data.change_config = True
        if win_mgr.m_width != now_width:
            win_mgr.m_width = now_width
            win_mgr.data.change_config = True
        if win_mgr.m_height != now_height:
            win_mgr.m_height = now_height
            win_mgr.data.change_config = True

    def ui_load2(self):
        root = self.get_root()
        self.config_load()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        my_x = screen_width - self.m_width - self.m_margin_x
        my_y = screen_height - self.m_height - self.m_margin_y
        print("X:Y(%d:%d) - width x height: (%dx%d)" % (my_x, my_y, screen_width, screen_height))

        root.title("WinPosManager")
        root.geometry("%dx%d+%d+%d" % (self.m_width, self.m_height, my_x, my_y))
        root.resizable(False, False)

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
        entry1.pack(side=tk.LEFT, fill=tk.X, padx=10)

        frame2 = tk.Frame(root)
        frame2.pack(fill=tk.X)
        btn2_1 = tk.Button(frame2, text="Save", width=20, command=lambda: button_pressed(self, 'save'))
        btn2_1.grid(row=0, column=0, padx=5)
        btn2_2 = tk.Button(frame2, text="Load", width=20, command=lambda: button_pressed(self, 'load'))
        btn2_2.grid(row=1, column=0, padx=5)

        frame3 = tk.Frame(root)
        frame3.pack(fill=tk.X)
        btn3_1 = tk.Button(frame3, text="Show", width=12, command=lambda: button_pressed(self, 'show'))
        btn3_1.grid(row=0, column=0, padx=5)
        btn3_2 = tk.Button(frame3, text="Exit", width=12, command=lambda: self.destroy())
        btn3_2.grid(row=0, column=1, padx=5)

        frame4 = tk.Frame(root)
        frame4.pack(fill=tk.BOTH)
        #wg_log_msg = tk.Text(frame4, height=3, state=tk.DISABLED)
        self.wg_log_msg.master = frame4
        self.wg_log_msg.pack(fill=tk.BOTH)
        """
        scroll4 = tk.Scrollbar(frame4)
        scroll4.pack(side=tk.RIGHT, fill=tk.Y)
        self.wg_log_msg.pack(side=tk.LEFT, fill=tk.Y)
        scroll4.config(command=self.wg_log_msg.yview)
        self.wg_log_msg.config(yscrollcommand=scroll4.set)
        """

        root.protocol("WM_DELETE_WINDOW", self.ui_on_closing)
        root.bind('<B1-Motion>', self.ui_on_move)
        root.bind('<Configure>', self.ui_on_move)
        return root

    def set_log_message(self, add_time, msg, cmd='insert'):
        if cmd == 'insert':
            now = datetime.datetime.now()
            log_msg = ''
            if len(self.wg_log_msg.get(0.0, tk.END)) > 1:
                log_msg = "\n"
            if add_time:
                #log_msg += now.strftime("%Y%m%d %H:%M ")
                log_msg += now.strftime("%H:%M:%S ")
            log_msg += msg
            self.wg_log_msg.config(state=tk.NORMAL)
            self.wg_log_msg.insert(tk.END, log_msg)
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
    mgr.set_log_message(True, "%s %s" % (cmd, str))
    mgr.data.set_profile_name(str)
    wp.winpos_main(mgr.data, cmd)
    #wp.main(["WinPosCore", cmd])
    if len(mgr.data.logging_message) > 0:
        mgr.set_log_message(False, mgr.data.logging_message)
        mgr.data.logging_message = ''


def ui_show():
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
        print('Bye, then.')
        #win_mgr.data.save_config()
        win_mgr.destroy()

    tray.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)


win_mgr = WinPosManager()
win_mgr.set_data(wp.WinData())

if __name__ == '__main__':
    hk = system_hotkey.SystemHotkey()
    try:
        hk.register(('super', 'control', 'z'), callback=lambda e: button_pressed(win_mgr, 'load'))
        hk.register(('super', 'control', 'x'), callback=lambda e: button_pressed(win_mgr, 'save'))
    except Exception as e:
        print("already run this program: %s" % e)
        sys.exit(0)

    # app = threading.Thread(target=ShowUI)
    # app.start()
    tray_menu()
    win_mgr.removed = True
