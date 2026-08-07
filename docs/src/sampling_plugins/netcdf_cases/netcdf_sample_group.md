# NetCDF Sample Group
APP/sampling_plugins/mtf_netcdf_cases/netcdf_sample_group.py

## Purpose
A NetCDF Sample Group is the NetCDF Cases plugin's implementation of 
[SampleGroup](../../sampling/sample_group.md). It reads in a NetCDF file with a
dimension (cases) representing the number of Samples and variables representing all the values
of the constants for each Sample. 

## Functionality
On instantiation, the NetCDFSampleGroup will read its NetCDF file and create a single
Sample from the values of each variable at a particular indice along the cases
dimension. It repeats this for every indice along the cases dimension until it has a
full SampleGroup. 
