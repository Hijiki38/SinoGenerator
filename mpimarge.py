import sys
import csv
import os
import time
import numpy as np
# import cupy as cp
import tqdm
import multiprocessing
from multiprocessing import Pool
# -*- coding: utf-8 -*-


#fsct6mpiの出力ファイルを統合
def FsctMarge(step, core, inpath):

    start = time.time()

    angle = 0
    print("processing...")
    os.makedirs("./output", exist_ok=True)
    for i in tqdm.tqdm(range(int(step))):
        outfilename = f"./output/{angle:06.2f}.csv"
        outlist = None
        with open(outfilename, 'w') as fo:
            for j in range(int(core)):
                infilename = inpath + f"/{angle:06.2f}.{j:06}.csv"
                with open(infilename, 'r') as fi:
                    inreader = csv.reader(fi)
                    outreader = csv.reader(fo)
                    inlist = np.array([[int(k) for k in l] for l in inreader])
                    if(outlist is None):
                        outlist = np.full(np.shape(inlist),0) #init with zeros
                    outlist += inlist
            np.savetxt(outfilename, outlist, fmt='%d', delimiter=',')
            angle += 360 / int(step)

    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")


def FsctMargeMulti(step, core, inpath):

    print("processing...")
    cpucount = multiprocessing.cpu_count()
    os.makedirs("./output", exist_ok=True)

    start = time.time()

    outlist = None
    anglerange = [i * (360 / int(step)) for i in range(int(step))]
    infilearray = [[inpath + f"/{i:06.2f}.{j:06}.csv" for j in range(int(core))] for i in anglerange] #all angles, all cores
    p = Pool(int(cpucount))
    imap = p.imap(__Marge, infilearray)
    outlistarray = list(tqdm.tqdm(imap, total=len(infilearray)))
    #outlistarray = p.map(__Marge, infilearray) #core allay will be passed to the function "__Marge"

    angle = 0
    for i in range(int(step)):
        outfilename = f"./output/{angle:06.2f}.csv"
        np.savetxt(outfilename, outlistarray[i], fmt='%d', delimiter=',')
        angle += 360 / int(step)

    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")


def __Marge(corenamearray):
    outlist = None
    for infilename in corenamearray:
        with open(infilename, 'r') as fi:
            inreader = csv.reader(fi)
            inlist = np.array([[int(k) for k in l] for l in inreader])
            if(outlist is None):
                outlist = np.full(np.shape(inlist),0) #init with zeros
            outlist += inlist
    return outlist


#
# def FsctMargeMultiGPU(step, core, inpath):
#
#     print("processing...")
#     cpucount = multiprocessing.cpu_count()
#     os.makedirs("./output", exist_ok=True)
#
#     start = time.time()
#
#     outlist = None
#     anglerange = [i * (360 / int(step)) for i in range(int(step))]
#     infilearray = [[inpath + f"/{i:06.2f}.{j:06}.csv" for j in range(int(core))] for i in anglerange] #all angles, all cores
#     p = Pool(int(cpucount))
#     imap = p.imap(__MargeGPU, infilearray)
#     outlistarray = list(tqdm.tqdm(imap, total=len(infilearray)))
#     #outlistarray = p.map(__Marge, infilearray) #core allay will be passed to the function "__Marge"
#
#     angle = 0
#     for i in range(int(step)):
#         outfilename = f"./output/{angle:06.2f}.csv"
#         np.savetxt(outfilename, outlistarray[i], fmt='%d', delimiter=',')
#         angle += 360 / int(step)
#
#     elapsed_time = time.time() - start
#     print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
#
#
# def __MargeGPU(corenamearray):
#     outlist = None
#     for infilename in corenamearray:
#         with open(infilename, 'r') as fi:
#             inreader = csv.reader(fi)
#             inlist = cp.array([[int(k) for k in l] for l in inreader])
#             if(outlist is None):
#                 outlist = cp.full(np.shape(inlist),0) #init with zeros
#             outlist += inlist
#     return outlist


if __name__ == '__main__':

    args = sys.argv
    if len(args) < 2:
        inpath = "."
    else:
        inpath = args[1]
        steps = input("input CT steps:")
        cores = input("input Number of Cores:")
    FsctMarge(steps, cores, inpath)
