#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Thieu Nguyen" at 07:03, 18/03/2020                                                        %
#                                                                                                       %
#       Email:      nguyenthieu2102@gmail.com                                                           %
#       Homepage:   https://www.researchgate.net/profile/Thieu_Nguyen6                                  %
#       Github:     https://github.com/thieu1995                                                        %
#-------------------------------------------------------------------------------------------------------%

import numpy as np
from mealpy.optimizer import Optimizer


class BaseEO(Optimizer):
    """
        The original version of: Equilibrium Optimizer (EO)
            (Equilibrium Optimizer: A Novel Optimization Algorithm)
        Link:
            https://doi.org/10.1016/j.knosys.2019.105190
            https://www.mathworks.com/matlabcentral/fileexchange/73352-equilibrium-optimizer-eo
    """

    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
        """
        Args:
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
        """
        super().__init__(problem, kwargs)
        self.nfe_per_epoch = pop_size
        self.sort_flag = False

        self.epoch = epoch
        self.pop_size = pop_size
        ## Fixed parameter proposed by authors
        self.V = 1
        self.a1 = 2
        self.a2 = 1
        self.GP = 0.5

    def make_equilibrium_pool(self, list_equilibrium=None):
        pos_list = [item[self.ID_POS] for item in list_equilibrium]
        pos_mean = np.mean(pos_list, axis=0)
        fit = self.get_fitness_position(pos_mean)
        list_equilibrium.append([pos_mean, fit])
        return list_equilibrium

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        # ---------------- Memory saving-------------------  make equilibrium pool
        _, c_eq_list, _ = self.get_special_solutions(self.pop, best=4)
        c_pool = self.make_equilibrium_pool(c_eq_list)
        # Eq. 9
        t = (1 - epoch / self.epoch) ** (self.a2 * epoch / self.epoch)
        pop_new = []
        for idx in range(0, self.pop_size):
            lamda = np.random.uniform(0, 1, self.problem.n_dims)  # lambda in Eq. 11
            r = np.random.uniform(0, 1, self.problem.n_dims)  # r in Eq. 11
            c_eq = c_pool[np.random.randint(0, len(c_pool))][self.ID_POS]  # random selection 1 of candidate from the pool
            f = self.a1 * np.sign(r - 0.5) * (np.exp(-lamda * t) - 1.0)  # Eq. 11
            r1 = np.random.uniform()
            r2 = np.random.uniform()  # r1, r2 in Eq. 15
            gcp = 0.5 * r1 * np.ones(self.problem.n_dims) * (r2 >= self.GP)  # Eq. 15
            g0 = gcp * (c_eq - lamda * self.pop[idx][self.ID_POS])  # Eq. 14
            g = g0 * f  # Eq. 13
            pos_new = c_eq + (self.pop[idx][self.ID_POS] - c_eq) * f + (g * self.V / lamda) * (1.0 - f)  # Eq. 16
            pos_new = self.amend_position_faster(pos_new)
            pop_new.append([pos_new, None])
        self.pop = self.update_fitness_population(pop_new)


class ModifiedEO(BaseEO):
    """
        Original version of: Modified Equilibrium Optimizer (MEO)
            (An efficient equilibrium optimizer with mutation strategy for numerical optimization)
    Link:
        https://doi.org/10.1016/j.asoc.2020.106542
    """

    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
        """
        Args:
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
        """
        super().__init__(problem, epoch, pop_size, **kwargs)
        self.nfe_per_epoch = 2*pop_size
        self.sort_flag = False

        self.pop_len = int(self.pop_size / 3)

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        # ---------------- Memory saving-------------------  make equilibrium pool
        _, c_eq_list, _ = self.get_special_solutions(self.pop, best=4)
        c_pool = self.make_equilibrium_pool(c_eq_list)

        # Eq. 9
        t = (1 - epoch / self.epoch) ** (self.a2 * epoch / self.epoch)

        pop_new = []
        for idx in range(0, self.pop_size):
            lamda = np.random.uniform(0, 1, self.problem.n_dims)  # lambda in Eq. 11
            r = np.random.uniform(0, 1, self.problem.n_dims)  # r in Eq. 11
            c_eq = c_pool[np.random.randint(0, len(c_pool))][self.ID_POS]  # random selection 1 of candidate from the pool
            f = self.a1 * np.sign(r - 0.5) * (np.exp(-lamda * t) - 1.0)  # Eq. 11
            r1 = np.random.uniform()
            r2 = np.random.uniform()  # r1, r2 in Eq. 15
            gcp = 0.5 * r1 * np.ones(self.problem.n_dims) * (r2 >= self.GP)  # Eq. 15
            g0 = gcp * (c_eq - lamda * self.pop[idx][self.ID_POS])  # Eq. 14
            g = g0 * f  # Eq. 13
            pos_new = c_eq + (self.pop[idx][self.ID_POS] - c_eq) * f + (g * self.V / lamda) * (1.0 - f)  # Eq. 16
            pos_new = self.amend_position_faster(pos_new)
            pop_new.append([pos_new, None])
        pop_new = self.update_fitness_population(pop_new)

        ## Sort the updated population based on fitness
        _, pop_s1, _ = self.get_special_solutions(pop_new, best=self.pop_len)

        ## Mutation scheme
        pop_s2_new = []
        for i in range(0, self.pop_len):
            pos_new = pop_s1[i][self.ID_POS] * (1 + np.random.normal(0, 1, self.problem.n_dims))  # Eq. 12
            pos_new = self.amend_position_faster(pos_new)
            pop_s2_new.append([pos_new, None])
        pop_s2 = self.update_fitness_population(pop_s2_new)

        ## Search Mechanism
        pos_s1_list = [item[self.ID_POS] for item in pop_s1]
        pos_s1_mean = np.mean(pos_s1_list, axis=0)
        pop_s3 = []
        for i in range(0, self.pop_len):
            pos_new = (c_pool[0][self.ID_POS] - pos_s1_mean) - np.random.random() * \
                      (self.problem.lb + np.random.random() * (self.problem.ub - self.problem.lb))
            pos_new = self.amend_position_faster(pos_new)
            pop_s3.append([pos_new, None])
        pop_s3 = self.update_fitness_population(pop_s3)

        ## Construct a new population
        self.pop = pop_s1 + pop_s2 + pop_s3
        n_left = self.pop_size - len(self.pop)
        idx_selected = np.random.choice(range(0, len(c_pool)), n_left, replace=False)
        for i in range(0, n_left):
            self.pop.append(c_pool[idx_selected[i]])


class AdaptiveEO(BaseEO):
    """
        Original version of: Adaptive Equilibrium Optimization (AEO)
            (A novel interdependence based multilevel thresholding technique using adaptive equilibrium optimizer)
    Link:
        https://doi.org/10.1016/j.engappai.2020.103836
    """

    def __init__(self, problem, epoch=10000, pop_size=100, **kwargs):
        """
        Args:
            epoch (int): maximum number of iterations, default = 10000
            pop_size (int): number of population size, default = 100
        """
        super().__init__(problem, epoch, pop_size, **kwargs)
        self.nfe_per_epoch = pop_size
        self.sort_flag = False

        self.pop_len = int(self.pop_size / 3)

    def evolve(self, epoch):
        """
        Args:
            epoch (int): The current iteration
        """
        # ---------------- Memory saving-------------------  make equilibrium pool
        _, c_eq_list, _ = self.get_special_solutions(self.pop, best=4)
        c_pool = self.make_equilibrium_pool(c_eq_list)

        # Eq. 9
        t = (1 - epoch / self.epoch) ** (self.a2 * epoch / self.epoch)

        ## Memory saving, Eq 20, 21
        t = (1 - epoch / self.epoch) ** (self.a2 * epoch / self.epoch)

        pop_new = []
        for idx in range(0, self.pop_size):
            lamda = np.random.uniform(0, 1, self.problem.n_dims)
            r = np.random.uniform(0, 1, self.problem.n_dims)
            c_eq = c_pool[np.random.randint(0, len(c_pool))][self.ID_POS]  # random selection 1 of candidate from the pool
            f = self.a1 * np.sign(r - 0.5) * (np.exp(-lamda * t) - 1.0)  # Eq. 14

            r1 = np.random.uniform()
            r2 = np.random.uniform()
            gcp = 0.5 * r1 * np.ones(self.problem.n_dims) * (r2 >= self.GP)
            g0 = gcp * (c_eq - lamda * self.pop[idx][self.ID_POS])
            g = g0 * f

            fit_average = np.mean([item[self.ID_FIT][self.ID_TAR] for item in self.pop])  # Eq. 19
            pos_new = c_eq + (self.pop[idx][self.ID_POS] - c_eq) * f + (g * self.V / lamda) * (1.0 - f)  # Eq. 9
            if self.pop[idx][self.ID_FIT][self.ID_TAR] >= fit_average:
                pos_new = np.multiply(pos_new, (0.5 + np.random.uniform(0, 1, self.problem.n_dims)))
            pos_new = self.amend_position_faster(pos_new)
            pop_new.append([pos_new, None])
        self.pop = self.update_fitness_population(pop_new)

