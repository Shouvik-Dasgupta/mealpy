#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu" at 11:34, 11/07/2021                                                               %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Nguyen_Thieu2                                  %
#       Github:     https://github.com/thieu1995                                                        %
# ------------------------------------------------------------------------------------------------------%

from mealpy.evolutionary_based.GA import BaseGA
from mealpy.utils.visualize import *
from numpy import sum, mean, sqrt


## Define your own fitness function
# Multi-objective but single fitness/target value. By using weighting method to convert from multiple objectives to single target

def obj_function(solution):
    f1 = (sum(solution**2) - mean(solution)) / len(solution)
    f2 = sum(sqrt(abs(solution)))
    f3 = sum(mean(solution**2) - solution)
    return [f1, f2, f3]


## Setting parameters
verbose = True
epoch = 100
pop_size = 50

lb1 = [-10, -5, -15, -20, -10, -15, -10, -30]
ub1 = [10, 5, 15, 20, 50, 30, 100, 85]

optimizer = BaseGA(obj_function, lb1, ub1, "min", verbose, epoch, pop_size, obj_weight=[0.2, 0.5, 0.3])
best_position, best_fitness, g_best_fit_list, c_best_fit_list = optimizer.train()
print(best_position)

## Draw convergence chart for globest solution found so far in each previous generation
export_convergence_chart(optimizer.history_list_g_best_fit, title='Global Best Fitness', filename="Global-best-convergence-chart")

# Parameter for this function
# data: optimizer.history_list_g_best_fit -> List of global best fitness found so far in each previous generation
# title: title of the figure
# linestyle: matplotlib API, default = "-"
# color: matplotlib API, default = "b"  -> Blue
# x_label: string, default = "#Iteration"
# y_label: string, default = "Function Value"
# filename: string, default = "convergence_chart"
# exts: matplotlib API, default = (".png", ".pdf") --> save figure in format of png and pdf
# verbose: show the figure on Python IDE, default = True

## Draw convergence chart for current best solution in each generation
export_convergence_chart(optimizer.history_list_c_best_fit, title='Local Best Fitness', filename='Current-best-convergence-chart')

## Draw runtime for each generation
export_convergence_chart(optimizer.history_list_epoch_time, title='Runtime chart', y_label="Second", filename='Runtime-per-epoch-chart')






