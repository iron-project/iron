from setuptools import setup, find_packages

long_description = '''

### Links

- https://github.com/iron-project/iron

'''

setup(
    name='iron',
    version='0.0.1',
    author='iron-project',
    author_email='rain.by.zhou@gmail.com',
    description='Distributed network file system',
    long_description=long_description,
    url='https://github.com/iron-project/iron',
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
        'records == 0.5.2',
        'rsa >= 4.0',
        'xxhash >= 1.3.0',
        'PySnooper >= 0.1.0',
        'flask-restplus >= 0.12.1',
        'requests >= 2.22.0',
        'requests-toolbelt >= 0.9.1',
    ],

    entry_points={
        'console_scripts':[
            'iron = iron.controller.iron_controller:main'
        ]
    },
)
