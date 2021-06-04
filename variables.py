#implement as environment variables for DAFNI
#all variables are stored as strings

import os

#set to True to use strings from environment variables
#set to False to use strings from this script
DAFNI = False

#type string
EXTENT = '459000,202000,501000,244000'
def get_extent():
	if DAFNI:
		return os.getenv('EXTENT')
	else:
		return EXTENT	

#type string
LAYER_NAME = 'test_region'
def get_layer_name():
	if DAFNI:
		return os.getenv('LAYER_NAME')
	else:
		return LAYER_NAME	
		