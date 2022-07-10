from abc import ABC, abstractmethod
from time import time

"""
The optimization functions generally take a function that returns a StopCriterion
This is because each StopCriterion has an internal state that has to be initialized at the start of the optimization function
If we gave the optimizaton functions an instance directly, it's possible it has already been initialized (it's impossible to know from inside the function)
Well, we don't really need that, as we are the only ones using the code and wouldn't make that mistake, but whatever
"""

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
Kinda crappy, but it is what one article uses (or at least what I got from it)
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
