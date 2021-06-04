import subprocess
from pathlib import Path
import os
import logging
import variables as v

#------------------------------------------------------------------------------------------------------------------------------
#rasterise_1m

#configure directory/subdirectories
current_dir = str(Path.cwd())
#print(current_dir)
inputs = Path(current_dir + '/data/inputs/')
#print(inputs)
temp = Path(current_dir + '/data/temp/')
#print(temp)
outputs = Path(current_dir + '/data/outputs/')
#print(outputs)
temp.mkdir(exist_ok=True)
outputs.mkdir(exist_ok=True)

#configure output
logger = logging.getLogger('udm-rasterise-coverage')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(outputs / 'udm-rasterise-coverage.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

#get input polygons
input_files = []
for ext in ['shp', 'gpkg']:
    input_files.extend(list(inputs.glob(f"*/*.{ext}")))

assert len(input_files) > 0, 'No input files found'
selected_file = input_files[0]

#get extent 'xmin,ymin,xmax,ymax'
extent = v.get_extent()
if extent == 'None' or extent is None:
    extent = []
else:
    extent = ['-te', *extent.split(',')]

#------------------------------------------------------------------------------------------------------------------------------
#rasterise_1m

logger.info(f'Rasterizing {selected_file}')

subprocess.call(['gdal_rasterize',
                 '-burn', '1',		#fixed value to burn for all objects
                 '-tr', '1', '1',	#target resolution <xres> <yres>
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',	#creation options
                 '-ot', 'UInt16',	#output data type
                 '-at',  			#enable all-touched rasterisation
                 *extent,			#'-te' <xmin> <ymin> <xmax> <ymax> 
                 selected_file, temp / 'rasterise_1m.tif'])	#src_datasource, dst_filename

logger.info('Rasterizing completed')

#------------------------------------------------------------------------------------------------------------------------------
#sum_resample_100m

logger.info('Sum resampling raster')

subprocess.call(['gdalwarp',
                 '-tr', '100', '100',	#target resolution <xres> <yres>
                 '-r', 'sum',			#resampling method e.g. sum OR mode
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',	#creation options
                 '-ot', 'UInt16',		#output data type
                 '-overwrite',			#overwrite target dataset if already exists
                 temp / 'rasterise_1m.tif', temp / 'sum_resample_100m.tif'])	#srcfile, dstfile

logger.info('Sum resampling completed')

#------------------------------------------------------------------------------------------------------------------------------
#translate

#get layer name
layer_name = v.get_layer_name() + '_coverage_100m.asc'

logger.info('Translating raster')

subprocess.call(['gdal_translate',
                 '-tr', '100', '100',	#target resolution <xres> <yres>                
                 '-ot', 'UInt16',		#output data type    
                 '-a_nodata', '0',		#set nodata value             
                 temp / 'sum_resample_100m.tif', outputs / layer_name])	#srcfile, dstfile

logger.info('Translating completed')

#------------------------------------------------------------------------------------------------------------------------------

