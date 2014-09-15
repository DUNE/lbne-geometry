''' 
35ton builders
'''

import gegede.builder

from gegede import Quantity as Q
class SimpleCryostat(gegede.builder.Builder):
    '''
    A simple rectangular cryostat
    '''
    defaults = dict(container_height = Q('2700 mm'),
                    container_width = Q('2700 mm'),
                    container_length = Q('4000 mm'),
                    concrete_thickness = Q('300 mm'),
                    concrete_material = 'Concrete',
                    foam_thickness = Q('400 mm'),
                    foam_material = 'Foam',
                    membrane_thickness = Q('2 mm'),
                    membrane_material = 'Stainless',
                    bulk_material = 'LiquidArgon')

    def configure(self, **kwds):
        if not set(kwds).issubset(self.defaults): # no unknown keywords
            msg = 'Unknown parameter in: "%s"' % (', '.join(sorted(kwds.keys())), )
            raise ValueError,msg
        self.__dict__.update(**self.defaults)    # stash them as data members
        self.__dict__.update(**kwds)             # and update any from user

    def construct(self, geom):
        # x,y,x
        dim = [0.5* x for x in (self.container_width, self.container_length, self.container_height)]

        lvs = list()

        # implement onion pattern
        for name, thick, mat in \
            [("shell",      self.concrete_thickness, self.concrete_material),
             ("insulation", self.foam_thickness,     self.foam_material),
             ("membrane",   self.membrane_thickness, self.membrane_material),
             ("bulk",       None,                    self.bulk_material)]:
            pre='%s_%s_' % (self.name, name)
            shape = geom.shapes.Box(pre+'shape', *dim)
            lv = geom.structure.Volume(pre+'volume', material = mat, shape=shape)

            if lvs:             # place
                last_lv = lvs[-1]
                p = geom.structure.Placement("%s_in_%s" % (lv.name,last_lv.name), volume = lv)
                last_lv.placements.append(p.name)
                print '35:',lv.name,last_lv.name
                if lv.placements:
                    print '\tthis: %s' % str(lv.placements)
                if last_lv.placements:
                    print '\tlast: %s' % str(last_lv.placements)

            lvs.append(lv)

            if thick:           # for the next layer of the onion
                dim = [d-thick for d in dim] 

            continue

        print 'THIRTYFIVE: constructed %d' % len(lvs)

        self.add_volume(lv[0])
        return
