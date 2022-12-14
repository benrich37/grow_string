import numpy as np
from ase.constraints import FixedMode
from time import ctime

def get_bond_vec(img, i, j):
    posns = img.get_positions()
    vec = posns[j] - posns[i]
    return vec

def get_bond_length(img, i, j):
    vec = get_bond_vec(img, i, j)
    return np.linalg.norm(vec)

def change_bond_length(img, i, j, l):
    vec = get_bond_vec(img, i, j)
    vec2 = (l/np.linalg.norm(vec))*vec
    posns = img.get_positions()
    posn_j = posns[i] + vec2
    posns[j] = posn_j
    img.set_positions(posns)

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
    b = rB-rO
    b_len = np.linalg.norm(b)
    ab = rB - rA
    sum1 = b/b_len
    sum2 = a/a_len
    sum3 = -(ab/(a_len + b_len))
    # sum3 = -(ab / (np.linalg.norm(ab)))
    return sum1 + sum2 + sum3

def nearly_same_posns(posns1, posns2, stepsize):
    return_bool = True
    for i in range(len(posns1)):
        # True -> position overlapping with final image
        # False -> position far away
        next_bool = abs(np.linalg.norm(posns1[i] - posns2[i])) < stepsize
        # If atleast one atom is far away, return_bool is set to false
        return_bool = return_bool and next_bool
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
    print('printing constraint vector')
    print(con_tan)
    c = FixedMode(con_tan)
    cur_img.set_constraint(c)

def get_next_img(last_img, final_img, stepsize, calc_fn):
    cur_img = last_img.copy()
    dir_vec = normalize_vecs_as_set(two_pt_tangent(cur_img, final_img))
    print('print dir_vec')
    print(dir_vec)
    add_vec_to_posns(cur_img, dir_vec*stepsize)
    print('printing new coordinates')
    print(cur_img.get_positions())
    set_constrain_tangent(last_img, cur_img, final_img)
    cur_img.set_calculator(calc_fn())
    return cur_img

def opt_image(img, optimizer, fmax, logname, n):
    f = open(logname, 'a')
    f.write(ctime() + ': ' + 'optimizing image ' + str(n) + '\n')
    f.close()
    dyn = optimizer(img)
    dyn.run(fmax=fmax)

def setup_next_img(images, final_img, stepsize, calc_fn, logname):
    next_img = get_next_img(images[-1], final_img, stepsize, calc_fn)
    cont_bool = not nearly_same_posns(next_img.get_positions(), final_img.get_positions(), stepsize)
    if cont_bool:
        images.append(next_img)
    else:
        f = open(logname, 'a')
        f.write(ctime() + ': ' + 'Next image will be too similar to given final, breaking \n')
        f.close()
    return cont_bool