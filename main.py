import sys
import subprocess
from pyfiglet import Figlet
from mpimarge import FsctMarge
from mpimarge import FsctMargeMulti
# from mpimarge import FsctMargeMultiGPU
from gensino import FsctGenSino
from gensino import GenSinoRaw
from gensino import FsctGenSinoMX
# -*- coding: utf-8 -*-

if __name__ == '__main__':

    args = sys.argv
    mode = 0
    enermode = 0
    inpath = "."
    outpath = "./output"
    steps = ""
    width = ""
    height = ""

    f = Figlet(font = 'digital')
    msg = f.renderText('SINOGENERATOR')
    print(msg)

    while True:
        mode = input("Operation mode(1: Marge & Sino(.csv)  2: Sino(.csv) 3: Sino(.raw))")
        if int(mode) > 0 and int(mode) < 4:
            enermode = input("Multi-energy(1: Enable 2: Disable)")
            if int(enermode) == 1 or int(enermode) == 2:
                break

    if len(args) >= 2:
        inpath = args[1]

    steps = input("input CT steps:")
    if int(mode) == 1:
        cores = input("input Number of Cores:")
        width = input("input width(pixels):")
        FsctMargeMulti(steps, cores, inpath)
        if int(enermode) == 1:
            FsctGenSinoMX(outpath, steps, width)
        else:
            split = input("input split mode(0:Single file, 1:Each projection)")
            FsctGenSino(outpath, steps, width, split)
    elif int(mode) == 2:
        width = input("input width(pixels):")
        if int(enermode) == 1:
            FsctGenSinoMX(inpath, steps, width)
        else:
            split = input("input split mode(0:Single file, 1:Each projection)")
            FsctGenSino(outpath, steps, width, split)
    elif int(mode) == 3:
        width = input("input width(pixels):")
        height = input("input height(pixels):")
        GenSinoRaw(inpath, steps, width, height)

        subprocess.Popen(["explorer", r"./output"], shell=True)
