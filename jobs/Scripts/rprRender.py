import argparse
import sys
import os
import subprocess
import psutil
import ctypes
import pyscreenshot
import json
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from jobs_launcher.core.config import main_logger


def get_windows_titles():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    titles = []

    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)

    return titles


def createArgsParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tests_list', required=True, metavar="<path>")
    parser.add_argument('--render_path', required=True, metavar="<path>")
    parser.add_argument('--scene_path', required=True, metavar="<path")
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--output_img_dir', required=True)
    parser.add_argument('--output_file_ext', required=True)
    return parser.parse_args()


def main():
    args = createArgsParser()

    tests_list = {}

    if not os.path.exists(args.output_img_dir):
        os.makedirs(args.output_img_dir)
    
    with open(args.tests_list, 'r') as file:
        tests_list = json.loads(file.read())

    tests = []
    for test in tests_list:
        if test['status'] == 'active':
            tests.append(test['name'])

    with open(os.path.join(os.path.dirname(__file__), 'main_template.py'), 'r') as file:
        py_script = file.read().format(tests=tests, work_dir=args.output_dir.replace('\\', '/'), res_path=args.scene_path.replace('\\', '/'))

    with open(os.path.join(args.output_dir, 'script.py'), 'w') as file:
        file.write(py_script)

    shutil.copyfile(os.path.join(os.path.dirname(__file__), 'convertVR2RPR.py'), os.path.join(args.output_dir, 'convertVR2RPR.py'))

    cmd_script = '''
    set MAYA_CMD_FILE_OUTPUT=%cd%/renderTool.log
    set PYTHONPATH=%cd%;PYTHONPATH
    set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
    "{}" -command "python(\\"import script as converter\\"); python(\\"converter.main()\\");" '''.format(args.render_path)

    cmd_script_path = os.path.join(args.output_dir, 'renderRPR.bat')

    try:
        with open(cmd_script_path, 'w') as file:
            file.write(cmd_script)
    except OSError as err:
        main_logger.error(str(err))
        return 1
    else:
        rc = -1
        os.chdir(args.output_dir)
        p = psutil.Popen(cmd_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        while True:
            try:
                rc = p.wait(timeout=5)
            except psutil.TimeoutExpired as err:
                fatal_errors_titles = ['maya', 'Student Version File', 'Radeon ProRender Error', 'Script Editor']
                if set(fatal_errors_titles).intersection(get_windows_titles()):
                    rc = -1
                    try:
                        error_screen = pyscreenshot.grab()
                        error_screen.save(os.path.join(args.output_dir, 'error_screenshot.jpg'))
                    except:
                        pass
                    for child in reversed(p.children(recursive=True)):
                        child.terminate()
                    p.terminate()
                    break
            else:
                break

        for test in tests_list:
            if test['status'] == 'active':
                conversion_log_path = os.path.join(args.scene_path, test['name'] + '.log')
                if os.path.exists(conversion_log_path):
                    shutil.copyfile(conversion_log_path, os.path.join(args.output_dir, test['name'] + '.conversion.log'))
        return rc


if __name__ == "__main__":
    exit(main())
