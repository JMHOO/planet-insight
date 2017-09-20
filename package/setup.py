from setuptools import setup

setup(name='insight',
      version='0.0.1',
      description='Planet Insight ',
      url='https://github.com/JMHOO/planet-insight',
      author='Jimmy Hu',
      author_email='huj22@uw.edu',
      license='MIT',
      packages=['insight'],
      install_requires=['Flask', 'keras', 'simple-settings'],
      zip_safe=False)