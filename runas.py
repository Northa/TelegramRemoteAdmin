import ctypes
from enum import IntEnum
from sys import executable, argv
from subprocess import run

# Reference:
# msdn.microsoft.com/en-us/library/windows/desktop/bb762153(v=vs.85).aspx

# beautiful solution. Credits:
# https://stackoverflow.com/a/42787518/15442115


class SW(IntEnum):

    HIDE = 0
    MAXIMIZE = 3
    MINIMIZE = 6
    RESTORE = 9
    SHOW = 5
    SHOWDEFAULT = 10
    SHOWMAXIMIZED = 3
    SHOWMINIMIZED = 2
    SHOWMINNOACTIVE = 7
    SHOWNA = 8
    SHOWNOACTIVATE = 4
    SHOWNORMAL = 1


class ERROR(IntEnum):

    ZERO = 0
    FILE_NOT_FOUND = 2
    PATH_NOT_FOUND = 3
    BAD_FORMAT = 11
    ACCESS_DENIED = 5
    ASSOC_INCOMPLETE = 27
    DDE_BUSY = 30
    DDE_FAIL = 29
    DDE_TIMEOUT = 28
    DLL_NOT_FOUND = 32
    NO_ASSOC = 31
    OOM = 8
    SHARE = 26


def runas(main):
    if ctypes.windll.shell32.IsUserAnAdmin():
        main()
    else:
        # SW.HIDE param hides the shell window
        # https://docs.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutea?#sw_hide-0
        hinstance = ctypes.windll.shell32.ShellExecuteW(
            None, 'runas', executable, argv[0], None, SW.HIDE)
        if hinstance <= 32:
            raise RuntimeError(ERROR(hinstance))


def test():
    # running smth requires superuser privilege
    run(["regedit"])


if __name__ == '__main__':
    runas(test)
