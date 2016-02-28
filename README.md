# pytsp

A python interface to external solvers for the **traveling salesman problem**.

Support for 
* Concorde, available free of charge for research use at http://www.math.uwaterloo.ca/tsp/concorde.html
* LKH, available free of charge for research use at http://www.akira.ruc.dk/~keld/research/LKH/

It is the user's responsibility to install these solvers and ensure compliance with the terms of use.
When done installing
make sure the binaries (`concorde` and/or `LKH`) are on your `PATH` or set `CONCORDE` and/or `LKH` environment variables to their respective binaries.

## Overview

The traveling salesman problem (TSP) seeks to find an optimal route between a set of point locations.

You start with a matrix representing the distance between all your points of interest. If you have `n` points,
your matrix will be an `n x n` two dimensional list.

    matrix = [
        [ 0,    2910, 4693 ],
        [ 2903, 0,    5839 ],
        [ 4695, 5745, 0    ]]

This matrix can be generated using e.g. the Mapbox [Distance API](https://github.com/mapbox/mapbox-sdk-py#distance)

To find the optimal route using pyconcorde, import the necessary modules

    from pyconcorde import atsp_tsp, run_concorde, dumps_matrix

Then we must convert the asymetrical TSP to a symetrical problem. The asymetrical case is not well researched and is not supported by Concorde. Furthermore, in practical application, traffic and road conditions will have more impact than asymmetry of travel times in most cases.

    matrix_sym = atsp_tsp(matrix, strategy="avg")

Next, write temporary file in the `tsp` format

    outf = "/tmp/myroute.tsp"
    with open(outf, 'w') as dest:
        dest.write(dumps_matrix(matrix_sym, name="My Route"))

Finally, run the optimization with concorde

    tour = run(outf, start=10, solver="concorde")

or with LKH

    tour = run(outf, start=10, solver="LKH")

The tour dictionary contains these keys:

* `tour['tour']` is an ordered list of point indicies. The optimal route is acheived when traveling between the points in this order.
* `tour['solution']` is the overall distance of the optimal solution. 
* `tour['metadata']` provides the raw output of Concorde which is useful for debugging.

