from setuptools import find_packages, setup

setup(name='futhark-server',
      version='1.0.0',
      url='https://github.com/diku-dk/futhark-server-python',
      license='ISC',
      author='Troels Henriksen',
      author_email='athas@sigkill.dk',
      description='Client side implementation of the Futhark server protocol',
      packages=['futhark_server'],
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: ISC License (ISCL)",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.8',
      install_requires=[
          'numpy',
          'futhark_data'
      ],
      zip_safe=True)
