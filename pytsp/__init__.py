import numpy as np
import subprocess
import os
import math

template = """NAME: {name}
TYPE: TSP
COMMENT: {name}
DIMENSION: {n_cities}
EDGE_WEIGHT_TYPE: EXPLICIT
EDGE_WEIGHT_FORMAT: LOWER_DIAG_ROW
EDGE_WEIGHT_SECTION
{matrix_s}EOF"""

class TSPSolverNotFound(IOError):
    pass


def atsp_tsp(matrix, strategy="avg"):
    """ convert an asymterical tsp to symetrical
    """

    arr = np.array(matrix)

    if strategy == 'avg':
        rarr = np.flipud(np.rot90(arr))
        avg = ((arr + rarr) / 2)
        # keep it < 32768 to stay within 16bit int
        scale = 32768.0 / avg.max()
        if scale > 1.0:
            scale = 1.0
        avg = (avg * scale).astype('i')
        return avg

    if strategy == 'cutoff':
        return arr

    if strategy == "dummy":
        """
        Jonker and Volgenant 1983
        """
        raise Exception("This is broken")
        # make very large number to simulate inf
        big = arr.sum() * 2
        nines = (10**math.ceil(math.log10(big)))-1
        np.fill_diagonal(arr, -1 * nines)
        newarr = np.ones(shape=tuple(np.array(arr.shape) * 2)) * nines
        np.fill_diagonal(newarr, 0)
        newarr[-1 * arr.shape[0]:, 0:arr.shape[1]] = arr
        return newarr


def dumps_matrix(arr, name="route"):
    n_cities = arr.shape[0]
    width = len(str(arr.max())) + 1

    assert arr.shape[0] == arr.shape[1]
    assert len(arr.shape) == 2

    # space delimited string
    matrix_s = ""
    for i, row in enumerate(arr.tolist()):
        matrix_s += " ".join(["{0:>{1}}".format((int(elem)), width)
                              for elem in row[:i+1]])
        matrix_s += "\n"

    return template.format(**{'name': name,
                              'n_cities': n_cities,
                              'matrix_s': matrix_s})


def _create_lkh_par(tsp_path, runs=4):
    prefix, _ = os.path.splitext(tsp_path)
    par_path = prefix + ".par"
    out_path = prefix + ".out"
    par = """PROBLEM_FILE = {}
RUNS = {}
TOUR_FILE =  {}
""".format(tsp_path, runs, out_path)
    with open(par_path, 'w') as dest:
        dest.write(par)
    return par_path, out_path


def run(tsp_path, start=None, solver="concorde"):
    bdir = os.path.dirname(tsp_path)
    os.chdir(bdir)

    if solver.lower() == 'concorde':
        CONCORDE = os.environ.get('CONCORDE', 'concorde')
        try:
            output = subprocess.check_output([CONCORDE, tsp_path], shell=False)
        except OSError as exc:
            if "No such file or directory" in str(exc):
                raise TSPSolverNotFound(
                    "{0} is not found on your path or is not executable".format(CONCORDE))

        solf = os.path.join(
            bdir, os.path.splitext(os.path.basename(tsp_path))[0] + ".sol")

        with open(solf) as src:
            sol = src.read()

        raw = [int(x) for x in sol.split()[1:]]  # first is just n cities

        metadata = output.strip().split("\n")
        for line in metadata:
            if line.startswith("Optimal Solution:"):
                solution = float(line.split(":")[1])

    elif solver.lower() == 'lkh':
        LKH = os.environ.get('LKH', 'LKH')
        par_path, out_path = _create_lkh_par(tsp_path)
        try:
            output = subprocess.check_output([LKH, par_path], shell=False)
        except OSError as exc:
            if "No such file or directory" in str(exc):
                raise TSPSolverNotFound(
                    "{0} is not found on your path or is not executable".format(LKH))

        meta = []
        raw = []
        solution = None
        with open(out_path) as src:
            header = True
            for line in src:
                if header:
                    if line.startswith("COMMENT : Length ="):
                        solution = int(line.split(" ")[-1])
                    if line.startswith("TOUR_SECTION"):
                        header = False
                        continue
                    meta.append(line)
                    continue

                else:
                    if line.startswith("-1"):
                        break
                    else:
                        raw.append(int(line.strip()) - 1)  # correct to zero-indexed

        metadata = "".join(meta)

    if start:
        # rotate to the beginning of the route
        while raw[0] != start:
            raw = raw[1:] + raw[:1]

    return {'tour': raw,
            'solution': solution,
            'metadata': metadata}
