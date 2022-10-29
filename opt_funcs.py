import numpy as np
from ase.constraints import FixedMode
from time import ctime

def two_pt_tangent(cur_img, final_img):
    return final_img.get_positions() - cur_img.get_positions()

def normalize_vecs_as_set(vecs):
    norm = np.linalg.norm(vecs)
    return vecs/norm

def three_pt_tangent(rA, rO, rB):
    # Uses approximation via finite differences as written in
    # "Asymptotic Analysis of Three-Point Approximation of Vertex
    # Normals and Curvatures" - Anoshkina et al
    a = rO-rA
    a_len = np.linalg.norm(a)
    b = rB - rO
    b_len = np.linalg.norm(b)
    ab = rB - rA
    sum1 = b/b_len
    sum2 = a/a_len
    sum3 = -(ab/(a_len + b_len))
    return sum1 + sum2 + sum3

def nearly_same_posns(posns1, posns2, cutoff):
    return_bool = True
    for i in range(len(posns1)):
        next_bool = abs(np.linalg.norm(posns1[i] - posns2[i])) < cutoff
        return_bool *= next_bool
    return_bool = bool(return_bool)
    return return_bool

def add_vec_to_posns(image, vec):
    posns = image.get_positions()
    posns += vec
    image.set_positions(posns)

def set_constrain_tangent(last_img, cur_img, final_img):
    con_tan = three_pt_tangent(
        last_img.get_positions(),
        cur_img.get_positions(),
        final_img.get_positions()
    )
    c = FixedMode(con_tan)
    cur_img.set_constraint(c)

def get_next_img(last_img, final_img, stepsize, calc_fn):
    cur_img = last_img.copy()
    dir_vec = normalize_vecs_as_set(two_pt_tangent(cur_img, final_img))
    add_vec_to_posns(cur_img, dir_vec*stepsize)
    set_constrain_tangent(last_img, cur_img, final_img)
    cur_img.set_calculator(calc_fn())
    return cur_img

def opt_image(img, optimizer, fmax, logname, n):
    f = open(logname, 'a')
    f.write(ctime() + ': ' + 'optimizing image ' + str(n) + '\n')
    f.close()
    dyn = optimizer(img)
    dyn.run(fmax=fmax)