#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; WinPosManager 에 Win+Ctrl+2, 4, 6, 8 key-mapping 이 되지 않아 autoHotKey 를 이용해 key-mapping 을 함.
#^Numpad2::#^k
#^Numpad4::#^j
#^Numpad6::#^l
#^Numpad8::#^i

