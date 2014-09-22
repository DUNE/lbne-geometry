#!/usr/bin/env python
'''Build a "larsoft compatible" geometry for the 35t based on what is
seen in lbne35t4apa_v2.gdml '''


import gegede.builder
from gegede import Quantity as Q



class Cryostat(gegede.builder.Builder):
    '''Put together the cryostat. 

    '''
    defaults = dict(
        # FIXME: these numbers are bogus and taken by eye from ROOT disp of old geom
        x_gap = Q('10 cm'),     # distance between short/long TPC faces
        x_offset = Q('-100 cm'), # distance from cryo center to TPC gap center in X
        y_gap = Q('1 cm'),      # gap between S and M TPCs in Y
        y_offset = Q('-18 cm'), # distance from cryo center to apa1/2 border
        z_gap = Q('1cm'),       # gap between TPCs in Z
        z_offset = Q('0 cm'),  # distance between cryo center and S/M APA centers
        material = 'LiquidArgon',
    )

    def construct(self, geom):
        tpc_builders = {b.name:b for b in self.builders if b.name.startswith('TPC_')}
        
        # The TPC volumes
        # s,m,l
        children = list()
        for height_letter, y_factor in zip('SML', (-1, +1, 0)):
            for drift_letter, x_sign, rot_angle in zip('SL',(-1, +1), (Q('180 deg'), 0)):
                tpcb = tpc_builders['TPC_' + height_letter + drift_letter]

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

                vol = tpcb.volumes[0]
                rot = geom.structure.Rotation(None, y = rot_angle)
                for z_factor in z_factors:
                    pos = geom.structure.Position(None, x=x_offset, y=y_offset, z=z_factor*z_offset)
                    place = geom.structure.Placement(None, volume=vol, pos=pos, rot=rot)
                    children.append(place)
                continue
            continue

        xtot = 2.0*tpc_builders['TPC_ML'].hdim[0] + tpc_builders['TPC_MS'].hdim[0] + self.x_gap
        ytot = 2.0*tpc_builders['TPC_ML'].hdim[1] + 2.0*tpc_builders['TPC_SL'].hdim[1] + self.y_gap
        ztot = 3*2.0*tpc_builders['TPC_ML'].hdim[2] + 2.0*self.z_gap
        dim = (0.5*xtot, 0.5*ytot, 0.5*ztot)


        shape = geom.shapes.Box(self.name, *dim)
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
        
