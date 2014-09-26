#!/usr/bin/env python
'''Build a "larsoft compatible" geometry for the 35t based on what is
seen in lbne35t4apa_v2.gdml '''


import gegede.builder
from gegede import Quantity as Q



class Cryostat(gegede.builder.Builder):
    '''Put together the cryostat. 

    This assembles the cryostat out from these sub-builders

    - TPC_IJ :: build a LiquidArgon drift volume with wire planes at
      one end, extending from wire frame on one end to CPA plane on
      the other and up to a field cage on the other four sides

    - WireFrame :: build a plane of LiquidArgon volume containing the wire
      frame members and optical paddles which will be situated between
      long and short drift volumes.
    
    - CPA :: build a plane of CPA material placed at the either
      non-wire ends of the TPC_IJ volumes

    '''
    defaults = dict(
        # FIXME: these numbers are bogus and taken by eye from ROOT disp of old geom
        x_gap = Q('1 inch'),     # distance between short/long TPC faces
        x_offset = Q('-100 cm'), # distance from cryo center to TPC gap center in X
        y_gap = Q('2 inch'),      # gap between S and M TPCs in Y
        y_offset = Q('-18 cm'), # distance from cryo center to apa1/2 border
        z_gap = Q('1cm'),       # gap between TPCs in Z
        z_offset = Q('0 cm'),  # distance between cryo center and S/M APA centers
        material = 'LiquidArgon',
    )

    def construct(self, geom):

        # The TPC volumes
        # s,m,l
        children = list()
        for height_letter, y_factor in zip('SML', (-1, +1, 0)):
            for drift_letter, x_sign, rot_angle in zip('SL',(-1, +1), (Q('180 deg'), 0)):
                tpcb = self.get_builder('TPC_' + height_letter + drift_letter)

                x_offset = self.x_offset + x_sign * (0.5*self.x_gap + tpcb.hdim[0])

                y_offset = Q('0.0 m')
                z_offset = Q('0.0 m')
                if height_letter in 'SM':
                    y_offset = self.y_offset + y_factor*(0.5*self.y_gap + tpcb.hdim[1])
                    z_factors = [0.0]
                else:
                    # Warning: assumes all TPCs same size in Z!
                    z_offset = self.z_offset + 2.0*tpcb.hdim[2] + self.z_gap
                    z_factors = [-1.0, 1.0]

                vol = tpcb.get_volume(0)
                rot = geom.structure.Rotation(None, y = rot_angle)
                for z_factor in z_factors:
                    pos = geom.structure.Position(None, x=x_offset, y=y_offset, z=z_factor*z_offset)
                    place = geom.structure.Placement(None, volume=vol, pos=pos, rot=rot)
                    children.append(place)
                continue
            continue

        short_drift_distance = 2.0*self.get_builder('TPC_MS').hdim[0]
        long_drift_distance  = 2.0*self.get_builder('TPC_ML').hdim[0]

        tpcs_xtot = 2.0*(short_drift_distance + long_drift_distance) + self.x_gap
        tpcs_ytot =   2.0*self.get_builder('TPC_ML').hdim[1] + 2.0*self.get_builder('TPC_SL').hdim[1] + self.y_gap
        tpcs_ztot = 3*2.0*self.get_builder('TPC_ML').hdim[2] + 2.0*self.z_gap

        # place wire frame volume into gap
        frame_builder = self.get_builder('WireFrame')
        frame_x = -tpcs_xtot + short_drift_distance + 0.5*self.x_gap
        frame_pos = geom.structure.Position(None, x=frame_x)
        frame_place = geom.structure.Placement(None, volume = frame_builder.get_volume(0), pos=frame_pos)
        children.append(frame_place)

        # place two CPA planes
        cpa_builder = self.get_builder('CPA')
        cpa_volume = cpa_builder.get_volume(0)
        cpa_width = 2.0 * geom.get_shape(cpa_volume.shape).dx # warning: assumes box!
        cpa_x = 0.5*(tpcs_xtot + cpa_width)
        for sign in [+1, -1]:
            cpa_pos = geom.structure.Position(None, x= sign*cpa_x)
            cpa_place = geom.structure.Placement(None, volume = cpa_volume, pos=cpa_pos)
            children.append(cpa_place)
            
        shape = geom.shapes.Box(self.name,
                                dx = 0.5*tpcs_xtot + cpa_width,
                                dy = 0.5*tpcs_ytot, # + self.field_cage_thickness,
                                dz = 0.5*tpcs_ztot) # + self.field_cage_thickness)

        top = geom.structure.Volume('vol'+self.name, material=self.material, shape=shape, 
                                    placements = children)
        self.add_volume(top)
        pass

class TPC(gegede.builder.Builder):
    '''Build a TPC

    This builder holds default dimensions for all possible TPCs, be
    they small, medium or large or short or long.

    It knows what type it is based on it's name which should be like:

    TPC_[SML][SL] encoding [height=small,medium,large] and [drift=short,long]

    Individual dimensions may be provided explicitly.

    .hdim holds (dx,dy,dz) of the top volume built
    '''
    defaults = dict(
        x_L = Q('228.443 cm'),  # size of a TPC drift volume in x (long TPCs)
        x_S = Q('28.443 cm'),  # size of a TPC drift volume in x (short TPCs)
        y_s = Q('86.5 cm'), # size of a TPC drift volume in Y (small TPCs)
        y_m = Q('114.5 cm'), # size of a TPC drift volume in Y (medium TPCs)
        y_l = Q('196.0 cm'), # size of a TPC drift volume in Y (large TPCs)
        z_size = Q('53.49 cm'), # size of a TPC drift volume in Z
        material = 'LiquidArgon',
    )

    # note: have to implement this because we are being tricky
    def configure(self, x=None, y=None, z=None, **kwds):
        super(TPC,self).configure(**kwds) # incase user wants to override defaults

        height,drift = self.name.split('_')[-1]
        x = x or getattr(self, 'x_%s' % drift.upper())
        y = y or getattr(self, 'y_%s' % height.lower())
        z = z or self.z_size
        self.hdim = (0.5*x, 0.5*y, 0.5*z)

    def construct(self, geom):
        shape = geom.shapes.Box(self.name, *self.hdim)
        vol = geom.structure.Volume('vol'+self.name, material = self.material, shape=shape)
        # fixme: currently this totally ignores children
        self.add_volume(vol)
        

class CPA(gegede.builder.Builder):
    '''Make one CPA'''

    defaults = dict(
        thick = Q('50.8 mm'),
        height = Q('2131.8 mm'),
        width = Q('1718.1 mm'),
        material = 'Stainless',
    )
    def construct(self, geom):
        shape = geom.shapes.Box(None,
                                dx=0.5*self.thick, 
                                dy=0.5*self.height,
                                dz=0.5*self.width)
        vol = geom.structure.Volume('vol'+self.name, material=self.material, shape=shape)
        self.add_volume(vol)

class WireFrameOne(gegede.builder.Builder):
    '''Make one wire frame.

    This is in the form of a "ladder" made up of a hollow, rectangular
    frame of some cross-sectional dimension with some number of ladder
    rungs ("cross") which may have different cross-sectional
    dimensions.

    Defaults are for the "large" frames that go on either side of the
    "small" and "medium" ones.  To configure small/medium only the
    height and cross_centers list likely needs redefining.
    cross_centers are measured from top of frame to center of cross
    member.

    The length of the ladder runs along Y and the width is in Z.  That
    is, no rotation is needed to put it in place.  The frame is
    assembled centered on its center of mass (not counting cross pieces).

    '''

    defaults = dict(
        frame_dim = (Q('2 inch'), Q('4 inch')), # dimensions of the main frame members
        cross_dim = (Q('2 inch'), Q('3 inch')), # dimensions of the main cross members
        height = Q('2036 mm'),                  # full top-to-bottom height
        width = Q('504 mm'),                    # full side-to-side width
        # fixme: 5mm is invented, and assumed universal - needs checking
        thick = Q('5 mm'),                      # rectangular tube thickness
        cross_centers = (Q('699.9 mm'), Q('1336.3 mm')),
        bar_material = 'Stainless',
        material = 'LiquidArgon',
    )
    def make_bar_tube(self, geom, x_size, y_size, length):
        '''
        Make a bar of <length> along z-axis and x/y_size (X, Y)-axes with walls of <thick>.
        '''
        thick = self.thick      # note: assumed universal
        bar_outer = geom.shapes.Box(None, 0.5*x_size,       0.5*x_size,       0.5*length)
        bar_inner = geom.shapes.Box(None, 0.5*x_size-thick, 0.5*y_size-thick, 0.5*length)
        bar_shape = geom.shapes.Boolean(None, 'subtraction', 
                                        first=bar_outer, second=bar_inner)
        return geom.structure.Volume(None, material = self.material, shape=bar_shape)

    def make_sides(self, geom, length, width, rot = None):
        dim = self.frame_dim
        if rot: rot = geom.structure.Rotation(None, x=Q(rot))
        bar = self.make_bar_tube(geom, dim[0], dim[1], length)
        off = 0.5*(width - dim[1])
        posp = geom.structure.Position(None, z=+1*off)
        posm = geom.structure.Position(None, z=-1*off)
        return (geom.structure.Placement(None, volume=bar, pos=posp, rot=rot),
                geom.structure.Placement(None, volume=bar, pos=posm, rot=rot))

    def construct(self, geom):
        children = list()

        cross_length = self.height-2*self.frame_dim[1]

        children += self.make_sides(geom, self.height, self.width, '90 deg')
        children += self.make_sides(geom, self.width, cross_length)

        center = 0.5*self.height # measure cross centers from top of frame
        for cross in self.cross_centers:
            center -= cross
            bar = self.make_bar_tube(geom, self.cross_dim[0], self.cross_dim[1], cross_length)
            pos = geom.structure.Position(None, y=center)
            place = geom.structure.Placement(None, volume=bar, pos=pos)
            children.append(place)

        # use envelope volume since GDML hates assemblies
        shape = geom.shapes.Box(None, dx=0.5*self.frame_dim[0], dy=0.5*self.height, dz=0.5*self.width)
        env_vol = geom.structure.Volume('vol' + self.name, material=self.material,
                                        shape=shape, placements = children)
        self.add_volume(env_vol)

class WireFrame(gegede.builder.Builder):
    '''Assemble the individual wire frames into one big frame.

    Three sub-builders are expected in order: small, medium and large.
    '''

    defaults = dict(
        small_center = 0.5*Q('730.0mm') + Q('4 inch') - 0.5*Q('2002.1mm'),
        medium_center = 0.5*Q('2002.1mm') - 0.5*Q('1196.2mm'),
        large_center = 0.5*Q('2002.1mm') - 0.5*Q('2036.2mm'),
        large_offset = Q('505 mm') + Q('1 inch'),
        material = 'LiquidArgon',
    )
        
    def construct(self, geom):
        children = list()

        maxyext = Q('0 m')

        # small
        s_volume = self.get_builder(0).get_volume(0)
        s_shape = geom.get_shape(s_volume.shape)
        pos = geom.structure.Position(None, y=self.small_center)
        place = geom.structure.Placement(None, volume=s_volume, pos=pos)
        children.append(place)
        maxyext = max(maxyext, self.small_center + s_shape.dx)

        # medium
        m_volume = self.get_builder(1).get_volume(0)
        m_shape = geom.get_shape(m_volume.shape)
        pos = geom.structure.Position(None, y=self.medium_center)
        place = geom.structure.Placement(None, volume=m_volume, pos=pos)
        children.append(place)
        maxyext = max(maxyext, self.medium_center + m_shape.dx)

        # large
        l_volume = self.get_builder(2).get_volume(0)
        l_shape = geom.get_shape(l_volume.shape)
        posm = geom.structure.Position(None, x = -1*self.large_offset, y=self.large_center)
        posp = geom.structure.Position(None, x = +1*self.large_offset, y=self.large_center)
        children += [
            geom.structure.Placement(None, volume=l_volume, pos=posm),
            geom.structure.Placement(None, volume=l_volume, pos=posp)
        ]
        maxyext = max(maxyext, self.large_center + l_shape.dx)


        # envelope
        env_shape = geom.shapes.Box(None, dx=l_shape.dx, dy = maxyext, dz = self.large_offset + l_shape.dz)
        env_vol = geom.structure.Volume('vol' + self.name, material = self.material,
                                        shape=env_shape, placements = children)
        self.add_volume(env_vol)

        
