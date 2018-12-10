==========================
foglamp-south-wind-sensors
==========================

FogLAMP South Plugin for a group of sensors used on a wind turbine. `read more <https://github.com/oshadmon/foglamp-south-wind-sensors/blob/master/python/foglamp/plugins/south/wind_sensors>`_ 


**************************
Packaging for wind-sensors
**************************

This repo contains the scripts used to create a foglamp-south-wind-sensors package. 

Install PyFTDI (prerequisite) 
=============================
.. code-block:: console

  cd $HOME
  git clone https://github.com/eblot/pyftdi.git
  cd $HOME/pyftdi 
  python3 setup.py

The make_deb script
===================

.. code-block:: console

  $ ./make_deb help
  make_deb help [clean|cleanall]
  This script is used to create the Debian package of foglamp south wind_sensors

  Arguments:
  help     - Display this help text
  clean    - Remove all the old versions saved in format .XXXX
  cleanall - Remove all the versions, including the last one
 


Building a Package
==================

Finally, run the ``make_deb`` command:


.. code-block:: console

    $ ./make_deb
    The package root directory is         : /home/ubntu/foglamp-south-wind-sensors
    The FogLAMP south wind_sensors version is : 1.0.0
    The package will be built in          : /home/ubntu/foglamp-south-wind-sensors/packages/build
    The package name is                   : foglamp-south-wind-sensors-1.0.0

    Populating the package and updating version file...Done.
    Building the new package...
    dpkg-deb: building package 'foglamp-south-wind-sensors' in 'foglamp-south-wind-sensors-1.0.0.deb'.
    Building Complete.
    The result will be:

.. code-block:: console

  $ ls -l packages/build/
    total 12
    drwxrwxr-x 4 ubntu ubntu 4096 Dec 10 13:09 foglamp-south-wind-sensors-1.0.0
    -rw-r--r-- 1 ubntu ubntu 7392 Dec 10 13:09 foglamp-south-wind-sensors-1.0.0.deb

If you execute the ``make_deb`` command again, you will see:

.. code-block:: console

    $ ./make_deb
    The package root directory is         : /home/ubntu/foglamp-south-wind-sensors
    The FogLAMP south wind_sensors version is : 1.0.0
    The package will be built in          : /home/ubntu/foglamp-south-wind-sensors/packages/build
    The package name is                   : foglamp-south-wind-sensors-1.0.0

    Saving the old working environment as foglamp-south-wind-sensors-1.0.0.0001
    Populating the package and updating version file...Done.
    Saving the old package as foglamp-south-wind-sensors-1.0.0.deb.0001
    Building the new package...
    dpkg-deb: building package 'foglamp-south-wind-sensors' in 'foglamp-south-wind-sensors-1.0.0.deb'.
    Building Complete.

    $ ls -l packages/build/
    total 24
    drwxrwxr-x 4 ubntu ubntu 4096 Dec 10 14:08 foglamp-south-wind-sensors-1.0.0
    drwxrwxr-x 4 ubntu ubntu 4096 Dec 10 13:09 foglamp-south-wind-sensors-1.0.0.0001
    -rw-r--r-- 1 ubntu ubntu 7392 Dec 10 14:08 foglamp-south-wind-sensors-1.0.0.deb
    -rw-r--r-- 1 ubntu ubntu 7392 Dec 10 13:09 foglamp-south-wind-sensors-1.0.0.deb.0001

... where the previous build is now marked with the suffix *.0001*.

