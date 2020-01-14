from setuptools import setup

setup(
    name='playlister',
    version='0.1.0',
    author='Guillermo Guirao Aguilar',
    author_email='contact@guillermoguiraoaguilar.com',
    py_modules=['playlister'],
    description='Spotify playlist generator',
    url='https://github.com/Funk66/playlister',
    license='MIT',
    classifiers=['Programming Language :: Python :: 3.8'],
    install_requires=['pyyaml', 'urllib3', 'certifi'],
    packages=['playlister'],
    entry_points={
        'console_scripts': ['playlister=playlister.client:main']
    })
