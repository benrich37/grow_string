from ase.io import read,write
from ase.constraints import FixedMode
from ase.optimize import BFGS
from JDFTx import JDFTx, shell
import numpy as np
from time import ctime
import os
import sys
import copy
from io_funcs import setup_img_dir

def new_calc():
    calculator = JDFTx(
            pseudoSet='SG15',
            ignoreStress=True,
            commands={
                'elec-cutoff' : '30',
                'dump' : 'End ElecDensity'
            }
    )
    return calculator

def distance_metric(posns1, posns2):
    sum_hold = 0
    for i in range(len(posns1)):
        sum_hold += abs(np.linalg.norm(posns1[i] - posns2[i]))
    return sum_hold

def scale_op(metric1, metric2):
    tot = metric1 + metric2
    s1 = metric1/tot
    s2 = metric2/tot
    s1 = s1**2
    s2 = s2**2
    tot2 = s1+s2
    r1 = s1/tot2
    r2 = s2/tot2
    return r1, r2

from opt_funcs import opt_image, get_next_img, nearly_same_posns

def setup_next_img(images, )

def grow_string(initial_img, final_img, fmax=0.1, stepsize=0.05, calc_fn=new_calc, optimizer=BFGS, logname='log.txt', tmpfile = 'cur.xyz', imgfile = 'images.xyz'):
    # initial is an atoms with calculators already set
    # final is an atoms with calculators already set
    images = setup_img_dir(initial_img)
    continuing = True
    while continuing:
        n_imgs = len(images)
        f.write(ctime() + ': ' + str(n_imgs) + ' Images currently \n')
        f.write(ctime() + ': ' + 'optimizing image ' + str(n_imgs) + '\n')
        f.close()
        cur_img = images[-1]
        cur_img.set_calculator(calc_fn())
        try:
            opt_image(cur_img, optimizer, fmax)
        except Exception as e:
            f = open(logname, 'a')
            f.write(ctime() + ': ' + str(e) + '\n')
            f.close()
        next_img = get_next_img(cur_img, final_img, stepsize)
        if nearly_same_posns(next_img.get_positions(), final_img.get_positions(), stepsize):
            f = open(logname, 'a')
            f.write(ctime() + ': ' + 'Next image will be too similar to given final, breaking \n')
            f.close()
            continuing = False
        else:
            f = open(logname, 'a')
            f.write(ctime() + ': ' + 'Initializing next image \n')
            images.append(next_img)
            write(tmpfile, next_img)
            write(imgfile, images)
            f.close()
    f = open(logname, 'a')
    f.write(ctime() + ': ' + 'appending final image \n')
    f.close()
    images.append(final_img)
    write(imgfile, images)

