import random, os, xml.dom.minidom, sys, math
from Common.Module import NONE, NVP01, RB01, Module, Application
from Common.Algorithm import Algorithm
from Common.Schedule import Schedule, Link
from Common.Constraints import TimeConstraints
import itertools
import copy

class System:
    '''
    Represents a system.
    '''
    constraints = []
    def __init__(self):
        self.modules = []
        self.applications = []
        self.relL = -1.0
        self.relR = -1.0
        self.cost = -1
        self.penalty = 1.0
        self.num = 0
        self.hwrc_cost = Module.conf.hwrc_cost
        self.hwrc_relL = Module.conf.hwrc_relL
        self.hwrc_relR = Module.conf.hwrc_relR

    def __eq__(self, other):
        if other == None:
            return False
        for m1, m2 in zip(self.modules, other.modules):
            if not (m1 == m2):
                return False
        return True

    def distance(self, other):
        '''
        :param other: other system.
        :returns: number of different modules for self and other.
        '''
        res = 0
        for m in self.modules:
            if not (m == other.modules[m.num]):
                res += 1
        return res

    def __computeRel(self):
        self.relL = 1.0
        self.relR = 1.0
        for m in self.modules:
            self.relL *= m.relL
            self.relR *= m.relR

    def __computeCost(self):
        self.cost = 0
        self.cost += self.hwrc_cost
        for m in self.modules:
            self.cost += m.cost

    def brokenLag(self):
        for module in self.modules:
            if module.lag > Module.conf.limitlag:
                return True
        return False

    def brokenUtil(self):
        for module in self.modules:
            if module.util > module.limitutil:
                return True
        return False

    def Update(self, use_metamodel=True, add=True):
        '''
        Updates reliability, cost and times.
        Call it after every changing in modules!!!
        :param use_metamodel: if metamodel is used.
        :param add: if we should add new solution to metamodel base.
        '''
        self.__computeCost()
        self.__computeRel()
        #self.__computeTime(use_metamodel, add)
        self.ComputePenalty()

    def ComputePenalty(self):
        self.penalty = 1.0
        for c in self.constraints:
            self.penalty *= c.GetPenalty(self)
        for module in self.modules:
            if module.lag > Module.conf.limitlag:
                self.penalty *= Module.conf.limitlag / module.lag
            if module.util > module.limitutil:
                self.penalty *= module.limitutil / module.util

    def CheckConstraints(self):
        '''
        Checks all constraints.
        '''
        ok = True
        for c in self.constraints:
            ok = c.CheckConstraints(self)
            if not ok:
                break
        if ok and (self.brokenLag() or self.brokenUtil()):
            ok = False
        return ok

    #greedily assign apps to modules according to inter-application message traffic
    def GreedyAssignment(self):
        #P_assigned - list of already assigned applications
        p = -1
        P_ass = []
        #dict of msg size from/to p and apps from list P_ass
        #dict of msg size from p from/to application p
        vc_p = {}
        #fill vc_p
        for i in range(0, len(self.applications)):
            vc_p[ i ] = 0
            #count volumes of from/to messaging for each app
            for j in range(0, len(self.applications)):
                if i <> j:
                    vc_p[ i ] += Application.conf.messaging[(i, j)] + Application.conf.messaging[(j, i)]

        flFirstIter = True
        while (len(P_ass) > 0 and len(P_ass) < len(self.applications)) or flFirstIter:

            vc_p_P_ass = {}
            #count volumes of from/to traffic from apps not in P_ass to apps in P_ass
            for i in range(0, len(self.applications)):
                if not i in P_ass:
                    vc_p_P_ass[i] = 0
                    for j in P_ass:
                        vc_p_P_ass[i] += Application.conf.messaging[(i, j)] + Application.conf.messaging[(j, i)]

            #flag that msging between all applications not in P_ass and those in P_ass
            #is equal to 0
            vc_p_not_ass_to_ass_eq_0 = True
            for i in range(0, len(self.applications)):
                if not i in P_ass:
                    if vc_p_P_ass[i] > 0:
                        vc_p_not_ass_to_ass_eq_0 = False
                        break

            #choose app to assign
            if ( len(P_ass) == 0 ) or vc_p_not_ass_to_ass_eq_0:
                #pick first not assigned app
                for i in range(0, len(self.applications)):
                    if not i in P_ass:
                        p = i
                        break
                #choose app with highest from/to msging
                for i in range(1, len(self.applications)):
                    if not i in P_ass:
                        if vc_p[ i ] > vc_p[ p ]:
                            p = i
            else:
                #pick first not assigned app
                for i in range(0, len(self.applications)):
                    if not i in P_ass:
                        p = i
                        break
                #choose unassigned app with highest traffic from/to P_ass
                for i in range(0, len(self.applications)):
                    if not i in P_ass:
                        if vc_p_P_ass[ i ] > vc_p_P_ass[ p ]:
                            p = i

            #application to be assigned
            app = self.applications[p]

            #calculate vc_p_m - total size of messages transferred between partition p and partitions not assigned to
            #the module it is assigned to
            vc_p_m = {}
            for module in self.modules:
                vc_p_m[module.num] = 0
                for app2 in self.applications:
                    if app2 <> app:
                        if (app2.module >= 0 and app2.module <> module.num) or (app2.module < 0):
                            vc_p_m[module.num] += Application.conf.messaging[(p, app2.num)] + Application.conf.messaging[(app2.num, p)]
            #sort all modules by their vc_p_m
            self.modules.sort(key=lambda x: vc_p_m[x.num])

            #assign app to the module
            for module in self.modules:
                if module.util + app.computeUtil(module.num) < module.limitutil:
                    module.apps.append(app)
                    app.module = module.num
                    P_ass.append(app.num)
                    module.computeUtil()
                    break

            #if app.module < 0 then it's an error and app couldn't be assigned anywhere
            if app.module < 0:
                return False
            #it was needed only for first iteration
            flFirstIter = False
        return True
    
    def RearrangeByRelL(self):
        for module in self.modules:
            module.util = 0
            module.lag = 0
            module.cost = 0
            module.apps = []
        for module in self.modules:
            module.computeRel()
        self.modules.sort(key=lambda x: 1 - x.relL)
        for app in self.applications:
            app.module = -1
            # assign to lowest
            for module in self.modules:
                if module.util + app.computeUtil(module.num) < module.limitutil:
                    module.apps.append(app)
                    app.module = module.num
                    module.computeUtil()
                    break
            # if not just assign to the best possible module
            if app.module < 0:
                module = modules[0]
                module.apps.append(app)
                app.module = module.num
                module.computeUtil()
        # calculate characteristics
        for m in self.modules:
            m.computeRel()
            m.computeCost()
            m.computeUtil()
            m.computeLag()
        self.modules.sort(key=lambda x: x.num)
        for module in self.modules:
            module.apps.sort(key=lambda x: x.num)
        self.Update(False)

    def RearrangeByUtil(self):
        for module in self.modules:
            module.util = 0
            module.lag = 0
            module.cost = 0
            module.apps = []
        # assign apps by their impact on module utilization
        for app in self.applications:
            app.module = -1
            self.modules.sort(key=lambda x: x.util + app.computeUtil(module.num) - x.limitutil)
            # assign to lowest
            for module in self.modules:
                if module.util + app.computeUtil(module.num) < module.limitutil:
                    module.apps.append(app)
                    app.module = module.num
                    module.computeUtil()
                    break
            # if not just assign to the best possible module
            if app.module < 0:
                module = modules[0]
                module.apps.append(app)
                app.module = module.num
                module.computeUtil()
        # calculate characteristics
        for m in self.modules:
            m.computeRel()
            m.computeCost()
            m.computeUtil()
            m.computeLag()
        self.modules.sort(key=lambda x: x.num)
        for module in self.modules:
            module.apps.sort(key=lambda x: x.num)
        self.Update(False)

    def RearrangeApps(self):
        self.RearrangeByRelL()
        return 0

        for module in self.modules:
            module.util = 0
            module.lag = 0
            module.cost = 0
            module.apps = []
        for app in self.applications:
            app.module = -1
        #assign apps to modules according to inter-application data traffic
        if self.GreedyAssignment():
            #calculate module characteristics
            for m in self.modules:
                m.computeRel()
                m.computeCost()
                m.computeUtil()
                m.computeLag()
            self.modules.sort(key=lambda x: x.num)
            for module in self.modules:
                module.apps.sort(key=lambda x: x.num)
            self.Update(False)
        else:
            #unable to assign by traffic
            self.RearrangeByUtil()

    def GenerateRandom(self, checkConstraints):
        '''
        Generates random solution.
        :param checkConstraints: if generated solution must satisfy constraints.
        '''
        for j in range(Algorithm.algconf.maxGenIter):
            self.modules = []
            self.applications = []
            for i in range(Module.conf.modNum):
                self.modules.append(Module(i))
            for i in range(Module.conf.appNum):
                type = random.choice(Module.conf.applications[i].tools)
                if type == "none":
                    app = NONE(i)
                elif type == "nvp01":
                    app = NVP01(i)
                elif type == "rb01":
                    app = RB01(i)
                self.applications.append(app)
                self.applications.sort(key=lambda x: x.num)
                #check if can use this appversion
            self.RearrangeApps()
            if not checkConstraints or self.CheckConstraints():
                break

    def __str__(self):
        s = "RelL = %0.6f RelR = %0.6f Cost = %d" %(self.relL, self.relR, self.cost)
        for m in self.modules:
            s += os.linesep
            s += "Module: " + str(m.num) + " HW: "
            s += str(m.hw) + " Apps:\n"
            for app in m.apps:
                s += "\t" + "App: " + str(app.num) + " FTM: " + app.__class__.__name__ + " SW: " + str(app.sw) + "\n"
            s += " Reliability: [ " + str(m.relL) + " , " + str(m.relR) + " ]"
        s += os.linesep
        #for i in self.modules:
        #    s+= str(i.time) + ","
        #s = s[:-1]+"]"
        #print "\n"
        #for i in self.modules:
        #    s += str(i)
        return s

    def toSchedule(self):
        '''
        Generates xml-file with schedule for self
        '''
        sch = Schedule()
        for m in self.modules:
            m.toSchedule(sch)
        for l in Module.conf.links:
            src = self.modules[l.src.num]
            dst = self.modules[l.dst.num]
            src_str = ""
            dst_str = ""
            if isinstance(src, NONE) or isinstance(src, HWRC20) or isinstance(src, NVP01):
                src_str = "t" + str(src.num)
            if isinstance(src, NVP11) or isinstance(src, RB01):
                src_str = "t" + str(src.num) + "_snd"
            if isinstance(dst, NONE) or isinstance(src, HWRC20)  or isinstance(dst, NVP01):
                dst_str = "t" + str(dst.num)
            if isinstance(dst, NVP11) or isinstance(dst, RB01):
                dst_str = "t" + str(dst.num) + "_rcv"
            sch.links.append(Link(src_str, dst_str, l.vol))
        filename = "sch" + str(os.getpid()) + ".xml"
        sch.exportXML(filename)

    def getTimesSim(self):
        '''
        Runs simulation experiment for self and finds module times.
        '''
        Algorithm.simcounts += 1
        self.toSchedule()
        sch = "sch" + str(os.getpid()) + ".xml"
        res = "res" + str(os.getpid()) + ".xml"
        #os.system("python Common/Timecounter.py %s %s" % (sch, res))
        if sys.platform.startswith("win"):
            os.system(u"python.exe Common/Timecounter.py %s %s" % (unicode(sch), unicode(res)))
        else:
            os.system("python Common/Timecounter.py %s %s" % (sch, res))
        f = open(res, "r")
        dom = xml.dom.minidom.parse(f)
        for task in dom.getElementsByTagName("task"):
            id = task.getAttribute("id")
            id = id.replace("t","")
            time = int(task.getAttribute("time"))
            if id.find("_snd") > 0:
                num = int(id.replace("_snd",""))
                self.modules[num].time = time
                continue
            if id.find("_") == -1:
                num = int(id)
                self.modules[num].time = time
                continue
        f.close()