from ase.io import read,write
from ase.constraints import FixedMode
from ase.optimize import BFGS
from JDFTx import JDFTx, shell
import numpy as np
from time import ctime
import os
import sys
import copy
from io_funcs import setup_img_dir, write_error_to_log, write_img
from opt_funcs import opt_image, get_next_img, nearly_same_posns, setup_next_img


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

def grow_string(initial_img, final_img, fmax=0.1, stepsize=0.05, calc_fn=new_calc, optimizer=BFGS, logname='log.txt'):
    # initial is an atoms with calculators already set
    # final is an atoms with calculators already set
    images = setup_img_dir(initial_img)
    continuing = setup_next_img(images, final_img, stepsize, new_calc, logname)
    while continuing:
        n = len(images) - 1
        cur_img = images[-1]
        try:
            opt_image(cur_img, optimizer, fmax, logname, n)
        except Exception as e:
            write_error_to_log(logname, n, e)
        write_img(cur_img, n)
        continuing = setup_next_img(images, final_img, stepsize, calc_fn, logname)
    f = open(logname, 'a')
    f.write(ctime() + ': ' + 'Normal Termination \n')
    f.close()

from io_funcs import write_pickle
from ase.vibrations import Vibrations
def get_modes(img, fname='img_'):
    img.set_calculator(new_calc())
    BFGS(img).run(fmax=0.01)
    write_pickle(img, fname + "opt.pkl")
    vib = Vibrations(img)
    vib.run()
    write_pickle(vib, fname + "vib.pkl")





