import pytest
import json

from pyconcorde import atsp_tsp, run_concorde, dumps_matrix


@pytest.fixture
def matrix():
    with open("tests/matrix.json") as src:
        matrix = json.loads(src.read())
    return matrix


def test_tour(matrix):
    matrix_sym = atsp_tsp(matrix, strategy="avg")
    outf = "/tmp/myroute.tsp"
    with open(outf, 'w') as dest:
        dest.write(dumps_matrix(matrix_sym, name="My Route"))
    tour = run_concorde(outf, start=10)

    assert tour['solution'] == 3485031.00
    assert tour['tour'][0] == 10
    # assert tour['tour'] in tours  # can't do this, not deterministic 
