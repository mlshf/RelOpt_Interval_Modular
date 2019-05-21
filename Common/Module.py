import random
import math
from Common.Schedule import Task, Link

class Application:
    '''class for software'''
    conf = None
    def __init__(self, num, sw):
        self.cost = -1
        self.relL = -1.0
        self.relR = -1.0
        self.num = num
        self.sw = sw
        self.module = -1
        self.conf.applications[self.num].type = self.__class__.__name__

    def __eq__(self, other):
        '''Operator ==
        '''
        return self.num ==  other.num and self.sw == other.sw

class NONE(Application):
    '''Class for module with NONE mechanism.
    :param num: number of module
    :param hw: List of used HW versions. DO NOT USE -1 FOR ABSENT VERSIONS! MUST CONTAIN 0 OR 1 ELEMENT.
    :param sw: List of used SW versions. DO NOT USE -1 FOR ABSENT VERSIONS! MUST CONTAIN 0 OR 1 ELEMENT.

    If len(hw) == 0  and len(sw) == 0 module is generated randomly.
    '''
    def __init__(self, num, sw = None):
        if sw is None:
            sw = [random.randint(0, len(self.conf.applications[num].sw)-1)]
        Application.__init__(self, num, sw)

    def computeRel(self, QhwL, QhwR):
        QL = QhwL * self.conf.applications[self.num].sw[self.sw[0]].relL
        QR = QhwR * self.conf.applications[self.num].sw[self.sw[0]].relR
        self.relL = QL
        self.relR = QR

    def computeCost(self):
        self.cost = self.conf.applications[self.num].sw[self.sw[0]].cost
        return self.cost

    def computeUtil(self, modnum):
        return self.conf.util[( self.num, modnum )]

    def computeLag(self, modnum):
        return self.conf.lag[( self.num, modnum )]

    def __str__(self):
        '''Converts app to string. So we can 'print app'
        '''
        return "\t"+str(self.num) + ". None:" + str(self.sw) + "\n"

class NVP01(Application):
    def __init__(self, num, sw=None):
        if sw is None:
            sw1 = random.randint(0, len(self.conf.applications[num].sw)-3)
            sw2 = random.randint(sw1+1, len(self.conf.applications[num].sw)-2)
            sw = [sw1, sw2, random.randint(sw2+1, len(self.conf.applications[num].sw)-1)]
        Application.__init__(self, num, sw)

    def computeRel(self, QhwL, QhwR):
        PhwL = 1 - QhwR
        PhwR = 1 - QhwL
        Qsw0L = self.conf.applications[self.num].sw[self.sw[0]].relL
        Qsw0R = self.conf.applications[self.num].sw[self.sw[0]].relR
        Psw0L = 1 - Qsw0R
        Psw0R = 1 - Qsw0L
        Qsw1L = self.conf.applications[self.num].sw[self.sw[1]].relL
        Qsw1R = self.conf.applications[self.num].sw[self.sw[1]].relR
        Psw1L = 1 - Qsw1R
        Psw1R = 1 - Qsw1L
        Qsw2L = self.conf.applications[self.num].sw[self.sw[2]].relL
        Qsw2R = self.conf.applications[self.num].sw[self.sw[2]].relR
        Psw2L = 1 - Qsw2R
        Psw2R = 1 - Qsw2L
        QrvL = self.conf.applications[self.num].qrvL
        QrvR = self.conf.applications[self.num].qrvR
        PrvL = 1 - QrvR
        PrvR = 1 - QrvL
        QdL = self.conf.applications[self.num].qdL
        QdR = self.conf.applications[self.num].qdR
        PdL = 1 - QdR
        PdR = 1 - QdL
        QallL = self.conf.applications[self.num].qallL
        QallR = self.conf.applications[self.num].qallR
        PallL = 1 - QallR
        PallR = 1 - QallL

        PL = (PrvL +
              QrvL * PrvL +
              QrvL * QrvL * PrvL +
              QrvL * QrvL * QrvL * PdL +
              QrvL * QrvL * QrvL * QdL * PallL +
              QrvL * QrvL * QrvL * QdL * QallL * PhwL +
              QrvL * QrvL * QrvL * QdL * QallL * QhwL * Qsw2L * Psw0L * Psw1L +
              QrvL * QrvL * QrvL * QdL * QallL * QhwL * Qsw0L * Psw1L * Psw2L +
              QrvL * QrvL * QrvL * QdL * QallL * QhwL * Qsw1L * Psw0L * Psw2L)

        PR = (PrvR +
              QrvR * PrvR +
              QrvR * QrvR * PrvR +
              QrvR * QrvR * QrvR * PdR +
              QrvR * QrvR * QrvR * QdR * PallR +
              QrvR * QrvR * QrvR * QdR * QallR * PhwR +
              QrvR * QrvR * QrvR * QdR * QallR * QhwR * Qsw2R * Psw0R * Psw1R +
              QrvR * QrvR * QrvR * QdR * QallR * QhwR * Qsw0R * Psw1R * Psw2R +
              QrvR * QrvR * QrvR * QdR * QallR * QhwR * Qsw1R * Psw0R * Psw2R)

        QL = 1 - PR
        QR = 1 - PL

        q0l = QhwL * Qsw0L
        q0R = QhwR * Qsw0R
        q1l = QhwL * Qsw1L
        q1R = QhwR * Qsw1R
        q2l = QhwL * Qsw2L
        q2R = QhwR * Qsw2R

        self.relL = QL
        self.relR = QR

    def computeCost(self):
        self.cost = (self.conf.applications[self.num].sw[self.sw[0]].cost +
                     self.conf.applications[self.num].sw[self.sw[1]].cost +
                     self.conf.applications[self.num].sw[self.sw[2]].cost)
        return self.cost

    def computeUtil(self, modnum):
        return self.conf.util[( self.num, modnum )]

    def computeLag(self, modnum):
        return self.conf.lag[( self.num, modnum )]

    def __str__(self):
        '''Converts app to string. So we can 'print app'
        '''
        return "\t"+str(self.num) + ". NVP01:" + str(self.sw) + "\n"

class RB01(Application):
    def __init__(self, num, sw = None):
        if sw is None:
            sw1 = random.randint(0, len(self.conf.applications[num].sw)-2)
            sw = [sw1, random.randint(sw1+1, len(self.conf.applications[num].sw)-1)]
        Application.__init__(self, num, sw)

    def computeRel(self, QhwL, QhwR):
        PhwL = 1 - QhwR
        PhwR = 1 - QhwL
        Qsw0L = self.conf.applications[self.num].sw[self.sw[0]].relL
        Qsw0R = self.conf.applications[self.num].sw[self.sw[0]].relR
        Psw0L = 1 - Qsw0R
        Psw0R = 1 - Qsw0L
        Qsw1L = self.conf.applications[self.num].sw[self.sw[1]].relL
        Qsw1R = self.conf.applications[self.num].sw[self.sw[1]].relR
        Psw1L = 1 - Qsw1R
        Psw1R = 1 - Qsw1L
        QrvL = self.conf.applications[self.num].qrvL
        QrvR = self.conf.applications[self.num].qrvR
        PrvL = 1 - QrvR
        PrvR = 1 - QrvL
        QdL = self.conf.applications[self.num].qdL
        QdR = self.conf.applications[self.num].qdR
        PdL = 1 - QdR
        PdR = 1 - QdL
        QallL = self.conf.applications[self.num].qallL
        QallR = self.conf.applications[self.num].qallR
        PallL = 1 - QallR
        PallR = 1 - QallL

        PL = (PrvL +
              QrvL * PdL +
              QrvL * QdL * PallL +
              QrvL * QdL * QallL * PhwL +
              QrvL * QdL * QallL * QhwL * Psw0L * Psw1L)

        PR = (PrvR +
              QrvR * PdR +
              QrvR * QdR * PallR +
              QrvR * QdR * QallR * PhwR +
              QrvR * QdR * QallR * QhwR * Psw0R * Psw1R)

        QL = 1 - PR
        QR = 1 - PL

        q0l = QhwL * Qsw0L
        q0R = QhwR * Qsw0R
        q1l = QhwL * Qsw1L
        q1R = QhwR * Qsw1R
        
        self.relL = QL
        self.relR = QR

    def computeCost(self):
        self.cost = (self.conf.applications[self.num].sw[self.sw[0]].cost +
                     self.conf.applications[self.num].sw[self.sw[1]].cost)
        return self.cost

    def computeUtil(self, modnum):
        return self.conf.util[( self.num, modnum )] * 2

    def computeLag(self, modnum):
        return self.conf.lag[( self.num, modnum )] * 2

    def __str__(self):
        '''Converts app to string. So we can 'print app'
        '''
        return "\t"+str(self.num) + ". RB01:" + str(self.sw) + "\n"

class Module:
    '''Base class for system module.
    :param num: Number of module.
    :param hw: List of used HW versions. DO NOT USE -1 FOR ABSENT VERSIONS!
    :param sw: List of used SW versions. DO NOT USE -1 FOR ABSENT VERSIONS!
    '''
    conf = None
    def __init__(self, num, hw = None, apps = None):
        if hw is None:
            hw = [random.randint(0, len(self.conf.modules[num].hw)-1)]
        self.util = 0
        self.num = num
        self.hw = hw
        if apps is None:
            apps = []
        self.apps = apps
        self.cost = -1
        self.relL = -1.0
        self.relR = -1.0
        self.util = 0.0
        self.lag = 0.0
        self.limitutil = 1

    def __eq__(self, other):
        '''Operator ==
        '''
        return self.num ==  other.num and self.hw == other.hw and self.apps == other.apps

    def computeHWRel(self):
        QhwrcL = self.conf.hwrc_relL
        QhwrcR = self.conf.hwrc_relR
        PhwrcL = 1 - QhwrcR
        PhwrcR = 1 - QhwrcL
        QhwL = self.conf.modules[self.num].hw[self.hw[0]].relL
        QhwR = self.conf.modules[self.num].hw[self.hw[0]].relR
        PhwL = 1 - QhwR
        PhwR = 1 - QhwL

        # modules that partake in reconfiguration after initial fault (self fault)
        zone_0 = []
        for i in self.conf.modules:
            if ((i != self.conf.modules[self.num]) and
                    (i.hwrc_zone_num == self.conf.modules[self.num].hwrc_zone_num)):
                zone_0.append(i)
        # probability of failure after initial reconfiguration
        P_post_reconf_1L = 0.0
        P_post_reconf_1R = 0.0
        if len(zone_0) > 0:
            for j in zone_0:
                # modules that partake in reconfiguration after second fault (j fault)
                zone_1 = []
                for i in zone_0:
                    if ((i != j) and
                            (i != self.conf.modules[self.num]) and
                            (i.hwrc_zone_num == j.hwrc_zone_num)):
                        zone_1.append(i)
                # probability of failure after second reconfiguration
                P_post_reconf_2L = 0.0
                P_post_reconf_2R = 0.0
                if len(zone_1) > 0:
                    for k in zone_1:
                        P_post_reconf_2L += 1 - k.hw[self.hw[0]].relR
                        P_post_reconf_2R += 1 - k.hw[self.hw[0]].relL
                    P_post_reconf_2L /= len(zone_1)
                    P_post_reconf_2R /= len(zone_1)
                else:
                    P_post_reconf_2L = 1.0
                    P_post_reconf_2R = 1.0
                P_post_reconf_1L += (1 - j.hw[self.hw[0]].relR) * (PhwrcL + QhwrcL * P_post_reconf_2L)
                P_post_reconf_1R += (1 - j.hw[self.hw[0]].relL) * (PhwrcR + QhwrcR * P_post_reconf_2R)
            P_post_reconf_1L /= len(zone_0)
            P_post_reconf_1R /= len(zone_0)
        else:
            P_post_reconf_1L = 1.0
            P_post_reconf_1R = 1.0
        PL = PhwL * (PhwrcL + QhwrcL * P_post_reconf_1L)
        PR = PhwR * (PhwrcR + QhwrcR * P_post_reconf_1R)
        QL = 1 - PR
        QR = 1 - PL
        self.relL = QL
        self.relR = QR

    def computeRel(self):
        Module.computeHWRel(self)
        if len(self.apps) > 0:
            relL = 1
            relR = 1
            for app in self.apps:
                app.computeRel(self.relL, self.relR)
                relL *= app.relL
                relR *= app.relR
            self.relL = relL
            self.relR = relR

    def computeCost(self):
        self.cost = self.conf.modules[self.num].hw[self.hw[0]].cost
        if len(self.apps) > 0:
            for app in self.apps:
                self.cost += app.computeCost()
        return self.cost

    def computeUtil(self):
        self.util = 0.0
        if len(self.apps) > 0:
            for app in self.apps:
                self.util += app.computeUtil(self.num)
        return self.util

    def computeLag(self):
        self.lag = 0.0
        if len(self.apps) > 0:
            for app in self.apps:
                self.lag += app.computeLag(self.num)
        return self.lag


    def __str__(self):
        '''Converts module to string. So we can 'print module'
        '''
        string = "\t" + str(self.num) + ". Apps:\n"
        for app in self.apps:
            string += "\t" + app.__str__()
        return string