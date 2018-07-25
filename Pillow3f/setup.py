from setuptools import setup
with open('README.txt', 'r') as readme:
    longdescription = readme.read()
    
setup(name='Pillow3f',
      long_description=longdescription,
      version='1.0',
      description='A non-realtime 3D rendering application',
      packages=['Pillow3f'],
      install_requires = ['numpy', 'pillow']
     )
