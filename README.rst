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

.. code-block:: console

 $ ./make_deb help
 make_deb help [clean|cleanall]
 This script is used to create the Debian package of foglamp south wind_sensors

 Arguments:
 help     - Display this help text
 clean    - Remove all the old versions saved in format .XXXX
 cleanall - Remove all the versions, including the last one
