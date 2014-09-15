from setuptools import setup

setup(name = 'lbne-geometry',
      version = '0.0',
      description = 'Geometry Description for LBNE',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/LBNE/lbne-geometry',
      package_dir = {'':'python'},
      packages = ['lbne','lbne.geo','lbne.geo.builders'],
      # These are just what were developed against.  Older versions may be okay.
      install_requires=[
          "gegede",
      ],
  )

