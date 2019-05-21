from GA_optimistic import *
import copy


class HGA_optimistic(GA_optimistic):
    def __init__(self):
        GA.__init__(self)
        self.prevSolution = None
        self.prevAvgR = -1
        self.currentAvg = -1

    def Step(self):
        self._select()
        self._recombine()
        self._mutate()
        self._evalPopulation()
        self._fuzzyLogic()

    def Clear(self):
        GA.Clear(self)
        self.prevSolution = None
        self.prevAvgR = -1
        self.currentAvg = -1
        self.algconf.crossPercent.cur = self.algconf.crossPercent.norm
        self.algconf.Pcross.cur = self.algconf.Pcross.norm

    def _fuzzyLogic(self):
        # if no prev solution, there's nothing to compare
        if self.prevSolution == None:
            self.algconf.crossPercent.cur = self.algconf.crossPercent.max
            self.algconf.Pcross.cur = self.algconf.Pcross.max
            self.algconf.mutPercent.cur = self.algconf.mutPercent.max
            self.algconf.Pmut.cur = self.algconf.Pmut.max
            # if curr solution exists, save it as prev solution
            if self.currentSolution != None:
                self.prevSolution = copy.deepcopy(self.currentSolution)
                self.currentAvgR = reduce(lambda a, b: a + b.relR, self.population, 0) / len(
                    self.population)
                self.prevAvgR = self.currentAvgR
        # else prevSollution != None
        # and of currentSolution != None
        elif self.currentSolution != None:
            self.currentAvgR = reduce(lambda a, b: a + b.relR, self.population, 0) / len(self.population)
            if self.currentIter > 1:
                curr_relR = self.currentSolution.relR
                prev_relR = self.prevSolution.relR
                bestDiff = (curr_relR - prev_relR) / curr_relR
                avgRDiff = (self.currentAvgR - self.prevAvgR) / self.currentAvgR
                if bestDiff >= 0.01:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.max
                    self.algconf.Pcross.cur = self.algconf.Pcross.max
                else:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.min
                    self.algconf.Pcross.cur = self.algconf.Pcross.min
                if avgRDiff >= 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.min
                    self.algconf.Pmut.cur = self.algconf.Pmut.min
                elif avgRDiff > -0.03 and avgRDiff < 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.norm
                    self.algconf.Pmut.cur = self.algconf.Pmut.norm
                elif avgRDiff <= -0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.max
                    self.algconf.Pmut.cur = self.algconf.Pmut.max
            self.prevSolution = copy.deepcopy(self.currentSolution)
            self.prevAvgR = self.currentAvgR
        # somehow prev != None, curr == None
        else:
            self.algconf.crossPercent.cur = self.algconf.crossPercent.max
            self.algconf.Pcross.cur = self.algconf.Pcross.max
            self.algconf.mutPercent.cur = self.algconf.mutPercent.max
            self.algconf.Pmut.cur = self.algconf.Pmut.max

