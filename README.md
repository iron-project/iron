
# Table of Contents

1.  [develop](#org65b8647)
    1.  [setup](#org40083d2)
    2.  [unittest](#orgca63b67)
    3.  [flask](#org8f13b19)


<a id="org65b8647"></a>

# develop

    $ git clone https://github.com/RainMark/iron.git
    $ cd iron
    $ python3.7 -m venv env # init
    $ source ./env/bin/activate
    $ pip install -r requirements.txt # init


<a id="org40083d2"></a>

## setup

-   create `iron/etc/iron.conf`

    $ tree iron/etc
    iron/etc
    ├── iron.conf
    └── iron.sql
    
    0 directories, 2 files
    
    $ cat iron/etc/iron.conf
    [Default]
    TmpPath = /tmp/iron
    DataPath = /iron
    
    [Baidu]
    User = xxx
    Password = xxx


<a id="orgca63b67"></a>

## unittest

    $ python -m unittest iron/*/*_test.py


<a id="org8f13b19"></a>

## flask

    $ python setup.py sdist bdist_wheel
    $ python setup.py develop
    $ python iron/controller/iron_controller.py

