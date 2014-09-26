#!/usr/bin/env python
'''
Some builders of simplified 35t geometry
'''
import gegede.builder
from gegede import Quantity as Q

class Cryostat(gegede.builder.Builder):
    '''Build a simple (incorrect) cryostat.

    This assumes a symmetric, concentric rectangular onion which is
    not reality, eg the roof is not flat and it has not concrete.

    '''
    defaults = dict(

        # x direction
        container_width = Q('4104 mm'),
        # y direction
        container_length = Q('5404 mm'),
        # z direction
        container_height = Q('4104 mm'), # adds extra 300 mm to accommodate nonexistent concrete roof

        concrete_thickness = Q('300 mm'),
        concrete_material = 'Concrete',

        foam_thickness = Q('400 mm'),
        foam_material = 'Foam',

        membrane_thickness = Q('2 mm'),
        membrane_material = 'Stainless',
        bulk_material = 'LiquidArgon')

    def construct(self, geom):
        gs = geom.structure         # shorthand

        # dx,dy,dx
        dim = [0.5* x for x in (self.container_width, self.container_length, self.container_height)]

        lvs = list()

        # implement onion pattern
        for name, thick, mat in \
            [("shell",      self.concrete_thickness, self.concrete_material),
             ("insulation", self.foam_thickness,     self.foam_material),
             ("membrane",   self.membrane_thickness, self.membrane_material),
             ("bulk",       None,                    self.bulk_material)]:

            shape = geom.shapes.Box(name+'_shape', *dim)
            print '35:',shape

            lv = gs.Volume(name+'_volume', material = mat, shape=shape)

            if lvs:             # place
                last_lv = lvs[-1]
                p = gs.Placement("%s_in_%s" % (lv.name,last_lv.name), volume = lv)
                last_lv.placements.append(p.name)
                #print '35:',lv.name,last_lv.name
                #if lv.placements:
                #    print '\tthis: %s' % str(lv.placements)
                #if last_lv.placements:
                #    print '\tlast: %s' % str(last_lv.placements)

            lvs.append(lv)

            if thick:           # for the next layer of the onion
                dim = [d-thick for d in dim] 

            continue

        mb_vol = lvs[-1]
        det_vol_name = self.get_builder(0).get_volume(0).name
        # fixme: place in center for now
        mb_vol.placements.append(gs.Placement(None, volume=det_vol_name).name)

        print 'THIRTYFIVE: constructed %d' % len(lvs)
        print '\twith %s in: %s' % (det_vol_name, mb_vol)

        self.add_volume(lvs[0])
        return

class Detector(gegede.builder.Builder):
    '''Build the actual detector.

    This assumes a sandwich in the Y-direction with ordered builders,
    each producing 1 volume.  Each builder should provide a "length"
    attribute to give the expected length in Y.

    '''


    def construct(self, geom):
        gs = geom.structure     # shorthand 

        total_length = sum([b.length for b in self.builders])
        arrow = -0.5 * total_length
        placements = list()

        for b in self.builders:
            vol = b.get_volume(0)
            place = gs.Placement(None, volume = vol,
                                 pos = gs.Position(None, y = arrow + 0.5 * b.length))
            arrow += b.length
            placements.append(place)

        ass = gs.Volume(self.name+'_volume', material=None, shape = None,
                        placements=placements)
        self.add_volume(ass)
        return

class FieldCage(gegede.builder.Builder):
    '''Build a simple, rectangular field cage for 35t

    This produces a subtraction made of the given material.
    '''

    defaults = dict(
        # x direction
        width = Q('1.8 m'),     # rough dimension from params ss render
        # y direction
        length = Q('2.29 m'),   # scaled from params ss render (long)
        #short_length = Q('0.26 m'), # scaled from params ss render
        #gap_length = Q('0.15 m'),   # subtracted from 2.7 marked on params ss render
        # z direction
        height = Q('2.08 m'),   # scaled from param ss render
        thickness = Q('0.006 inch'),
        material = 'FieldCage',
        )

    def construct(self, geom):

        outer = geom.shapes.Box(self.name + '_outer_shape', 
                                dx=0.5*self.width, 
                                dy=0.5*self.length, 
                                dz=0.5*self.height)

        inner = geom.shapes.Box(self.name + '_inner_shape', 
                                dx=outer.dx-self.thickness,
                                dy=outer.dy+self.thickness, # yes, "+". extend subtraction past edges
                                dz=outer.dz-self.thickness)

        shape = geom.shapes.Boolean(self.name+'_shape', type='subtraction',
                                    first=outer, second=inner)

        vol = geom.structure.Volume(self.name+'_volume', material=self.material, shape = shape)

        self.add_volume(vol)
        return

class ApaPlane(gegede.builder.Builder):
    
    defaults = dict(
        # x direction
        width = Q('1.8 m'),     # rough dimension from params ss render
        # y direction
        length = Q('0.15 m'),   # scaled from params ss render (long)
        # z direction
        height = Q('2.08 m'),   # scaled from param ss render
        material = 'ApaMaterial',
        )

    def construct(self, geom):
        shape = geom.shapes.Box(self.name + '_shape', 
                                dx=0.5*self.width, 
                                dy=0.5*self.length, 
                                dz=0.5*self.height)
        vol = geom.structure.Volume(self.name+'_volume', material=self.material, shape = shape)
        self.add_volume(vol)
        return
