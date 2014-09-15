#!/usr/bin/env python
'''
The lbne.geo.builders module
'''

import gegede.builder
from gegede import Quantity as Q
class World(gegede.builder.Builder):
    '''
    Build a simple box world of given material and size.
    '''
    def configure(self, material = 'Air', size = Q("1m"), **kwds):
        self.material, self.size = (material, size)
        pass
    def construct(self, geom):
        dim = (0.5*self.size,)*3
        shape = geom.shapes.Box(self.name + '_box_shape', *dim)
        lv = geom.structure.Volume(self.name+'_volume',
                                   material=self.material, shape=shape)
        self.add_volume(lv)

        # fixme: what about pos/rot?
        # place any daughters
        for sb in self.builders:
            for sub_lv_name in sb.volumes:
                p = geom.structure.Placement("%s_in_%s" % (sub_lv_name,lv.name), volume = sub_lv_name)
                lv.placements.append(p.name)
                
