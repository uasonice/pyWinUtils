#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import win32gui as W32
import win32con
import sys
import ctypes

class WinData:
    profile_name: object

    def __init__(self):
        self.version = "0.2"
        self.description = "windows position manager"

        self.init_done = False
        self.cnt = 0
        self.list = []

        # config data information
        self.change_config = False
        self.profile_name = "data"
        self.dumpinfo = False   # dump process simple information.

    def init2(self):
        if self.init_done is True: return
        self.init_done = True
        self.load_config()

    @property
    def get_profile_name(self):
        return self.profile_name

    def set_profile_name(self, str):
        if self.profile_name == str: return
        self.change_config = True
        self.profile_name = str

    @staticmethod
    def ExcludeWinName(title: str, w, h):
        if (2 > len(title)): # 제목이 없거나 1자인 경우
            return True
        if (3 > w + h):    # 넓이 + 높이가 3 미만인 경우
            return True
        return False

    @staticmethod
    def GetWinScreen():
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
        print("screensize: (%d, %d)" % (screensize))
        return screensize

    def ShowWinInfo(self):
        cnt = 0
        for d in self.list:
            cnt += 1
            pos = d['pos'][0]
            self.printinfo("%08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title'])))
            self.printinfo("₩tLocation: %d (%d, %d) - Size: (%d, %d)" % (cnt, pos['x'], pos['y'], pos['w'], pos['h']))
        return

    def ShowWinInfo_sys(self, hwnd):
        rect = W32.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        title = W32.GetWindowText(hwnd)
        if self.ExcludeWinName(title, w, h) == True: return
        self.cnt += 1
        print("Window %s:" % W32.GetWindowText(hwnd))
        print("₩tLocation: %d (%d, %d) - Size: (%d, %d)" % (self.cnt, x, y, w, h))
        return

    def SaveWinInfo(self, hwnd):
        rect = W32.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        title = W32.GetWindowText(hwnd)
        if self.ExcludeWinName(title, w, h) == True: return
        if 0 < title.find("cmd.exe"):            # remove cmd console process
            print("remove cmd console process: %08X %s" % (hwnd, title))
            return

        l = {
            "hwnd": hwnd,
            "title": title,
            "pos": [{
                "x": x,
                "y": y,
                "w": w,
                "h": h
            }]
        }
        self.list.append(l)
        self.cnt += 1
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
            hwnd = W32.FindWindow(None, d['title'])

            if not hwnd:
                self.printinfo("Removed %08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title'])))
                continue
            pos = d['pos'][0]
            try:
                W32.SetWindowPos(hwnd, win32con.HWND_TOP, pos['x'], pos['y'], pos['w'], pos['h'], uflag)
            except:
                self.printinfo("Exception %08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title'])))

            self.printinfo("%08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title'])))
            self.printinfo("₩tLocation: %d (%d, %d) - Size: (%d, %d)" % (cnt, pos['x'], pos['y'], pos['w'], pos['h']))
        return

    def save_config(self, forced: bool = False):
        # 변경 사항이 있는지 확인 하여, 있을 때만 파일을 저장한다.
        if forced is False and self.change_config is False: return
        self.change_config = False

        conf = {
            "profile_name": self.profile_name,
            "username": "login username",
        }
        conffile = "winposcore.conf"
        with open(conffile, 'w') as outfile:
            json.dump(conf, outfile, indent=4)

        print("config saved: %s" % conffile)
        return

    def load_config(self):
        conffile = "winposcore.conf"
        try:
            json_data = open(conffile, encoding='utf-8').read()
            conf = json.loads(json_data)
            print("load config\n", conf)
            self.profile_name = conf['profile_name']
            #print(conf['profile_name'])
        except FileNotFoundError:
            self.save_config(True)
        return


def cbWinShowInfo(hwnd, data: WinData):
    data.ShowWinInfo_sys(hwnd)
    return

def cbWinSave(hwnd, data: WinData):
    data.SaveWinInfo(hwnd)
    return


def winpos_main(windata: WinData, cmd: str):
    #windata = WinData()
    windata.init2()

    #cmd = ["show", "save", "load"]
    print("select cmd: %s" % cmd)

    #windata.dumpinfo = True
    screen = windata.GetWinScreen()
    datafile = "winpos%s_%dx%d.json" % (windata.profile_name, screen[0], screen[1])
    print("datafile name: %s" % datafile)
    if cmd == "show":
        W32.EnumWindows(cbWinShowInfo, windata)

    if cmd == "save":        # 저장
        W32.EnumWindows(cbWinSave, windata)
        with open(datafile, 'w') as outfile:
            json.dump(windata.list, outfile, indent=4)
        windata.ShowWinInfo()
    if cmd == "load":        # 불러오기
        windata.LoadWinInfo(datafile)
    windata.save_config()
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
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
