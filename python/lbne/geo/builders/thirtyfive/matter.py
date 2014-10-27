#!/usr/bin/env python
'''
Define the matter required for 35t geometry.
'''

import gegede.builder

class Matter(gegede.builder.Builder):
    '''
    Define the materials for 35t prototype
    '''
    def configure(self, **kwds):
        pass

    def construct(self, geom):
        '''
        Construct matter.

        Naming conventions:

        - element names are lower case, symbols are U[l]
        - mixtures are CamelCase

        Only what is needed is defined

        '''

        hydrogen   = geom.matter.Element("hydrogen",   "H", 1, "1.0079 g/mole")
        carbon     = geom.matter.Element("carbon",     "C", 6, "12.0107 g/mole")
        nitrogen   = geom.matter.Element("nitrogen",   "N", 7, "14.0067 g/mole")
        oxygen     = geom.matter.Element("oxygen",     "O", 8, "15.999 g/mole")
        sodium     = geom.matter.Element("sodium",    "Na", 11, "22.99 g/mole")
        #magnesium  = geom.matter.Element("magnesium", "Mg", 12, "24.305 g/mole")
        aluminum   = geom.matter.Element("aluminum",  "Al", 13, "26.9815 g/mole")
        silicon    = geom.matter.Element("silicon",   "Si", 14, "28.0855 g/mole")
        #phosphorus = geom.matter.Element("phosphorus", "P", 15, "30.973 g/mole")
        #sulphur    = geom.matter.Element("sulphur",    "S", 16, "32.065 g/mole")
        argon      = geom.matter.Element("argon",     "Ar", 18, "39.9480 g/mole")
        #potassium  = geom.matter.Element("potassium",  "K", 19, "39.0983 g/mole")
        calcium    = geom.matter.Element("calcium",   "Ca", 20, "40.078 g/mole")
        chromium   = geom.matter.Element("chromium",  "Cr", 24, "51.9961 g/mole")
        iron       = geom.matter.Element("iron",      "Fe", 26, "55.8450 g/mole")
        nickel     = geom.matter.Element("nickel",    "Ni", 28, "58.6934 g/mole")
        copper     = geom.matter.Element("copper",    "Cu", 29, "63.546 g/mole")
        #titanium   = geom.matter.Element("titanium","  Ti", 22, "47.867 g/mole")
        #bromine    = geom.matter.Element("bromine",   "Br", 35,"79.904 g/mole")


        geom.matter.Mixture('Air', density = '0.001205 g/cc',
                            components = ((nitrogen, 0.781154),
                                          (oxygen,   0.209476),
                                          (argon,    0.00934)))

        geom.matter.Mixture('Concrete', density = '2.3 g/cc',
                            components = ((oxygen,   0.530),
                                          (silicon,  0.335), 
                                          (calcium,  0.060),
                                          (sodium,   0.015),
                                          (iron,     0.020),
                                          (aluminum, 0.040)))

        # Density taken from page 10 of 
        # http://lbne2-docdb.fnal.gov:8080/cgi-bin/ShowDocument?docid=6275
        # Molecular formula taken from polyurethane:
        # http://www.chemnet.com/cas/en/9009-54-5/polyurethane-foam.html
        # C3H8N2O
        # Actual ELFOAM formula is "proprietary" woopty doo
        # http://www.elliottfoam.com/pdf/ELFOAM%20Safety%20Data%20Sheet%201401.pdf
        geom.matter.Molecule('Foam', density = '32 kg/m^3',
                             elements = ((carbon, 3),
                                         (hydrogen, 8),
                                         (nitrogen, 2),
                                         (oxygen, 1)))

        geom.matter.Mixture('Stainless', density = '7.9300 g/cc',
                            components = ((carbon,   0.0010),
                                          (chromium, 0.1792),
                                          (iron,     0.7298),
                                          (nickel,   0.0900)))

        geom.matter.Mixture('LiquidArgon', density = '1.40 g/cc',
                            components = ((argon, 1.0),))

        # Fixme: this is really G10/F4 with copper plating.  Use density of former, element of latter
        geom.matter.Mixture('FieldCage', density = '1.850 g/cc', # from wikipedia
                            components = ((copper, 1.0),))
