# Python console remote interface traffic load (by SNMP) #
sload.py version 0.1.5
http://obrazcov.github.io/sload

REQUIREMENTS:

	Python 2.4
	pysnmp Python library
	- if you have python-setuptools installed then you can install pysnmp library with this command:
	  easy_install pysnmp
	- other way is to use local downloaded pysnmp*.egg file

SCRIPT DEFAULTS:
	
	SNMP version   = v2
	SNMP community = public
	Polling time   = 1 sec

USE:

	sload.py <host>
