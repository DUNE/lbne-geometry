import gegede.builder
from gegede import Quantity as Q



class Detector(gegede.builder.Builder):
    '''Assemble the 35t detector

    It is a sandwich in X of "small drift", "wire frame" and "large
    drift" volumes with CPA volumes capping both ends.  Builders are
    assumed to be in order from -x to +x:

      CPA, short drift, wire frame, long drift, [CPA]

    If last CPA builder is not given, the volume from the first will
    be reused.

    '''

    defaults = dict(
        material = 'LiquidArgon'
        )

    def construct(self, geom):

        volumes = [sb.get_volume(0) for sb in self.get_builders()]
        if len(volumes) == 4:
            volumes.append(volumes[0])
        shapes = [geom.get_shape(v) for v in volumes]

        # Get envelop just fitting the sandwich
        dx_extent = sum([s.dx for s in shapes])
        dy_extent = max([s.dy for s in shapes])
        dz_extent = max([s.dz for s in shapes])

        x_cursor = -1 * dx_extent
        placements = list()
        for shape,volume in zip(shapes,volumes):
            x_cursor += shape.dx
            pos = geom.structure.Position(None, x=x_cursor)
            x_cursor += shape.dx            
            place = geom.structure.Placement(None, volume=volume, pos=pos)
            placements.append(place)
            
        shape = geom.shapes.Box(self.name, dx = dx_extent, dy = dy_extent, dz = dz_extent)
        top = geom.structure.Volume('vol'+self.name, material=self.material, shape=shape, 
                                    placements = placements)
        self.add_volume(top)
            

class Cage(gegede.builder.Builder):
    '''
    Build a field cage.
    '''
    defaults = dict(
        thickness = Q('0.006 inch'), # from doc9176
        length = Q('254 mm'), # from Bo/Rohul's drift direction dimensions
        height = Q('2002.1 mm'), # doc 7550 / Rahul's model
        width = Q('1588.5 mm'), # doc 7550 / Rahul's model
        material = 'FieldCage',
        )

    def construct(self, geom):
        inner = geom.shapes.Box(None, 
                                0.5*self.length+self.thickness, # add a bit to punch out the hole
                                0.5*self.height-self.thickness, 
                                0.5*self.width-self.thickness)
        outer = geom.shapes.Box(None, 0.5*self.length, 0.5*self.height, 0.5*self.width)
        shape = geom.shapes.Boolean(None, 'subtraction', first=outer, second=inner)
        vol = geom.structure.Volume('vol'+self.name, material = self.material, shape=shape)
        self.add_volume(vol)

class CPA(gegede.builder.Builder):
    '''
    Build a CPA.
    '''
    defaults = dict(
        # defaults from PSL drawing 0ECPA0001.pdf and 0ECPA0002.pdf
        thickness = Q('2.94 inch'), 
        height = Q('83.93 inch'), # includes piping
        width = Q('67.64 inch'),  # includes piping
        material = 'Stainless',
        )

    def construct(self, geom):
        shape = geom.shapes.Box(None, 0.5*self.thickness, 0.5*self.height, 0.5*self.width)
        vol = geom.structure.Volume('vol'+self.name, material = self.material, shape=shape)
        self.add_volume(vol)

class WireFrame(gegede.builder.Builder):
    '''Assemble the individual wire frames into one big frame.

    Three sub-builders are expected in order: small, medium and large.

    Nominal locations place the two large frames and the S&M frame (+gap) centered on Y=0.
    '''

    defaults = dict(
        y_gap = Q('1 inch'),    # between S & M
        z_gap = Q('1 inch'),    # between S/M and L
        y_offset_ll = Q('0 mm'), # offset in Y for both large frames
        y_offset_sm = Q('0 mm'), # offset in Y for both S & M frames

        material = 'LiquidArgon',
    )
        
    def construct(self, geom):
        children = list()

        maxyext = Q('0 m')

        s_volume = self.get_builder(0).get_volume(0)
        s_shape = geom.get_shape(s_volume)
        m_volume = self.get_builder(1).get_volume(0)
        m_shape = geom.get_shape(m_volume)
        l_volume = self.get_builder(2).get_volume(0)
        l_shape = geom.get_shape(l_volume)

        # small
        small_center = -0.5*self.y_gap - m_shape.dy + self.y_offset_sm
        pos = geom.structure.Position(None, y = small_center)
        place = geom.structure.Placement(None, volume=s_volume, pos=pos)
        children.append(place)
        maxyext = max(maxyext, abs(small_center - s_shape.dy))

        # medium
        medium_center = 0.5*self.y_gap + s_shape.dy  + self.y_offset_sm
        pos = geom.structure.Position(None, y=medium_center)
        place = geom.structure.Placement(None, volume=m_volume, pos=pos)
        children.append(place)
        maxyext = max(maxyext, medium_center + m_shape.dy)

        # large
        large_center = Q('0 m') + self.y_offset_ll
        large_offset = s_shape.dz + l_shape.dz + self.z_gap
        posm = geom.structure.Position(None, z = -1*large_offset, y=large_center)
        posp = geom.structure.Position(None, z = +1*large_offset, y=large_center)
        children += [
            geom.structure.Placement(None, volume=l_volume, pos=posm),
            geom.structure.Placement(None, volume=l_volume, pos=posp)
        ]
        maxyext = max(maxyext, large_center + l_shape.dy)

        # envelope
        # fixme: maybe want to add 0.5*self.z_gap to dz
        env_shape = geom.shapes.Box(None, dx=l_shape.dx, dy = maxyext, dz = large_offset + l_shape.dz)
        env_vol = geom.structure.Volume('vol' + self.name, material = self.material,
                                        shape=env_shape, placements = children)
        self.add_volume(env_vol)

# PSL 8752C300
# PSL 8752C305
# PSL 8752C310
class WireFrameOne(gegede.builder.Builder):
    defaults = dict(
        bar_width = Q('4 inch'),
        bar_thickness = Q('3.05mm'), # same for crosses
        ncrosses = 2,
        cross_gap = Q('560.20 mm'),
        cross_width = Q('3 inch'),

        thickness = Q('2 inch'),                 # all
        height = Q('2036.2 mm'),                 # large
        width = Q('300.8 mm') + 2.0*Q('4 inch'), # all

        bar_material = 'Stainless',
        material = 'LiquidArgon',
    )

    def make_bar_tube(self, volname, geom, x_size, y_size, length):
        '''
        Make a bar of <length> along z-axis and x/y_size (X, Y)-axes with walls of <thick>.
        '''
        thick = self.bar_thickness
        bar_outer = geom.shapes.Box(None, 0.5*x_size,       0.5*y_size,       0.5*length)
        bar_inner = geom.shapes.Box(None, 0.5*x_size-thick, 0.5*y_size-thick, 0.5*length)
        bar_shape = geom.shapes.Boolean(None, 'subtraction', 
                                        first=bar_outer, second=bar_inner)
        return geom.structure.Volume(volname, material = self.bar_material, shape=bar_shape)

    def make_sides(self, volname, geom, length, width, rot = None):
        '''
        Make and place two sides of a frame of given <length> placed to make a given <width>
        '''
        bar = self.make_bar_tube(volname, geom, self.thickness, self.bar_width, length)
        off = 0.5*(width - self.bar_width)
        if rot: 
            rot = geom.structure.Rotation(None, x=Q(rot))
            posp = geom.structure.Position(None, z=+1*off)
            posm = geom.structure.Position(None, z=-1*off)
        else:
            posp = geom.structure.Position(None, y=+1*off)
            posm = geom.structure.Position(None, y=-1*off)

        return (geom.structure.Placement(None, volume=bar, pos=posp, rot=rot),
                geom.structure.Placement(None, volume=bar, pos=posm, rot=rot))

    def construct(self, geom):
        children = list()

        cross_length = self.width-2*self.bar_width

        children += self.make_sides('vol'+self.name+'LongSide', geom, self.height, self.width, '90 degree')
        children += self.make_sides('vol'+self.name+'ShortSide', geom, cross_length, self.height)

        center = 0.5*self.height # measure cross centers from top of frame
        cross_center = 0.5* self.height - self.bar_width
        for count in range(self.ncrosses):
            cross_center -= (self.cross_gap + 0.5* self.cross_width)
            volname = 'vol%sCross%d' % (self.name, count+1)
            bar = self.make_bar_tube(volname, geom, self.thickness, self.cross_width, cross_length)
            pos = geom.structure.Position(None, y=cross_center)
            cross_center -= 0.5* self.cross_width
            place = geom.structure.Placement(None, volume=bar, pos=pos)
            children.append(place)

        # use envelope volume since GDML hates assemblies
        volname = 'vol%s' % self.name
        shape = geom.shapes.Box(None, dx=0.5*self.thickness, dy=0.5*self.height, dz=0.5*self.width)
        env_vol = geom.structure.Volume(volname, material=self.material,
                                        shape=shape, placements = children)
        self.add_volume(env_vol)


class TPC(gegede.builder.Builder):
    '''
    Build a single TPC drift volume
    '''
    defaults = dict(
        length = Q('303mm') - 0.5*Q('2.94 inch')-Q('25.4 inch'), # short drift
        height = Q('2002.1 mm') - 2.0*Q('0.006 inch'), # based on field cage
        width = (Q('1588.5mm')-2.0*Q('0.006 inch'))/3.0, # based on field cage
        material = 'LiquidArgon',
        )

    def construct(self, geom):
        shape = geom.shapes.Box(None, 0.5*self.length, 0.5*self.height, 0.5*self.width)
        vol = geom.structure.Volume('vol'+self.name, material = self.material, shape=shape)
        self.add_volume(vol)
        

class Drift(gegede.builder.Builder):
    '''Build a drift volume.  

    This consists of a liquid argon box, wrapped by a field cage and with 4 drift sub-volumes.  

    The sub-builders are assumed to be in order:

    cage, small-tpc, medium-tpc, large-tpc

    The large-tpc's volume is placed twice.

    Result has +X pointing at the wires.

    Note, full 35t has two of these, one with a "short" and one with a
    "long" drift.  One of which must have a 180 degree rotation.

    '''
    defaults = dict(
        # x-offset from center of the cage volume
        x_cage_offset = -0.5*(Q('12.7mm') - Q('10.0mm')),
        # Nominal placement of small+medium drifts in Y center them.  This allows an additional Y-offset
        y_sm_tpc_offset = Q('0m'),
        material = 'LiquidArgon',
        length = Q('2259mm') - Q('1 inch'), # long
    )

    def construct(self, geom):
        children = list()

        volumes = [sb.get_volume(0) for sb in self.get_builders()]
        cage_vol, stpc_vol, mtpc_vol, ltpc_vol = volumes

        shapes = [geom.get_shape(v) for v in volumes]
        cage_shape, stpc_shape, mtpc_shape, ltpc_shape = shapes

        # place cage
        pos = geom.structure.Position(None, x=self.x_cage_offset)
        place = geom.structure.Placement(None, volume=cage_vol, pos=pos)
        children.append(place)

        # place large
        for sign in [-1, +1]:
            pos = geom.structure.Position(None, z=sign*(stpc_shape.dz+ltpc_shape.dz))
            place = geom.structure.Placement(None, volume=ltpc_vol, pos=pos)
            children.append(place)

        # place medium nominally up in Y by small's dy 
        pos = geom.structure.Position(None, y=+1*stpc_shape.dy + self.y_sm_tpc_offset)
        place = geom.structure.Placement(None, volume=mtpc_vol, pos=pos)
        children.append(place)

        # place small nominally down in Y by medium's dy
        pos = geom.structure.Position(None, y=-1*mtpc_shape.dy + self.y_sm_tpc_offset)
        place = geom.structure.Placement(None, volume=stpc_vol, pos=pos)
        children.append(place)

        # use envelope volume since GDML hates assemblies
        cage_builder = self.get_builder(0)
        volname = 'vol%s' % self.name
        shape = geom.shapes.Box(None, 
                                dx=0.5*self.length, 
                                dy=0.5*cage_builder.height,
                                dz=0.5*cage_builder.width)
        env_vol = geom.structure.Volume(volname, material=self.material,
                                        shape=shape, placements = children)
        self.add_volume(env_vol)

