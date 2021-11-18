"""
Random distributions
"""
from random import random
import math


class RandomVariable:
    def __init__(self, dist_f):
        self.dist_f = dist_f

    def __call__(self, *args):
        if self.dist_f == 'uniform':
            return self._uniform(args[0], args[1])
        elif self.dist_f == 'exp':
            return self._exp(args[0])
        elif self.dist_f == 'normal':
            return self._normal(args[0], args[1])
        else:
            raise NotImplementedError('Method not implemented')

    def _uniform(self, a, b):
       return a + (b - a) * random() 

    def _exp(self, lambda_):
        return -(1 / lambda_) * math.log(random())

    def _normal(self, u, o):
        while(True):
            y1 = self._exp(1)
            y2 = self._exp(1)
            v = y2 - (((y1 - 1) ** 2) / 2)
            if v > 0:
                return u + y1 * (o ** 0.5)


def choice(prob_arr):
    u = random()
    interval = 0
    for i, v in enumerate(prob_arr):
        interval += v
        if u <= interval:
            return i
    raise Exception("sum(prob_arr) should be equal to 1.")

