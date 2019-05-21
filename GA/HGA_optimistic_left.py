from GA_optimistic_left import *
import copy


class HGA_optimistic_left(GA_optimistic_left):
    def __init__(self):
        GA.__init__(self)
        self.prevSolution = None
        self.prevAvgL = -1
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
        self.prevAvgL = -1
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
                self.currentAvgL = reduce(lambda a, b: a + b.relL, self.population, 0) / len(
                    self.population)
                self.prevAvgL = self.currentAvgL
        # else prevSollution != None
        # and of currentSolution != None
        elif self.currentSolution != None:
            self.currentAvgL = reduce(lambda a, b: a + b.relL, self.population, 0) / len(self.population)
            if self.currentIter > 1:
                curr_relL = self.currentSolution.relL
                prev_relL = self.prevSolution.relL
                bestDiff = (curr_relL - prev_relL) / curr_relL
                avgLDiff = (self.currentAvgL - self.prevAvgL) / self.currentAvgL
                if bestDiff >= 0.01:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.max
                    self.algconf.Pcross.cur = self.algconf.Pcross.max
                else:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.min
                    self.algconf.Pcross.cur = self.algconf.Pcross.min
                if avgLDiff >= 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.min
                    self.algconf.Pmut.cur = self.algconf.Pmut.min
                elif avgLDiff > -0.03 and avgLDiff < 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.norm
                    self.algconf.Pmut.cur = self.algconf.Pmut.norm
                elif avgLDiff <= -0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.max
                    self.algconf.Pmut.cur = self.algconf.Pmut.max
            self.prevSolution = copy.deepcopy(self.currentSolution)
            self.prevAvgL = self.currentAvgL
        # somehow prev != None, curr == None
        else:
            self.algconf.crossPercent.cur = self.algconf.crossPercent.max
            self.algconf.Pcross.cur = self.algconf.Pcross.max
            self.algconf.mutPercent.cur = self.algconf.mutPercent.max
            self.algconf.Pmut.cur = self.algconf.Pmut.max

