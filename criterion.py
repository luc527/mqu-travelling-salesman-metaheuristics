from abc import ABC, abstractmethod
from time import time

class StopCriterion(ABC):
    @abstractmethod
    def update(self, solution_weight: int):
        pass

    @abstractmethod
    def stop(self) -> bool:
        pass

class IterationCriterion(StopCriterion):
    def __init__(self, max_iters):
        self.max_iters = max_iters
        self.iters     = 0

    def update(self, solution_weight: int):
        self.iters += 1

    def stop(self) -> bool:
        return self.iters >= self.max_iters

"""
Time in seconds
Not a very precise implementation, but close enough
"""
class TimeCriterion(StopCriterion):
    def __init__(self, time_limit):
        self.start_time = time()
        self.time_limit = time_limit

    def update(self, solution_weight: int):
        pass

    def stop(self) -> bool:
        return time() - self.start_time >= self.time_limit

"""
Will stop after seeing the current best solution k times
Crappy for local search, but it is what one article uses
"""
class TimesSeenBestCriterion(StopCriterion):
    def __init__(self, k):
        self.k = k
        self.times_seen = 0
        self.current_best_weight = float('inf')

    def update(self, solution_weight: int):
        if solution_weight == self.current_best_weight:
            self.times_seen += 1
        elif solution_weight < self.current_best_weight:
            self.current_best_weight = solution_weight
            self.times_seen = 0

    def stop(self) -> bool:
        return self.times_seen >= self.k
