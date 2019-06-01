from setuptools import setup, find_packages

with open('README.md', 'r') as inf:
    long_description = inf.read()

setup(
    name='iron',
    version='0.0.1',
    author='RainMark',
    author_email='rain.by.zhou@gmail.com',
    description='Distributed network file system',
    long_description=long_description,
    url='https://github.com/RainMark/iron',
    classifiers=[
        'Environment :: MacOS X',
        'Environment :: X11 Applications',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'License :: OSI Approved :: MIT License',
    ],

    # packages=['iron'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires = [
        'xxhash >= 1.3.0',
    ],

    entry_points={
        'console_scripts':[
            'iron = iron.controller.iron_controller:main'
        ]
    },
)
