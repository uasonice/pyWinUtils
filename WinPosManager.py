#!/usr/bin/python
# -*- coding: utf8 -*-
import win32gui
import win32con
import win32api
from io import StringIO
import datetime
import os, sys
import tkinter as tk

import SysRegEdit
import SysRunAdmin
import WinPosCore as wp
import SysTrayIcon as tray
import system_hotkey

# constant value
MIN_WIDTH = 200
MIN_HEIGHT = 200


class WinPosManager(wp.WinData):
    root: tk.Tk
    popup: tk.Tk
    wg_str_profile_name: tk.StringVar
    m_width: int
    m_height: int
    m_margin_x: int
    m_margin_y: int
    m_win: int

    # log message
    wg_log_msg: tk.Text

    def __init__(self):
        wp.WinData.__init__(self)

        self.root = tk.Tk()
        self.popup = None
        self.wg_str_profile_name = tk.StringVar()
        self.removed = False
        self.is_ui_load = False
        self.is_ui_show = False
        self.wg_log_msg = tk.Text()
        self.m_width = MIN_WIDTH
        self.m_height = MIN_HEIGHT
        self.m_margin_x = 100
        self.m_margin_y = 100
        self.pos_mouse = (0, 0)

    # minimize to python console window
    def init_window(self):
        self.m_win = win32gui.FindWindow(None, "WinPosManager")
        #win32gui.ShowWindow(self.m_win, win32con.SW_MINIMIZE)
        win32gui.ShowWindow(self.m_win, win32con.SW_HIDE)

    def get_root(self):
        if self.root is 0:
            self.root = tk.Tk()
        return self.root

    def destroy(self):
        if self.root is 0: return
        if self.removed is False:
            self.ui_show_toggle()
            return
        self.config_save()
        self.root.destroy()
        self.root = 0

    def config_load(self):
        conf = self.init2()
        self.wg_str_profile_name.set(self.get_profile_name)
        #print("coredata: profile(%s)" % self.get_profile_name)
        #print("config_load: profile(%s)" % (self.wg_str_profile_name.get()))
        if conf and conf.get('manager'):
            pos = conf['manager']['pos']
            self.m_width =  pos['w']
            if self.m_width <= MIN_WIDTH:
                self.m_width = MIN_WIDTH
            self.m_height = pos['h']
            if self.m_height <= MIN_HEIGHT:
                self.m_height = MIN_HEIGHT
            self.m_margin_x = pos['margin_x']
            self.m_margin_y = pos['margin_y']

    def config_save(self):
        # check change config
        if self.change_config is False: return
        conf = {'pos': {
            'w': self.m_width,
            'h': self.m_height,
            'margin_x': self.m_margin_x,
            'margin_y': self.m_margin_y,
        }}
        self.save_config(p_conf=conf)

    def ui_load(self):
        root = self.get_root()
        root.title("WinPosManager_UI")
        self.ui_calc_geometry()
        tk.Label(root, text="Windows Position Manager").pack()
        tk.Button(root, text="Save", width=20, command=lambda: button_pressed(self, 'save')).pack()
        tk.Button(root, text="Load", width=20, command=lambda: button_pressed(self, 'load')).pack()
        tk.Button(root, text="Show", width=20, command=lambda: button_pressed(self, 'show')).pack()
        tk.Button(root, text="Exit", width=20, command=lambda: self.destroy()).pack()
        root.protocol("WM_DELETE", self.destroy)
        return root

    def ui_on_move(self, event):
        root = self.get_root()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        now_width = root.winfo_width()
        now_height = root.winfo_height()
        now_x = root.winfo_x()
        now_y = root.winfo_y()
        now_margin_x = screen_width - now_width - now_x
        now_margin_y = screen_height - now_height - now_y
        if self.m_margin_x != now_margin_x:
            self.m_margin_x = now_margin_x
            self.change_config = True
        if self.m_margin_y != now_margin_y:
            self.m_margin_y = now_margin_y
            self.change_config = True
        if self.m_width != now_width:
            self.m_width = now_width
            self.change_config = True
        if self.m_height != now_height:
            self.m_height = now_height
            self.change_config = True
        #print("UI Move or resize event - changed: ", self.change_config)

    def ui_calc_geometry(self, x=0, y=0):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        my_x = screen_width - self.m_width - self.m_margin_x
        my_y = screen_height - self.m_height - self.m_margin_y
        if x > 0 and x + self.m_width <= screen_width:
            print("set x:", x)
            my_x = x
        if y > 0 and y + self.m_height <= screen_height:
            print("set y:", y)
            my_y = y
        if my_x < 0:
            print("reset x:", my_x)
            my_x = 0
        if my_y < 0:
            print("reset y:", my_y)
            my_y = 0
        print("X:Y(%d:%d) - width x height: (%dx%d) scr(%dx%d)" % (my_x, my_y, self.m_width, self.m_height, screen_width, screen_height))
        self.root.geometry("%dx%d+%d+%d" % (self.m_width, self.m_height, my_x, my_y))

    def ui_show_toggle(self):
        if self.is_ui_load is False: return False
        if self.is_ui_show:
            print("UI withdraw")
            self.root.withdraw()
            self.is_ui_show = False
        else:
            print("UI redraw")
            self.root.deiconify()
            self.root.focus_set()
            self.is_ui_show = True
        return True

    def ui_load2(self):
        root = self.get_root()
        self.config_load()

        root.overrideredirect(True)
        root.title("WinPosManager_UI")
        root.resizable(False, False)
        self.ui_calc_geometry()

        if self.ui_show_toggle() is True: return
        self.is_ui_load = True
        self.is_ui_show = True

        def toggle_title():
            if root.overrideredirect():
                root.overrideredirect(False)
            else:
                root.overrideredirect(True)

        frame0 = tk.Frame(root)
        frame0.pack(fill=tk.X)
        lbl = tk.Label(frame0, text="Windows Position Manager")
        lbl.grid(row=0, column=0, padx=7)
        btn0_1 = tk.Button(frame0, text="T", width=1, command=lambda: toggle_title())
        btn0_1.grid(row=0, column=1)
        btn0_2 = tk.Button(frame0, text="X", width=1, command=lambda: self.destroy())
        btn0_2.grid(row=0, column=2)

        frame1 = tk.Frame(root)
        frame1.pack(fill=tk.X)
        lbl1 = tk.Label(frame1, text="Profile: ", width=6)
        lbl1.pack(side=tk.LEFT, padx=2, pady=2)

        entry1 = tk.Entry(frame1, width=13, textvariable=self.wg_str_profile_name)
        entry1.pack(side=tk.LEFT, fill=tk.X, padx=10)

        frame2 = tk.Frame(root)
        frame2.pack(fill=tk.X)
        btn2_1 = tk.Button(frame2, text="Save", width=12, command=lambda: button_pressed(self, 'save'))
        btn2_1.grid(row=0, column=0, padx=3, pady=3)
        btn2_2 = tk.Button(frame2, text="Load", width=12, command=lambda: button_pressed(self, 'load'))
        btn2_2.grid(row=0, column=1, padx=3)

        frame3 = tk.Frame(root)
        frame3.pack(fill=tk.X)
        btn3_1 = tk.Button(frame3, text="Show", width=12, command=lambda: button_pressed(self, 'show'))
        btn3_1.grid(row=0, column=0, padx=3)
        btn3_2 = tk.Button(frame3, text="Close", width=12, command=lambda: self.destroy())
        btn3_2.grid(row=0, column=1, padx=3)

        frame4 = tk.Frame(root)
        frame4.pack(fill=tk.BOTH)
        #wg_log_msg = tk.Text(frame4, height=3, state=tk.DISABLED)
        self.wg_log_msg.master = frame4
        self.wg_log_msg.pack(fill=tk.BOTH)

        def ui_on_closing():
            print("UI close event")
            self.destroy()

        root.protocol("WM_DELETE_WINDOW", ui_on_closing)
        root.bind('<B1-Motion>', lambda ev: self.ui_on_move(ev))
        root.bind('<Configure>', lambda ev: self.ui_on_move(ev))
        root.bind("<Escape>", lambda ev: self.ui_show_toggle())
        root.focus_set()

        return root

    def popupmsg(self, msg):
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None
        self.popup = tk.Tk()
        self.popup.title('wininfo')
        root = self.get_root()
        width=400
        height=300
        x = self.popup.winfo_screenwidth() - width
        y = root.winfo_y() - height
        self.popup.geometry("%dx%d+%d+%d" % (width, height, x, y))
        text_msg = tk.Text(self.popup, height=70)
        text_msg.pack(fill=tk.BOTH)
        text_msg.insert(1.0, msg)
        text_msg.config(state=tk.DISABLED)
        #self.popup.bind("<Key>", lambda ev: self.popup.withdraw())
        self.popup.bind("<Escape>", lambda ev: self.popup.withdraw())
        self.popup.focus_set()

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
            self.wg_log_msg.config(state=tk.NORMAL)
            self.wg_log_msg.delete(1.0, tk.END)
            self.wg_log_msg.config(state=tk.DISABLED)


def button_pressed(mgr, cmd):
    stdout = sys.stdout
    str = mgr.wg_str_profile_name.get()
    if str == "": str = "data"
    print("profile: %s" % str)
    mgr.set_log_message(True, "%s %s" % (cmd, str))
    mgr.set_profile_name(str)
    if cmd == "show":
        sys.stdout = buffer = StringIO()
    wp.winpos_main(mgr, cmd)
    #wp.main(["WinPosCore", cmd])
    if cmd == "show":
        sys.stdout = stdout
        mgr.popupmsg(buffer.getvalue())
    if cmd == "save":
        mgr.set_log_message(False, "cnt: %03d, cntExclude: %03d" % (mgr.cnt, mgr.cntExclude))
    if len(mgr.logging_message) > 0:
        mgr.set_log_message(False, mgr.logging_message)
        mgr.logging_message = ''


def ui_show(sys_tray, forced):
    if forced:  # forced reload WinPosCore
        win_mgr.init_done = False
    root = win_mgr.ui_load2()
    if win_mgr.pos_mouse[0] is 0:
        win_mgr.pos_mouse = win32gui.GetCursorPos()
    win_mgr.ui_calc_geometry(win_mgr.pos_mouse[0])
    if root:
        root.mainloop()

listPos = 10*[None]
def init_list_position():
    global listPos
    # get screen info
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint(win32api.GetCursorPos()))
    work_area = monitor_info.get("Work")
    w_half_1 = int(work_area[2] / 2)
    h_half_1 = int(work_area[3] / 2)
    margin_w = 15 # 화면상에 비는 영역이 발생하여 넓이 보정치
    margin_h = 20
    '''
    screen = win_mgr.get_window_screen()
    w_half_1 = int(screen[0] /2)
    h_half_1 = int(screen[1] /2)
    '''
    listPos[0] = 5* [None]
    listPos[0][0] = wp.Rect().set([0        , 0       , int(w_half_1)+margin_w, h_half_1+margin_h])
    listPos[0][1] = wp.Rect().set([w_half_1 , 0       , int(w_half_1)+margin_w, h_half_1+margin_h])
    listPos[0][2] = wp.Rect().set([0        , h_half_1, int(w_half_1)+margin_w, h_half_1+margin_h])
    listPos[0][3] = wp.Rect().set([w_half_1 , h_half_1, int(w_half_1)+margin_w, h_half_1+margin_h])
    listPos[0][4] = wp.Rect().set([int(w_half_1 /2), int(h_half_1 /2), int(w_half_1)+margin_w, h_half_1+margin_h])
    listPos[1] = 3* [None]
    listPos[1][0] = wp.Rect().set([0               , h_half_1, int(w_half_1 /2)+margin_w, h_half_1+margin_h])
    listPos[1][1] = wp.Rect().set([int(w_half_1 /2), h_half_1, int(w_half_1 /2)+margin_w, h_half_1+margin_h])
    listPos[1][2] = wp.Rect().set([0               , h_half_1, int(w_half_1   )+margin_w, h_half_1+margin_h])
    listPos[2] = 3* [None]
    listPos[2][0] = wp.Rect().set([int(w_half_1 /2), h_half_1, int(w_half_1 /2), h_half_1])
    listPos[2][1] = wp.Rect().set([int(w_half_1   ), h_half_1, int(w_half_1 /2), h_half_1])
    listPos[2][2] = wp.Rect().set([int(w_half_1 /2), h_half_1, int(w_half_1   ), h_half_1])
    listPos[3] = 3* [None]
    listPos[3][0] = wp.Rect().set([w_half_1 -margin_w         , h_half_1, int(w_half_1 /2)+margin_w, h_half_1+margin_h])
    listPos[3][1] = wp.Rect().set([w_half_1 + int(w_half_1 /2), h_half_1, int(w_half_1 /2)         , h_half_1+margin_h])
    listPos[3][2] = wp.Rect().set([w_half_1 -margin_w         , h_half_1, int(w_half_1   )+margin_w, h_half_1+margin_h])
    listPos[4] = 3* [None]
    listPos[4][0] = wp.Rect().set([0               , 0, int(w_half_1 /2), h_half_1*2])
    listPos[4][1] = wp.Rect().set([int(w_half_1 /2), 0, int(w_half_1 /2), h_half_1*2])
    listPos[4][2] = wp.Rect().set([0               , 0, int(w_half_1   ), h_half_1*2])
    listPos[6] = 3* [None]
    listPos[6][0] = wp.Rect().set([w_half_1 -margin_w         , 0, int(w_half_1 /2)+margin_w, h_half_1*2])
    listPos[6][1] = wp.Rect().set([w_half_1 + int(w_half_1 /2), 0, int(w_half_1 /2)         , h_half_1*2])
    listPos[6][2] = wp.Rect().set([w_half_1 -margin_w         , 0, int(w_half_1   )+margin_w, h_half_1*2])
    listPos[7] = 3* [None]
    listPos[7][0] = wp.Rect().set([0               , 0, int(w_half_1 /2)+margin_w, h_half_1+margin_h])
    listPos[7][1] = wp.Rect().set([int(w_half_1 /2), 0, int(w_half_1 /2)+margin_w, h_half_1+margin_h])
    listPos[7][2] = wp.Rect().set([0               , 0, int(w_half_1   )+margin_w, h_half_1+margin_h])
    listPos[8] = 3* [None]
    listPos[8][0] = wp.Rect().set([int(w_half_1 /2), 0, int(w_half_1 /2), h_half_1])
    listPos[8][1] = wp.Rect().set([int(w_half_1   ), 0, int(w_half_1 /2), h_half_1])
    listPos[8][2] = wp.Rect().set([int(w_half_1 /2), 0, int(w_half_1   ), h_half_1])
    listPos[9] = 3* [None]
    listPos[9][0] = wp.Rect().set([w_half_1 -margin_w         , 0, int(w_half_1 /2)+margin_w, h_half_1+margin_h])
    listPos[9][1] = wp.Rect().set([w_half_1 + int(w_half_1 /2), 0, int(w_half_1 /2)         , h_half_1+margin_h])
    listPos[9][2] = wp.Rect().set([w_half_1 -margin_w         , 0, int(w_half_1   )+margin_w, h_half_1+margin_h])

listMovedWin = []
def ui_resizer(sys_tray, key):
    global listMovedWin, listPos
    hwnd = win32gui.GetForegroundWindow()
    print("current win id: ", hwnd)
    str = win32gui.GetWindowText(hwnd)
    print("current win name: ", str)
    pos = win_mgr.get_window_rect(hwnd)
    find_win = None
    idx = None
    for one in listMovedWin:
        if one is None: break
        if one['hwnd'] == hwnd:
            find_win = one
            idx = listMovedWin.index(one)
            break

    if find_win is not None:
        print(find_win)
    else:
        find_win = dict(
            hwnd=hwnd,
            title=str,
            pos=pos,
            key=key,        # pressed key number
            key_count=0,
        )
        listMovedWin.append(find_win)

    def ui_move_position(idx):
        if key == win32con.VK_NUMPAD5:      # return original position
            listMovedWin.remove(find_win)
            return find_win["pos"]
        new_pos = wp.Rect()
        if find_win["key"] != key:
            find_win["key"] = key
            find_win["key_count"] = 0
        len = listPos[idx].__len__()
        if find_win["key_count"] == len:      # return original position
            listMovedWin.remove(find_win)
            new_pos = find_win["pos"]
        else:
            new_pos = listPos[idx][find_win["key_count"]]
            find_win["key_count"] += 1
            pass
        return new_pos

    new_pos = wp.Rect()
    if key >= win32con.VK_NUMPAD0 and key <= win32con.VK_NUMPAD9 :
        new_pos = ui_move_position(key - win32con.VK_NUMPAD0)

    if not new_pos.is_empty():
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, new_pos.x, new_pos.y, new_pos.w, new_pos.h, win32con.SWP_NOZORDER)
    #listMovedWin[idx].update(find_win)
    pass

def tray_menu():
    import itertools, glob

    icons = itertools.cycle(glob.glob('data/*.ico'))
    hover_text = "WinPosManager"
    menu_options = (
        ('Show', None, lambda sys_tray: ui_show(sys_tray, False)),
        ('Save', None, lambda sys_tray: button_pressed(win_mgr, 'save')),
        ('Load', None, lambda sys_tray: button_pressed(win_mgr, 'load')),
        ('Clear log', None, lambda sys_tray: win_mgr.set_log_message('', '', cmd='clear')),
        ('Experiments', None, (
          ('Reset', None, lambda sys_tray: ui_show(sys_tray, True)),
          ('Show debug msg.', None, lambda sys_tray: win32gui.ShowWindow(win_mgr.m_win, win32con.SW_SHOW)),
        ))
    )

    def get_click(sys_trayicon):
        win_mgr.pos_mouse = win32gui.GetCursorPos()

    def bye(sys_trayIcon):
        print('Bye, Bye.')
        #win_mgr.config_save()
        win_mgr.removed = True
        win_mgr.destroy()

    tray.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=0, on_click=get_click)
    if win_mgr:
        win_mgr.removed = True
        win_mgr.destroy()

def run_as_admin():
    if not SysRunAdmin.isUserAdmin():
        print("You're not an admin.", os.getpid(), "params: ", sys.argv)
        rc = SysRunAdmin.runAsAdmin()

win_mgr = WinPosManager()
win_mgr.config_load()


def enableHotkey():
    hk = system_hotkey.SystemHotkey()
    try:
        hk.register(('super', 'control', 'z'), callback=lambda ev: button_pressed(win_mgr, 'load'))
        hk.register(('super', 'control', 'x'), callback=lambda ev: button_pressed(win_mgr, 'save'))
        hk.register(('super', 'control', 'a'), callback=lambda ev: ui_show(ev, False))
        hk.register(('super', 'control', 'kp_0'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD0))
        hk.register(('super', 'control', 'kp_1'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD1))
        hk.register(('super', 'control', 'k'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD2))
        hk.register(('super', 'control', 'kp_3'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD3))
        hk.register(('super', 'control', 'j'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD4))
        hk.register(('super', 'control', 'kp_5'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD5))
        hk.register(('super', 'control', 'l'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD6))
        hk.register(('super', 'control', 'kp_7'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD7))
        hk.register(('super', 'control', 'i'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD8))
        hk.register(('super', 'control', 'kp_9'), callback=lambda ev: ui_resizer(ev, win32con.VK_NUMPAD9))
    except Exception as e:
        print("already run this program: %s" % e)
        sys.exit(0)
    except system_hotkey.SystemRegisterError as e:
        print("key reg. fail: %s" % e)


if __name__ == '__main__':
    #sys.exit(0)
    # minimize to python console window
    win_mgr.init_window()

    # change directory
    os.chdir(os.path.dirname(__file__))

    #run_as_admin()
    #SysRegEdit.execute(__file__)

    init_list_position()
    enableHotkey()

    # app = threading.Thread(target=ShowUI)
    # app.start()
    tray_menu()
