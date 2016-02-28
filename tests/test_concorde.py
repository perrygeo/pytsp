import json
import os

import pytest

from pytsp import atsp_tsp, run, dumps_matrix


@pytest.fixture
def matrix():
    thisdir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(thisdir, "matrix.json")) as src:
        matrix = json.loads(src.read())
    return matrix


def test_tour_concorde(matrix):
    matrix_sym = atsp_tsp(matrix, strategy="avg")
    outf = "/tmp/myroute_concorde.tsp"
    with open(outf, 'w') as dest:
        dest.write(dumps_matrix(matrix_sym, name="My Route"))
    tour = run(outf, start=10, solver="concorde")

    assert tour['solution'] == 102975
    assert tour['tour'][0] == 10
    # assert tour['tour'] in tours  # can't do this, not deterministic 

def test_tour_LKH(matrix):
    matrix_sym = atsp_tsp(matrix, strategy="avg")
    outf = "/tmp/myroute_lkh.tsp"
    with open(outf, 'w') as dest:
        dest.write(dumps_matrix(matrix_sym, name="My Route"))
    tour = run(outf, start=10, solver="lkh")

    assert tour['solution'] == 102975
    assert tour['tour'][0] == 10
    # assert tour['tour'] in tours  # can't do this, not deterministic 
