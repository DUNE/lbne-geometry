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
                


class BoxWithOne(gegede.builder.Builder):
    '''
    Build a simple box that holds one child taken from a particular builder.
    '''
    defaults = dict(
        material = 'Air',
        dim = (Q('1m'),Q('1m'),Q('1m')),
        off = (Q('1m'),Q('1m'),Q('1m')),
        sbind = 0,
        volind = 0,
    )

    def construct(self, geom):
        dim = [0.5*d for d in self.dim]
        shape = geom.shapes.Box(self.name, *dim)
        pos = geom.structure.Position(None, *self.off)
        child = self.builders[self.sbind].volumes[self.volind]
        place = geom.structure.Placement(None, volume = child, pos = pos)
        vol = geom.structure.Volume('vol'+self.name, material = self.material, shape=shape,
                                    placements = [place])
        self.add_volume(vol)
        return
