#!usr/bin/env python3
import os
import sys
import re
import platform
import subprocess
import psutil
import cpuinfo


def get_machine_info():

    def get_os():
        if platform.system() == "Windows":
            return '{} {}({})'.format(platform.system(), platform.release(), platform.architecture()[0])
        elif platform.system() == "Darwin":
            return '{} {}({})'.format(platform.system(), platform.mac_ver()[0], platform.architecture()[0])
        else:
            return '{} {}({})'.format(platform.linux_distribution()[0], platform.linux_distribution()[1], platform.architecture()[0])

    def get_driver_ver():
        if os.name == "nt":
            proc = subprocess.Popen(
                ["reg", "query",
                 r"HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\0000",
                 "/v", "ReleaseVersion"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            stdout, stderr = proc.communicate(10)
            return re.search(r'\s(\d+\.\d+.+?)$', stdout.decode(), re.MULTILINE).group(1).strip()
        else:
            return "not_implemented_for_" + os.name

    def get_gpu_name():
        if os.name == "nt":
            tool = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gpu_name.py")
            proc = subprocess.Popen([sys.executable, tool], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            stdout, stderr = proc.communicate(10)
            return stdout.decode().replace("\n", "").replace("\r", "")
        else:
            return "not_implemented_for_" + os.name

    def get_host():
        if platform.system() == "Darwin" and platform.node().endswith('.local'):
            return platform.node()[:-len('.local')]
        else:
            return platform.node()


    try:
        info = {}
        info['os'] = get_os()
        # info['driver'] = get_driver_ver()
        info['host'] = get_host()
        info['cpu_count'] = str(psutil.cpu_count())
        # info['asic'] = get_gpu_name()
        # info['asic_count'] = "{}".format(len(info['asic'].split('+')))
        info['ram'] = psutil.virtual_memory().total / 1024 ** 3
        # info['cpu'] = platform.processor()
        info['cpu'] = cpuinfo.get_cpu_info()['brand']
        return info
    except Exception as err:
        print("Exception: {0}".format(err))
        return {"host": platform.node()}


def print_machine_info():
    info = get_machine_info();

