from setuptools import setup

from new import __version__


setup(name='radiss',
      version=__version__,
      author='Guillermo Guirao Aguilar',
      author_email='contact@guillermoguiraoaguilar.com',
      py_modules=['radiss'],
      # requires=['spotipy'],
      description='Smarter data structures',
      url='https://github.com/Funk66/radiss',
      license='MIT',
      classifiers=['Programming Language :: Python :: 3.7'])
