#!/usr/bin/env python

import json
from collections import namedtuple

ISP = namedtuple('ISP', 'vacuum jet atmosphere')

with open('parts.json') as f:
    parts = json.load(f)

class Engine(object):

    def __init__(self):
        self.thrust = 0
        self.isp = None
        self.name = ''

    def __repr__(self):
        return ('Engine("%s", thrust=%s, vacuumISP=%s, atmosphereISP=%s)' % (
            self.name, self.thrust, self.isp.vacuum, self.isp.atmosphere))

    def __str__(self):
        return self.__repr__()

engines = []
for path, d in parts.items():
    part = d['PART']
    if 'MODULE' in part:
        modules = part['MODULE']
        if not isinstance(modules, list):
            modules = [modules]
        for module in modules:
            if module['name'] == 'ModuleEngines':
                eng = Engine()
                eng.thrust = module['maxThrust']
                eng.name = part['title']
                atmo_curve = module['atmosphereCurve']['key']
                if not isinstance(atmo_curve[0], list):
                    atmo_curve = (atmo_curve,)
                atmo_curve = dict(atmo_curve)
                eng.isp = ISP(atmo_curve.get(0), atmo_curve.get(0.3),
                    atmo_curve.get(1))
                engines += [eng]

for eng in engines:
    print eng
