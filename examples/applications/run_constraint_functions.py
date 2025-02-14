#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu" at 17:33, 06/11/2021                                                               %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Nguyen_Thieu2                                  %
#       Github:     https://github.com/thieu1995                                                        %
# ------------------------------------------------------------------------------------------------------%

from mealpy.bio_based import SMA
import numpy as np

def obj_function(solution):
    def g1(x):
        return 2*x[0] + 2*x[1] + x[9] + x[10] - 10
    def g2(x):
        return 2 * x[0] + 2 * x[2] + x[9] + x[10] - 10
    def g3(x):
        return 2 * x[1] + 2 * x[2] + x[10] + x[11] - 10
    def g4(x):
        return -8*x[0] + x[9]
    def g5(x):
        return -8*x[1] + x[10]
    def g6(x):
        return -8*x[2] + x[11]
    def g7(x):
        return -2*x[3] - x[4] + x[9]
    def g8(x):
        return -2*x[5] - x[6] + x[10]
    def g9(x):
        return -2*x[7] - x[8] + x[11]

    def violate(value):
        return 0 if value <= 0 else value

    fx = 5 * np.sum(solution[:4]) - 5*np.sum(solution[:4]**2) - np.sum(solution[4:13])

    ## Increase the punishment for g1 and g4 to boost the algorithm (You can choice any constraint instead of g1 and g4)
    fx += violate(g1(solution))**2 + violate(g2(solution)) + violate(g3(solution)) + \
            2*violate(g4(solution)) + violate(g5(solution)) + violate(g6(solution))+ \
            violate(g7(solution)) + violate(g8(solution)) + violate(g9(solution))
    return fx

problem_dict1 = {
    "obj_func": obj_function,
    "lb": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "ub": [1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 100, 100, 1],
    "minmax": "min",
    "verbose": True,
}

## Run the algorithm
model1 = SMA.BaseSMA(problem_dict1, epoch=100, pop_size=50, pr=0.03)
model1.solve()