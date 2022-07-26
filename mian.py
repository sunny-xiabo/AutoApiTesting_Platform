import subprocess
import sys
import logging
import os

gameproc = ["loginserver", "gameserver", "dbserver", "logserver"]


def getPid(process):
    cmd = "ps aux| grep '%s'|grep -v grep " % process
    logging.info(cmd)
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    infos = out.stdout.read().splitlines()
    pidlist = []
    if len(infos) >= 1:
        for i in infos:
            pid = i.split()[1]
            if pid not in pidlist:
                pidlist.append(pid)
        return pidlist
    else:
        return -1


for process in gameproc:
    pid = getPid(process)


print(getPid("chrome"))
