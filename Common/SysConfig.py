import xml.dom.minidom, random, math

class Component:
    def __init__(self, num, relL=0.0, relR=0.0, cost=0):
        self.num = num
        self.relL = relL
        self.relR = relR
        self.cost = cost

    def generateRandom(self, param):
        self.relL = random.uniform(param["minrel"], param["maxrel"])
        self.relR = random.uniform(relL, param["maxrel"])
        self.cost = random.randint(param["mincost"], param["maxcost"])

class AppConfig:
    def __init__(self):
        self.sw = []
        self.tools = []
        self.num = -1
        self.qrvL = -1.0
        self.qdL = -1.0
        self.qallL = -1.0
        self.qrvR = -1.0
        self.qdR = -1.0
        self.qallR = -1.0
        self.type = ""

    def costInterval(self):
        '''Computes minimum and maximum costs for module.'''
        costs = []
        for i in self.sw:
            costs.append(i.cost)
        costs.sort()
        minCost = min(self.sw, key=lambda x: x.cost).cost
        size = len(costs)
        maxCost = 0
        if "rb01" in self.tools:
            maxCost = max(maxCost, costs[size - 1] + costs[size - 2])
        if "nvp01" in self.tools:
            maxCost = max(maxCost, costs[size - 1] + costs[size - 2] + costs[size - 3])
        if "none" in self.tools:
            maxCost = max(maxCost, costs[size - 1])
        return (minCost, maxCost)

    def LoadFromXmlNode(self, node):
        self.num = int(node.getAttribute("num"))
        self.qrvL = float(node.getAttribute("qrvL"))
        self.qdL = float(node.getAttribute("qdL"))
        self.qallL = float(node.getAttribute("qallL"))
        self.qrvR = float(node.getAttribute("qrvR"))
        self.qdR = float(node.getAttribute("qdR"))
        self.qallR = float(node.getAttribute("qallR"))
        self.sw = []
        for child in node.childNodes:
            if child.nodeName == "sw":
                num = int(child.getAttribute("num"))
                relL = float(child.getAttribute("relL"))
                relR = float(child.getAttribute("relR"))
                cost = int(child.getAttribute("cost"))
                self.sw.append(Component(num, relL, relR, cost))
            elif child.nodeName == "tool":
                name = child.getAttribute("name")
                self.tools.append(name)
        '''[!!!] Sort lists in order not to search elements by field 'num',
        but to refer them by index.'''
        self.sw.sort(key=lambda x: x.num)

    def generateRandom(self, param):
        self.sw = []
        self.hw = []
        self.qrvL = param["qrvL"]
        self.qdL = param["qdL"]
        self.qallL = param["qallL"]
        self.qrvR = param["qrvR"]
        self.qdR = param["qdR"]
        self.qallR = param["qallR"]
        self.tools = []
        if param["none"]:
            self.tools.append("none")
        if param["nvp01"]:
            self.tools.append("nvp01")
        if param["rb01"]:
            self.tools.append("rb01")
        for i in range(param["swnum"]):
            sw = Component(i)
            sw.generateRandom(param)
            self.sw.append(sw)

class ModConfig:
    def __init__(self):
        self.hw = []
        self.num = -1
        self.hwrc_zone_num = -1

    def GetConfigsNum(self):
        res = 0
        hw_num = len(self.hw)
        sw_num = 1
        if len(self.sw) > 0:
            sw_num = len(self.sw)
        if "none" in self.tools:
            res += hw_num * sw_num
        if "nvp01" in self.tools:
            res += hw_num * math.factorial(sw_num) /(6 * math.factorial(sw_num - 3))
        if "rb01" in self.tools:
            res += hw_num * math.factorial(sw_num) /(2 * math.factorial(sw_num - 2))
        return res

    def costInterval(self):
        '''Computes minimum and maximum costs for module.'''
        minhw = min(self.hw, key=lambda x: x.cost).cost
        maxhw = max(self.hw, key=lambda x: x.cost).cost
        return (minhw, maxhw)

    def LoadFromXmlNode(self, node):
        '''Loading from node with tag 'module'.'''
        self.num = int(node.getAttribute("num"))
        self.hwrc_zone_num = float(node.getAttribute("hwrczonenum"))
        if (node.hasAttribute("limittime")):
            self.limittime=int(node.getAttribute("limittime"))
        self.hw = []
        self.tools = []
        for child in node.childNodes:
            if isinstance(child, xml.dom.minidom.Text):
                continue
            if child.nodeName == "hw":
                num = int(child.getAttribute("num"))
                relL = float(child.getAttribute("relL"))
                relR = float(child.getAttribute("relR"))
                cost = int(child.getAttribute("cost"))
                self.hw.append(Component(num, relL, relR, cost))
        '''[!!!] Sort lists in order not to search elements by field 'num',
        but to refer them by index.'''
        self.hw.sort(key=lambda x: x.num)
            
    def generateRandom(self, param):
        if param["hwrczonenum"]:
            self.hwrc_zone_num = param["hwrczonenum"]
        self.hw = []
        for i in range(param["hwnum"]):
            hw = Component(i)
            hw.generateRandom(param)
            self.hw.append(hw)

class SysConfig:
    def __init__(self):
        self.modNum = 0 #use it instead of len(self.modules)
        self.appNum = 0
        self.modules = []
        self.applications = []
        self.limitcost = []
        self.limitlag = []
        self.hwrc_cost = -1
        self.hwrc_relL = -1.0
        self.hwrc_relR = -1.0
        self.messaging = {}
        self.lag = {}
        self.util = {}

    def costInterval(self):
        '''Computes minimum and maximum system costs (is needed for generator)'''
        min = self.hwrc_cost
        max = self.hwrc_cost
        for m in self.modules:
            range = m.costInterval()
            min += range[0]
            max += range[1]
        for app in self.applications:
            range = app.costInterval()
            min += range[0]
            max += range[1]
        return (min, max)

    def loadXML(self, fileName):
        self.modules = []
        f = open(fileName, "r")
        dom = xml.dom.minidom.parse(f)
        for root in dom.childNodes:
            if root.tagName == "system":
                if root.hasAttribute("limitcost"):
                    self.limitcost = int(root.getAttribute("limitcost"))
                if root.hasAttribute("limitcost"):
                    self.limitlag = float(root.getAttribute("limitlag"))
                if root.hasAttribute("costhwrc"):
                    self.hwrc_cost = int(root.getAttribute("costhwrc"))
                if root.hasAttribute("qhwrcL"):
                    self.hwrc_relL = float(root.getAttribute("qhwrcL"))
                if root.hasAttribute("qhwrcR"):
                    self.hwrc_relR = float(root.getAttribute("qhwrcR"))
                for node in root.childNodes:
                    if isinstance(node, xml.dom.minidom.Text):
                        continue
                    if node.tagName == "module":
                        m = ModConfig()
                        m.LoadFromXmlNode(node)
                        self.modules.append(m)
                    elif node.tagName == "application":
                        app = AppConfig()
                        app.LoadFromXmlNode(node)
                        self.applications.append(app)
                    elif node.tagName == "msg":
                        self.messaging[( int(node.getAttribute("pnum")), int(node.getAttribute("qnum")) )] = int(node.getAttribute("size"))
                    elif node.tagName == "perf":
                        self.lag[( int(node.getAttribute("appnum")), int(node.getAttribute("modnum")) )] = float(node.getAttribute("lag"))
                        self.util[( int(node.getAttribute("appnum")), int(node.getAttribute("modnum")) )] = float(node.getAttribute("util"))
                #[!!!]Sort list in order not to search elements by num, but refer them by index
                self.modules.sort(key=lambda x: x.num)
                self.applications.sort(key=lambda x: x.num)
                self.modNum = len(self.modules)
                self.appNum = len(self.applications)
        
    def generateRandom(self, param):
        self.modules = []
        self.applications = []
        self.links = []
        self.modNum = param["modnum"]
        self.appNum = param["appnum"]
        for i in range(param["modnum"]):
            m = ModConfig()
            m.generateRandom(param)
            m.num = i
            self.modules.append(m)
        for j in range(param["appnum"]):
            app = AppConfig()
            app.generateRandom(param)
            app.num = j
            self.applications.append(app)
        self.modNum = len(self.modules)
        self.appNum = len(self.applications)

    def saveXML(self, filename):
        dom = xml.dom.minidom.Document()
        system = dom.createElement("system")
        system.setAttribute("limitcost", str(self.limitcost))
        if self.hwrc_cost >= 0.0:
            system.setAttribute("costhwrc", str(self.hwrc_cost))
        if self.hwrc_relL >= 0.0:
            system.setAttribute("qhwrcL", str(self.hwrc_relL))
        if self.hwrc_relR >= 0.0:
            system.setAttribute("qhwrcR", str(self.hwrc_relR))
        for mod in self.modules:
            m = dom.createElement("module")
            m.setAttribute("num", str(mod.num))
            m.setAttribute("qrvL", str(mod.qrvL))
            m.setAttribute("qdL", str(mod.qdL))
            m.setAttribute("qallL", str(mod.qallL))
            m.setAttribute("qrvR", str(mod.qrvR))
            m.setAttribute("qdR", str(mod.qdR))
            m.setAttribute("qallR", str(mod.qallR))
            if mod.hwrc_zone_num >= 0:
                m.setAttribute("hwrczonenum", str(mod.hwrc_zone_num))
            if mod.limittime != None:
                m.setAttribute("limittime", str(mod.limittime))
            for tool in mod.tools:
                t = dom.createElement("tool")
                t.setAttribute("name", tool)
                m.appendChild(t)
            for sw in mod.sw:
                s = dom.createElement("sw")
                s.setAttribute("num", str(sw.num))
                s.setAttribute("cost", str(sw.cost))
                s.setAttribute("relL", str(sw.relL))
                s.setAttribute("relR", str(sw.relR))
                m.appendChild(s)
            for hw in mod.hw:
                h = dom.createElement("hw")
                h.setAttribute("num", str(hw.num))
                h.setAttribute("cost", str(hw.cost))
                h.setAttribute("relL", str(hw.relL))
                h.setAttribute("relR", str(hw.relR))
                m.appendChild(h)
            system.appendChild(m)
            system.appendChild(l)
        dom.appendChild(system)
        f = open(filename, "w")
        f.write(dom.toprettyxml())
        f.close()

