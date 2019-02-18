#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import win32gui
import win32con
import sys
import ctypes


class Point:
    x: int
    y: int

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, pt):
        return Point(self.x + pt.x, self.y + pt.y)

    def __sub__(self, pt):
        return Point(self.x - pt.x, self.y - pt.y)

    def __mul__(self, scalar):
        return Point(self.x *scalar, self.y *scalar)

    def __div__(self, scalar):
        return Point(self.x /scalar, self.y /scalar)

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)


class Rect(Point):
    w: int
    h: int

    def __init__(self, pt1=Point(), pt2=Point()):
        self.x = pt1.x
        self.y = pt1.y
        self.w = pt2.x
        self.h = pt2.y

    def __add__(self, rect):
        return Rect(self.x + rect.x, self.y + rect.y, self.w + rect.w, self.h + rect.h)

    def __sub__(self, rect):
        return Rect(self.x - rect.x, self.y - rect.y, self.w - rect.w, self.h - rect.h)

    def __str__(self):
        return "(%d, %d, %d, %d)" % (self.x, self.y, self.w, self.h)

    def set(self, obj):
        try:
            #print(type(obj))
            if type(obj) == list:
                self.x = obj[0]
                self.y = obj[1]
                self.w = obj[2]
                self.h = obj[3]
            elif type(obj) == dict:
                self.x = obj['x']
                self.y = obj['y']
                self.w = obj['w']
                self.h = obj['h']
        except Exception as e:
            pass
        return self

    def to_json(self):
        return dict(x=self.x, y=self.y, w=self.w, h=self.h)


class WinData(object):
    profile_name: object
    logging_message: str

    def __init__(self):
        self.version = "0.2"
        self.description = "windows position manager"

        self.init_done = False
        self.cnt = 0
        self.cntExclude = 0
        self.list = []
        self.m_conf_file = "winposcore.conf"
        self.logging_message = ""

        # config data information
        self.change_config = False
        self.profile_name = "data"
        self.dumpinfo = False   # dump process simple information.

        # exclude App. list
        self.exclude_list = ["cmd.exe"]

    def init2(self):
        if self.init_done is True: return 0
        self.init_done = True
        return self.load_config()

    @property
    def get_profile_name(self):
        return self.profile_name

    def set_profile_name(self, str):
        if self.profile_name == str: return
        self.change_config = True
        self.profile_name = str

    def ExcludeWinName(self, hwnd, title: str, pos):
        if win32gui.IsWindowEnabled(hwnd) == False:
            return True
        if win32gui.IsWindowVisible(hwnd) == False:
            return True
        if (2 > len(title)): # 제목이 없거나 1자인 경우
            return True
        if (100 > pos.w + pos.h):   # 넓이 + 높이가 100 미만인 경우
            return True
        if (0 > pos.x + pos.w):     # X 축 모니터 벗어남
            return True
        if (0 > pos.y + pos.h):     # Y 축 모니터 벗어남
            return True
        for name in self.exclude_list:   # remove App
            if 0 < title.find(name):
                print("remove App: %08X %s" % (hwnd, name))
                return True
        return False

    @staticmethod
    def get_window_screen():
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
        print("screensize: (w:%d, h:%d)" % (screensize))
        return screensize

    def get_window_rect(self, hwnd):
        w_rect = win32gui.GetWindowRect(hwnd)
        pt = Point(w_rect[0], w_rect[1])
        r = Rect(pt, Point(w_rect[2], w_rect[3]) - pt)
        return r

    def ShowWinInfo(self):
        cnt = 0
        for d in self.list:
            cnt += 1
            pos = Rect.set(Rect(), d['pos'])
            self.printinfo("%08X [%s]: %d (%d, %d) - Size: (%d, %d)" % (d['hwnd'], d['title'], \
                cnt, pos.x, pos.y, pos.w, pos.h))
        return

    def ShowWinInfo_sys(self, hwnd):
        title = win32gui.GetWindowText(hwnd)
        pos = self.get_window_rect(hwnd)
        if self.ExcludeWinName(hwnd, title, pos) == True:
            return
        self.cnt += 1
        print("%08X [%s]: %d (%d, %d) - Size: (%d, %d)" % (hwnd, win32gui.GetWindowText(hwnd), \
            self.cnt, pos.x, pos.y, pos.w, pos.h))
        return

    def SaveWinInfo(self, hwnd):
        title = win32gui.GetWindowText(hwnd)
        pos = self.get_window_rect(hwnd)
        if self.ExcludeWinName(hwnd, title, pos) == True:
            self.cntExclude += 1
            return
        self.cnt += 1
        l = {
            "no": self.cnt,
            "hwnd": hwnd,
            "title": title,
            "pos": pos.to_json()
        }
        self.list.append(l)
        return

    def printinfo(self, fmt):
        if self.dumpinfo:
            print(fmt)

    def LoadWinInfo(self, data):
        try:
            json_data = open(data, encoding='utf-8').read()
            self.list = json.loads(json_data)
        except FileNotFoundError:
            print("no found winpos info file: %s" % data)
            return

        cnt = 0
        uflag = win32con.SWP_NOZORDER
        for d in self.list:
            cnt += 1
            hwnd = win32gui.FindWindow(None, d['title'])
            if not hwnd:
                err_msg = "Removed or Changed %08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title']))
                self.logging_message += err_msg
                print(err_msg)
                #continue
                hwnd = d['hwnd']
            pos = Rect.set(Rect(), d['pos'])
            try:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, pos.x, pos.y, pos.w, pos.h, uflag)
            except:
                self.printinfo("Exception %08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title'])))

            self.printinfo("%08X [%s]: %d (%d, %d) - Size: (%d, %d)" % (d['hwnd'], d['title'], \
                cnt, pos.x, pos.y, pos.w, pos.h))
        return

    def save_config(self, forced: bool=False, p_conf=''):
        # 변경 사항이 있는지 확인 하여, 있을 때만 파일을 저장한다.
        if forced is False and self.change_config is False: return
        self.change_config = False

        conf = {
            "config_version":   self.version,
            "profile_name":     self.profile_name,
            "username":         "login username",
        }
        if len(p_conf) > 0:
            conf['manager'] = p_conf
        with open(self.m_conf_file, 'w') as outfile:
            json.dump(conf, outfile, indent=4)

        print("config saved: %s" % self.m_conf_file)
        return

    def load_config(self):
        try:
            json_data = open(self.m_conf_file, encoding='utf-8').read()
            conf = json.loads(json_data)
            print("load config\n", conf)
            self.profile_name = conf['profile_name']
            #print(conf['profile_name'])
        except FileNotFoundError as e:
            self.save_config(True)
        return conf


def cbWinShowInfo(hwnd, data: WinData):
    data.ShowWinInfo_sys(hwnd)
    return

def cbWinSave(hwnd, data: WinData):
    data.SaveWinInfo(hwnd)
    return


def winpos_main(windata: WinData, cmd: str):
    windata.init2()

    #cmd = ["show", "save", "load"]
    print("select cmd: %s" % cmd)

    #windata.dumpinfo = True
    if cmd == "show":
        win32gui.EnumWindows(cbWinShowInfo, windata)
        return 0

    screen = windata.get_window_screen()
    datafile = "winpos_%s_%dx%d.json" % (windata.profile_name, screen[0], screen[1])
    print("datafile name: %s" % datafile)
    if cmd == "save":        # 저장
        windata.cntExclude = 0
        win32gui.EnumWindows(cbWinSave, windata)
        with open(datafile, 'w') as outfile:
            json.dump(windata.list, outfile, indent=4)
        windata.ShowWinInfo()
    elif cmd == "load":        # 불러오기
        windata.LoadWinInfo(datafile)
    return 0

def main(argv):
    windata = WinData()
    cmd = "show"

    if len(argv) is 1:
        print("needed command option")
        print("default cmd: %s"% cmd)
    else:
        cmd = argv[1]

    winpos_main(windata, cmd)
    windata.save_config()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
