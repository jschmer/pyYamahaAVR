from setuptools import setup

setup(name='pyYamahaAVR',
      version='0.1',
      description='Generic API for your Yamaha AVR devices',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Topic :: Home Automation',
            'Topic :: Multimedia',
      ],
      url='https://github.com/jschmer/pyYamahaAVR',
      author='jschmer',
      license='MIT',
      packages=['pyYamahaAVR'],
      install_requires=[
            'requests',
      ],
      include_package_data=True,
      zip_safe=False)