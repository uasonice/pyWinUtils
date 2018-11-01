#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import win32gui
import win32con
import sys
import ctypes


class WinData(object):
    profile_name: object
    logging_message: str

    def __init__(self):
        self.version = "0.2"
        self.description = "windows position manager"

        self.init_done = False
        self.cnt = 0
        self.list = []
        self.m_conf_file = "winposcore.conf"
        self.logging_message = ""

        # config data information
        self.change_config = False
        self.profile_name = "data"
        self.dumpinfo = False   # dump process simple information.

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
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        title = win32gui.GetWindowText(hwnd)
        if self.ExcludeWinName(title, w, h) == True: return
        self.cnt += 1
        print("Window %s:" % win32gui.GetWindowText(hwnd))
        print("₩tLocation: %d (%d, %d) - Size: (%d, %d)" % (self.cnt, x, y, w, h))
        return

    def SaveWinInfo(self, hwnd):
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        title = win32gui.GetWindowText(hwnd)
        if self.ExcludeWinName(title, w, h) == True: return
        """
        if 0 < title.find("cmd.exe"):            # remove cmd console process
            print("remove cmd console process: %08X %s" % (hwnd, title))
            return
        """
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
            hwnd = win32gui.FindWindow(None, d['title'])
            if not hwnd:
                err_msg = "Removed or Changed %08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title']))
                self.logging_message += err_msg
                print(err_msg)
                #continue
                hwnd = d['hwnd']
            pos = d['pos'][0]
            try:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, pos['x'], pos['y'], pos['w'], pos['h'], uflag)
            except:
                self.printinfo("Exception %08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title'])))

            self.printinfo("%08X Window %s(%2d):" % (d['hwnd'], d['title'], len(d['title'])))
            self.printinfo("₩tLocation: %d (%d, %d) - Size: (%d, %d)" % (cnt, pos['x'], pos['y'], pos['w'], pos['h']))
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

    screen = windata.GetWinScreen()
    datafile = "winpos%s_%dx%d.json" % (windata.profile_name, screen[0], screen[1])
    print("datafile name: %s" % datafile)
    if cmd == "save":        # 저장
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
