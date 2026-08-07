# NetCDF Sampler
APP/src/sampling_plugins/netcdf_cases/netcdf_sampler.py

## Purpose
NetCDF Sampler is a subclass of [Sampler](../../sampling/sampler.md) that reads NetCDF 
case files from the directory specified in 
[its config file](../../../config/sampling_plugins/netcdf_cases.md) to create 
SampleGroup(s). Each NetCDF file creates one SampleGroup and contains all the values
needed for the model constants for each individual Sample. 

## Functionality
Reads NetCDF case files in the specified directory. NetCDF case files use the following
format, where x is the number of cases and n is the number of constants used:

netcdf {\
dimensions:\
&emsp; cases = UNLIMITED ; // (x currently)\
variables:\
&emsp; double constant_1(cases) ;\
&emsp; double constant_2(cases) ;\
&emsp; $\vdots$\
&emsp; double constant_n(cases) ;\
}
