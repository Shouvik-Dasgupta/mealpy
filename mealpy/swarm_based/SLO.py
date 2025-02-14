#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu" at 15:05, 03/06/2021                                                               %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Nguyen_Thieu2                                  %
#       Github:     https://github.com/thieu1995                                                        %
# ------------------------------------------------------------------------------------------------------%

import numpy as np
from math import gamma
from copy import deepcopy
from mealpy.optimizer import Optimizer


class BaseSLO(Optimizer):
    """
        The original version of: Sea Lion Optimization Algorithm (SLO)
            (Sea Lion Optimization Algorithm)
        Link:
            https://www.researchgate.net/publication/333516932_Sea_Lion_Optimization_Algorithm
            DOI: 10.14569/IJACSA.2019.0100548
        Notes:
            + The original paper is unclear in some equations and parameters
            + This version is based on my expertise
    """
    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
        """
        Args:
            problem ():
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
            **kwargs ():
        """
        super().__init__(problem, kwargs)
        self.nfe_per_epoch = pop_size
        self.sort_flag = False

        self.epoch = epoch
        self.pop_size = pop_size

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        c = 2 - 2 * epoch / self.epoch
        t0 = np.random.rand()
        v1 = np.sin(2 * np.pi * t0)
        v2 = np.sin(2 * np.pi * (1 - t0))
        SP_leader = np.abs(v1 * (1 + v2) / v2)  # In the paper this is not clear how to calculate

        pop_new = []
        for idx in range(0, self.pop_size):
            if SP_leader < 0.25:
                if c < 1:
                    pos_new = self.g_best[self.ID_POS] - c * np.abs(2 * np.random.rand() *
                                                                    self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
                else:
                    ri = np.random.choice(list(set(range(0, self.pop_size)) - {idx}))  # random index
                    pos_new = self.pop[ri][self.ID_POS] - c * np.abs(2 * np.random.rand() *
                                                                self.pop[ri][self.ID_POS] - self.pop[idx][self.ID_POS])
            else:
                pos_new = np.abs(self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS]) * \
                          np.cos(2 * np.pi * np.random.uniform(-1, 1)) + self.g_best[self.ID_POS]
            # In the paper doesn't check also doesn't update old solution at this point
            pos_new = self.amend_position_random(pos_new)
            pop_new.append([pos_new, None])
        pop_new = self.update_fitness_population(pop_new)
        self.pop = self.greedy_selection_population(self.pop, pop_new)


class ModifiedSLO(Optimizer):
    """
        My modified version of: Sea Lion Optimization (ISLO)
            (Sea Lion Optimization Algorithm)
        Noted:
            + Using the idea of shrink encircling combine with levy flight techniques
            + Also using the idea of local best in PSO
    """
    ID_LOC_POS = 2
    ID_LOC_FIT = 3

    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
        """
        Args:
            problem ():
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
            **kwargs ():
        """
        super().__init__(problem, kwargs)
        self.nfe_per_epoch = pop_size
        self.sort_flag = False

        self.epoch = epoch
        self.pop_size = pop_size

    def create_solution(self):
        """
        Returns:
            The position position with 2 element: index of position/location and index of fitness wrapper
            The general format: [position, [target, [obj1, obj2, ...]]]

        ## To get the position, fitness wrapper, target and obj list
        ##      A[self.ID_POS]                  --> Return: position
        ##      A[self.ID_FIT]                  --> Return: [target, [obj1, obj2, ...]]
        ##      A[self.ID_FIT][self.ID_TAR]     --> Return: target
        ##      A[self.ID_FIT][self.ID_OBJ]     --> Return: [obj1, obj2, ...]
        """
        ## Increase exploration at the first initial population using opposition-based learning.
        position = np.random.uniform(self.problem.lb, self.problem.ub)
        fitness = self.get_fitness_position(position=position)
        local_pos = self.problem.lb + self.problem.ub - position
        local_fit = self.get_fitness_position(local_pos)
        if fitness < local_fit:
            return [local_pos, local_fit, position, fitness]
        else:
            return [position, fitness, local_pos, local_fit]

    def _shrink_encircling_levy__(self, current_pos, epoch, dist, c, beta=1):
        up = gamma(1 + beta) * np.sin(np.pi * beta / 2)
        down = (gamma((1 + beta) / 2) * beta * np.power(2, (beta - 1) / 2))
        xich_ma_1 = np.power(up / down, 1 / beta)
        xich_ma_2 = 1
        a = np.random.normal(0, xich_ma_1, 1)
        b = np.random.normal(0, xich_ma_2, 1)
        LB = 0.01 * a / (np.power(np.abs(b), 1 / beta)) * dist * c
        D = np.random.uniform(self.problem.lb, self.problem.ub)
        levy = LB * D
        return (current_pos - np.sqrt(epoch + 1) * np.sign(np.random.random(1) - 0.5)) * levy

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """

        c = 2 - 2 * epoch / self.epoch
        if c > 1:
            pa = 0.3  # At the beginning of the process, the probability for shrinking encircling is small
        else:
            pa = 0.7  # But at the end of the process, it become larger. Because sea lion are shrinking encircling prey
        SP_leader = np.random.uniform(0, 1)

        pop_new = []
        for idx in range(0, self.pop_size):
            agent = deepcopy(self.pop[idx])
            if SP_leader >= 0.6:
                pos_new = np.cos(2 * np.pi * np.random.normal(0, 1)) * \
                          np.abs(self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS]) + self.g_best[self.ID_POS]
            else:
                if np.random.uniform() < pa:
                    dist1 = np.random.uniform() * np.abs(2 * self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
                    pos_new = self._shrink_encircling_levy__(self.pop[idx][self.ID_POS], epoch, dist1, c)
                else:
                    rand_SL = self.pop[np.random.randint(0, self.pop_size)][self.ID_LOC_POS]
                    rand_SL = 2 * self.g_best[self.ID_POS] - rand_SL
                    pos_new = rand_SL - c * np.abs(np.random.uniform() * rand_SL - self.pop[idx][self.ID_POS])
            agent[self.ID_POS] = self.amend_position_random(pos_new)
            pop_new.append(agent)
        pop_new = self.update_fitness_population(pop_new)

        for idx in range(0, self.pop_size):
            if self.compare_agent(pop_new[idx], self.pop[idx]):
                self.pop[idx] = deepcopy(pop_new[idx])
                if self.compare_agent(pop_new[idx], [None, self.pop[idx][self.ID_LOC_FIT]]):
                    self.pop[idx][self.ID_LOC_POS] = deepcopy(pop_new[idx][self.ID_POS])
                    self.pop[idx][self.ID_LOC_FIT] = deepcopy(pop_new[idx][self.ID_FIT])


class ISLO(ModifiedSLO):
    """
        My improved version of: Improved Sea Lion Optimization Algorithm (ISLO)
            (Sea Lion Optimization Algorithm)
        Link:
            https://www.researchgate.net/publication/333516932_Sea_Lion_Optimization_Algorithm
            DOI: 10.14569/IJACSA.2019.0100548
    """

    def __init__(self, problem, epoch=10000, pop_size=100, c1=1.2, c2=1.2, **kwargs):
        """
        Args:
            problem ():
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
            **kwargs ():
        """
        super().__init__(problem, epoch, pop_size, **kwargs)
        self.nfe_per_epoch = pop_size
        self.sort_flag = False

        self.epoch = epoch
        self.pop_size = pop_size
        self.c1 = c1
        self.c2 = c2

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        c = 2 - 2 * epoch / self.epoch
        t0 = np.random.rand()
        v1 = np.sin(2 * np.pi * t0)
        v2 = np.sin(2 * np.pi * (1 - t0))
        SP_leader = np.abs(v1 * (1 + v2) / v2)

        pop_new = []
        for idx in range(0, self.pop_size):
            agent = deepcopy(self.pop[idx])
            if SP_leader < 0.5:
                if c < 1:  # Exploitation improved by historical movement + global best affect
                    # pos_new = g_best[self.ID_POS] - c * np.abs(2 * rand() * g_best[self.ID_POS] - pop[i][self.ID_POS])
                    dif1 = np.abs(2 * np.random.rand() * self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
                    dif2 = np.abs(2 * np.random.rand() * self.pop[idx][self.ID_LOC_POS] - self.pop[idx][self.ID_POS])
                    pos_new = self.c1 * np.random.rand() * (self.pop[idx][self.ID_POS] - c * dif1) + \
                              self.c2 * np.random.rand() * (self.pop[idx][self.ID_POS] - c * dif2)
                else:  # Exploration improved by opposition-based learning
                    # Create a new solution by equation below
                    # Then create an opposition solution of above solution
                    # Compare both of them and keep the good one (Searching at both direction)
                    pos_new = self.g_best[self.ID_POS] + c * np.random.normal(0, 1, self.problem.n_dims) * \
                              (self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
                    fit_new = self.get_fitness_position(self.amend_position_faster(pos_new))
                    pos_new_oppo = self.problem.lb + self.problem.ub - self.g_best[self.ID_POS] + \
                                   np.random.rand() * (self.g_best[self.ID_POS] - pos_new)
                    fit_new_oppo = self.get_fitness_position(self.amend_position_faster(pos_new_oppo))
                    if self.compare_agent([pos_new_oppo, fit_new_oppo], [pos_new, fit_new]):
                        pos_new = pos_new_oppo
            else:  # Exploitation
                pos_new = self.g_best[self.ID_POS] + np.cos(2 * np.pi * np.random.uniform(-1, 1)) * \
                          np.abs(self.g_best[self.ID_POS] - self.pop[idx][self.ID_POS])
            agent[self.ID_POS] = self.amend_position_random(pos_new)
            pop_new.append(agent)
        pop_new = self.update_fitness_population(pop_new)

        for idx in range(0, self.pop_size):
            if self.compare_agent(pop_new[idx], self.pop[idx]):
                self.pop[idx] = deepcopy(pop_new[idx])
                if self.compare_agent(pop_new[idx], [None, self.pop[idx][self.ID_LOC_FIT]]):
                    self.pop[idx][self.ID_LOC_POS] = deepcopy(pop_new[idx][self.ID_POS])
                    self.pop[idx][self.ID_LOC_FIT] = deepcopy(pop_new[idx][self.ID_FIT])

