#!/usr/bin/python
# -*- coding: utf8 -*-

import json
import win32gui as W32
import win32con
import sys


class WinData:
    def __init__(self):
        self.version = "0.1"
        self.description = "windows position manager"

        self.cnt = 0
        self.list = []
        self.dumpinfo = False   # dump process simple information.

    def ExcludeWinName(self, title: str, w, h):
        if (2 > len(title)): # 제목이 없거나 1자인 경우
            return True
        if (3 > w + h):    # 넓이 + 높이가 3 미만인 경우
            return True
        return False

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
        json_data = open(data, encoding='utf-8').read()
        self.list = json.loads(json_data)

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


def cbWinShowInfo(hwnd, data: WinData):
    data.ShowWinInfo_sys(hwnd)
    return

def cbWinSave(hwnd, data: WinData):
    data.SaveWinInfo(hwnd)
    return


def main(argv):
    windata = WinData()

    cmd = "show"
    #cmd = ["show", "save", "load"]

    if len(argv) is 1:
        print("needed command option")
        print("default cmd: %s"% cmd)
    else:
        cmd = argv[1]
        print("select cmd: %s"% cmd)

    #windata.dumpinfo = True
    filename = 'winposdata.json'
    if cmd == "show":
        W32.EnumWindows(cbWinShowInfo, windata)

    if cmd == "save":        # 저장
        W32.EnumWindows(cbWinSave, windata)
        with open(filename, 'w') as outfile:
            json.dump(windata.list, outfile, indent=4)
        windata.ShowWinInfo()
    if cmd == "load":        # 불러오기
        windata.LoadWinInfo(filename)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
