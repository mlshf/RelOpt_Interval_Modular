from GA_single import *
import copy


class HGA_single(GA_single):
    def __init__(self):
        GA.__init__(self)
        self.prevSolution = None
        self.prevAvgSinObj = -1
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
        self.prevAvgSinObj = -1
        self.currentAvg = -1
        self.algconf.crossPercent.cur = self.algconf.crossPercent.norm
        self.algconf.Pcross.cur = self.algconf.Pcross.norm

    def _fuzzyLogic(self):
        ro = Algorithm.algconf.ro
        # if no prev solution, there's nothing to compare
        if self.prevSolution == None:
            self.algconf.crossPercent.cur = self.algconf.crossPercent.max
            self.algconf.Pcross.cur = self.algconf.Pcross.max
            self.algconf.mutPercent.cur = self.algconf.mutPercent.max
            self.algconf.Pmut.cur = self.algconf.Pmut.max
            # if curr solution exists, save it as prev solution
            if self.currentSolution != None:
                self.prevSolution = copy.deepcopy(self.currentSolution)
                self.currentAvgSinObj = reduce(lambda a, b: a + ( ro * b.relL + ( 1 - ro ) * ( b.relL + b.relR ) / 2), self.population, 0) / len(
                    self.population)
                self.prevAvgSinObj = self.currentAvgSinObj
        # else prevSollution != None
        # and of currentSolution != None
        elif self.currentSolution != None:
            self.currentAvgSinObj = reduce(lambda a, b: a + ( ro * b.relL + ( 1 - ro ) * ( b.relL + b.relR ) / 2), self.population, 0) / len(self.population)
            if self.currentIter > 1:
                curr_relSinObj = ( ro * self.currentSolution.relL + ( 1 - ro ) * ( self.currentSolution.relL + self.currentSolution.relR ) / 2)
                prev_relSinObj = ( ro * self.prevSolution.relL + ( 1 - ro ) * ( self.prevSolution.relL + self.prevSolution.relR ) / 2)
                bestDiff = (curr_relSinObj - prev_relSinObj) / curr_relSinObj
                avgSinObjDiff = (self.currentAvgSinObj - self.prevAvgSinObj) / self.currentAvgSinObj
                if bestDiff >= 0.01:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.max
                    self.algconf.Pcross.cur = self.algconf.Pcross.max
                else:
                    self.algconf.crossPercent.cur = self.algconf.crossPercent.min
                    self.algconf.Pcross.cur = self.algconf.Pcross.min
                if avgSinObjDiff >= 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.min
                    self.algconf.Pmut.cur = self.algconf.Pmut.min
                elif avgSinObjDiff > -0.03 and avgSinObjDiff < 0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.norm
                    self.algconf.Pmut.cur = self.algconf.Pmut.norm
                elif avgSinObjDiff <= -0.03:
                    self.algconf.mutPercent.cur = self.algconf.mutPercent.max
                    self.algconf.Pmut.cur = self.algconf.Pmut.max
            self.prevSolution = copy.deepcopy(self.currentSolution)
            self.prevAvgSinObj = self.currentAvgSinObj
        # somehow prev != None, curr == None
        else:
            self.algconf.crossPercent.cur = self.algconf.crossPercent.max
            self.algconf.Pcross.cur = self.algconf.Pcross.max
            self.algconf.mutPercent.cur = self.algconf.mutPercent.max
            self.algconf.Pmut.cur = self.algconf.Pmut.max

