from ase.io import read,write
from ase.constraints import FixedMode
from ase.optimize import BFGS
from JDFTx import JDFTx, shell
import numpy as np
from time import ctime
import os
import sys
import os
import copy

img_dirname = 'images/'
img_prefix = 'img_'
img_suffix = '.xyz'

def check_img_dir(dirname):
    if os.path.isdir(dirname):
        return True
    else:
        os.mkdir(dirname)
        return False

def read_img_dir():
    imgs = []
    i = 0
    reading = True and os.path.isfile(img_dirname + img_prefix + str(i) + img_suffix)
    while reading:
        imgs.append(read(img_dirname + img_prefix + str(i) + img_suffix))
        i += 1
        reading = reading and os.path.isfile(img_dirname + img_prefix + str(i) + img_suffix)
    return imgs


def setup_img_dir(i_img):
    if check_img_dir(img_dirname):
        imgs = read_img_dir()
    else:
        write(img_dirname + img_prefix + '0' + img_suffix, i_img)
        imgs = [i_img]
    return imgs


def start_log_file(logname):
    f = open(logname, 'w')
    f.write(ctime() + ": Beggining string growth: \n \n")
    f.close()