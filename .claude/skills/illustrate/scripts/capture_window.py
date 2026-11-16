#!/usr/bin/env python3
"""Save one desktop window as a PNG without raising it or stealing focus (Windows only).

  capture_window.py --list [--title TEXT] [--process TEXT]
  capture_window.py --title "MyProject" --process UnrealEditor.exe --out screens/editor.png

Exit codes: 0 saved or listed, 1 failed or blank capture, 2 no match, 3 several matches (narrow the filter).
"""
import argparse
import ctypes
import sys
from ctypes import wintypes
from pathlib import Path

from PIL import Image, ImageStat

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
PW_RENDERFULLCONTENT = 2
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
BLANK_STDDEV = 2.0
MIN_SIZE = 200
GDI_FUNCS = (gdi32.CreateCompatibleDC, gdi32.CreateCompatibleBitmap, gdi32.SelectObject, gdi32.GetDIBits)

user32.GetWindowDC.restype = wintypes.HDC
user32.ReleaseDC.argtypes = (wintypes.HWND, wintypes.HDC)
user32.PrintWindow.argtypes = (wintypes.HWND, wintypes.HDC, wintypes.UINT)
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateCompatibleDC.argtypes = (wintypes.HDC,)
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
gdi32.CreateCompatibleBitmap.argtypes = (wintypes.HDC, ctypes.c_int, ctypes.c_int)
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.SelectObject.argtypes = (wintypes.HDC, wintypes.HGDIOBJ)
gdi32.GetDIBits.argtypes = (wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT)
gdi32.DeleteObject.argtypes = (wintypes.HGDIOBJ,)
gdi32.DeleteDC.argtypes = (wintypes.HDC,)


def process_name(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ''
    try:
        size = wintypes.DWORD(1024)
        buf = ctypes.create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return ''
        return Path(buf.value).stem
    finally:
        kernel32.CloseHandle(handle)


def window_size(hwnd):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.right - rect.left, rect.bottom - rect.top


def list_windows(title='', process=''):
    found = []

    def visit(hwnd, _):
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        w, h = window_size(hwnd)
        name = process_name(hwnd)
        if buf.value and w >= MIN_SIZE and h >= MIN_SIZE and title.lower() in buf.value.lower() and process.lower().removesuffix('.exe') in name.lower():
            found.append(dict(hwnd=hwnd, title=buf.value, process=name, w=w, h=h))
        return True

    callback = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(visit)
    user32.EnumWindows(callback, 0)
    return found


def read_bitmap(dc, bitmap, w, h):
    header = (ctypes.c_uint32 * 10)(40, w, ctypes.c_uint32(-h).value, 1 | (32 << 16), 0, 0, 0, 0, 0, 0)
    pixels = ctypes.create_string_buffer(w * h * 4)
    if gdi32.GetDIBits(dc, bitmap, 0, h, pixels, header, 0) != h:
        raise RuntimeError('GetDIBits failed')
    return Image.frombuffer('RGB', (w, h), pixels, 'raw', 'BGRX', 0, 1)


def grab(hwnd):
    w, h = window_size(hwnd)
    win_dc = user32.GetWindowDC(hwnd)
    mem_dc = gdi32.CreateCompatibleDC(win_dc)
    bitmap = gdi32.CreateCompatibleBitmap(win_dc, w, h)
    old = gdi32.SelectObject(mem_dc, bitmap)
    try:
        if not user32.PrintWindow(hwnd, mem_dc, PW_RENDERFULLCONTENT):
            raise RuntimeError('PrintWindow failed')
        return read_bitmap(mem_dc, bitmap, w, h).copy()
    finally:
        gdi32.SelectObject(mem_dc, old)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(hwnd, win_dc)


def is_blank(image):
    return max(ImageStat.Stat(image.convert('RGB')).stddev) < BLANK_STDDEV


def print_windows(windows):
    for win in windows:
        print(f"{win['process']:32} {win['w']:5}x{win['h']:<5} {win['title']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--title', default='', help='case-insensitive part of the window title')
    parser.add_argument('--process', default='', help='case-insensitive part of the process name')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    windows = list_windows(args.title, args.process)
    if args.list:
        print_windows(windows)
        return 0
    if not args.out:
        parser.error('--out is required unless --list is given')
    if not args.title and not args.process:
        parser.error('give --title or --process')
    if not windows:
        print('no matching window (minimized windows are skipped)', file=sys.stderr)
        return 2
    if len(windows) > 1:
        print_windows(windows)
        print('several windows match; narrow --title or --process', file=sys.stderr)
        return 3
    image = grab(windows[0]['hwnd'])
    if is_blank(image):
        print('capture is blank: this window cannot be captured in the background; ask the user for this shot', file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.out)
    print(f'{args.out} {image.width}x{image.height} from "{windows[0]["title"]}"')
    return 0


if __name__ == '__main__':
    sys.exit(main())
