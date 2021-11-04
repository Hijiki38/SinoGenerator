import sys
import csv
import numpy as np
import tqdm
import base64
import binascii
import glob
import os
import code
# -*- coding: utf-8 -*-

def FsctGenSino(inpath, steps, width, split):
    # steps = input("input CT steps:")
    # width = input("input width(pixels):")
    angle = 0

    os.makedirs("./output", exist_ok=True)
    outfilename = "./output/sinogram.csv"
    outfilebase = "./output"
    outlist = np.empty((int(steps), int(width)))
    with open(outfilename, 'w') as fo:
        for i in tqdm.tqdm(range(int(steps))): #step回繰り返し
            infilename = inpath + f"\{angle:06.2f}.csv"
            with open(infilename, 'r') as fi:
                tmplist = np.zeros(int(width))
                inreader = csv.reader(fi)
                inlist = np.array([[int(k) for k in l] for l in inreader]) #csvの要素取り込み
                for j in inlist:
                    tmplist += j #全行を足す
                outlist[i] = tmplist
                angle += 360 / int(steps)

        if(int(split) == 0):
            np.savetxt(outfilename, outlist, fmt='%d', delimiter=',')
        else:
            for i in range(int(steps)):
                np.savetxt(outfilebase + "/projection" + str(i) + ".csv", outlist[i], fmt='%d', delimiter=',')


def FsctGenSinoMX(inpath, steps, width):
    # steps = input("input CT steps:")
    # width = input("input width(pixels):")
    angle = 0
    rowcount = 0
    bin = 1
    maxbins = 1000
    offset = 0.04
    deltae = 0.4


    while True:
        tmp = input("Max bin counts(default 1000):")
        if tmp == "":
            break
        maxbins = int(tmp)
        if maxbins > 0:
            break
    while True:
        tmp = input("bin offset(default 0.04 keV):")
        if tmp == "":
            break
        offset = float(tmp)
        if offset > 0:
            break
    while True:
        tmp = input("bin width(default 0.4 keV):")
        if tmp == "":
            break
        deltae = float(tmp)
        if deltae > 0:
            break

    thresholds = [0]

    while True:
        tmp = input("input thresholds(keV) (Enter to exit)")
        if tmp == "":
            break
        # tmpthre = int((float(tmp) - (offset + deltae / 2)) / deltae) + 2
        tmpthre = __keVtoBin(tmp,offset,deltae)
        thresholds.append(tmpthre)
        # print("Threshold added: " + tmp + " keV(" + str((tmpthre - 1) * deltae + offset) + ")")
        print("Threshold added: " + tmp + " keV(" + str(__BintokeV(tmpthre,offset,deltae)) + ")")

    thresholds.append(maxbins)

    os.makedirs("./output", exist_ok=True)
    outfilename = "./output/sinogram_total.csv"
    outfilebase = "./output"
    outlistall = np.empty((int(steps), int(width)))
    outlist = np.empty((int(len(thresholds) - 1),int(steps), int(width)))
    with open(outfilename, 'w') as fo:
        for i in tqdm.tqdm(range(int(steps))): #step回繰り返し
            infilename = inpath + f"\{angle:06.2f}.csv"
            with open(infilename, 'r') as fi:
                tmplist = np.zeros(int(width))
                inreader = csv.reader(fi)
                inlistall = np.array([[int(k) for k in l] for l in inreader]) #csvの要素取り込み
                for j in inlistall:
                    tmplist += j #全行を足す
                outlistall[i] = tmplist


                for j in range(len(thresholds) - 1):
                    tmplist = np.zeros(int(width)) #エネルギー別
                    inlist = inlistall[thresholds[j]:thresholds[j+1]]
                    for k in inlist:
                        tmplist += k
                    outlist[j][i] = tmplist
                angle += 360 / int(steps)


        #code.InteractiveConsole(globals()).interact()
        np.savetxt(outfilename, outlistall, fmt='%d', delimiter=',')
        for j in range(len(thresholds) - 1):
            np.savetxt(outfilebase + "/sinogram" + str(__BintokeV(thresholds[j],offset,deltae)) + ".csv" , outlist[j], fmt='%d', delimiter=',')

def __BintokeV(input, offset, deltae):
    result = (input - 1) * deltae + offset
    if result < 0:
        return 0
    else:
        return result

def __keVtoBin(input, offset, deltae):
    return int((float(input) - (offset + deltae / 2)) / deltae) + 2


def GenSinoRaw(inpath, maxsteps, width, height):

#rawからサイノグラムを作成
#各フレームの特定の行だけを集めてつくる
#入力　1つのrawファイル

    size = 2 #byte size for 1 character

    # maxsteps = input("input CT steps:")
    # width = input("input width(pixels):")
    # height = input("Input height(pixels):")

    infile = ""
    outfilelist = []

    #choose input file
    candidates = glob.glob(inpath + '/*.raw')
    for i in range(len(candidates)):
        print(str(i) + ": " + candidates[i])
    while True:
        tmp = input("Choose Input File:")
        if int(tmp) >= 0 and int(tmp) < len(candidates):
            infile = candidates[int(tmp)]
            break
        else:
            print("error: invalid value")

    os.makedirs("./output", exist_ok=True)
    for i in range(1,int(height)+1):
        outfilelist.append(open("./output/sino_" + str(i) + ".csv", 'w'))

    countx = 0
    county = 0
    step = 0

    outfilename = "./sinogram.csv"
    outlist = np.empty((int(height), int(maxsteps), int(width)))

    with open(infile, 'rb') as fi:
        data = fi.read(size)
        while data and step < int(maxsteps):
            decode = int.from_bytes(data, 'little')
            outlist[county][step][countx] = decode
            if countx >= int(width)-1:
                countx = 0
                if county >= int(height)-1:
                    county = 0
                    step += 1
                else:
                    county += 1
            else:
                countx += 1
            data = fi.read(size)
            #angle += 360 / int(steps)

    for i in range(int(height)):
        np.savetxt(outfilelist[i], outlist[i], fmt='%d', delimiter=',')
        outfilelist[i].close()


if __name__ == '__main__':

    print("### FsctGenSino / GenSinoRaw ###")

    args = sys.argv
    mode = 0
    steps = ""
    width = ""
    if len(args) < 2:
        inpath = "."
    else:
        inpath = args[1]
    while True:
        mode = input("Operation mode(0:.csv (fsct6), 1:.raw)")
        if int(mode) == 0 or int(mode) == 1:
            break
        else:
            print("error: invalid value")
    if int(mode) == 0:
        print("activate FsctGenSino...")
        FsctGenSino(inpath, steps, width)
    elif int(mode) == 1:
        print("activate GenSinoRaw...")
        GenSinoRaw(inpath, steps, width, height)
