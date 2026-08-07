# NetCDF4 Output Plugin
APP/src/analysis/plugins/netcdf4_output/

The NetCDF4 Output plugin is a [SampleGroupAnalyzer](../analysis/sample_group_analyzer.md)
intended to be used to save the contents of an entire Sample Group as a single NetCDF4
file. For each Sample Group, it creates a dimension to represent the number of Samples
run. Then, for every constant, it saves its value for each Sample in the Sample Group
and saves that it was a constant as an attribute. Then, for every output, it saves its 
dimensions (if they have not already been saved from another output variable), saves its
contents for each Sample in the Sample Group, and lastly saves that it was an output as
an attribute. 

This order is important because some variables have the same name as some dimensions. If
the variables were saved first, the output file would get mangled when it attempted to
save the dimension of the same name. Instead, all the dimensions are saved first and if
a variable with the same as a dimension is encountered, it will be internally saved as a
non-coordinate variable to differentiate the variable and dimension. This solves the
problem of the file getting mangled. Nevertheless, some tools external to NetCDF4 are
unable to differentiate between non-coordinate variables and dimensions of the same
name. If the user needs to use one of these tools, they can change the value of
'rename_colliding_variables' in netcdf4_output.ini to 'yes'. This will change the name
of the variable to outwardly differentiate it from the dimension of the same name while
saving the original name as an attribute. 

The resulting NetCDF4 file will have the following structure, where x is
the number of Samples in the Sample Group, k is the number of dimensions used, n is the
number of constants, m is the number of outputs, and j, l, and p are positive integers:

netcdf {
dimensions:
    sample_index = x ;
    dimension_1 = j ;
    dimension_2 = l ;
    $\vdots$
    dimension_k = p ;
variables:
    type constant_1(sample_index) ;
        constant_1:variable_type = "constant" ;
    type constant_2(sample_index) ;
        constant_2:variable_type = "constant" ;
    $\vdots$
    type constant_n(sample_index) ;
        constant_n:variable_type = "constant" ;
    type output_1 (sample_index, dimension_1, dimension_2, ... dimension_k) ;
        output_1:variable_type = "output" ;
    type output_2 (sample_index, dimension_1, dimension_2, ... dimension_k) ;
        output_2:variable_type = "output" ;
    $\vdots$
    type output_m(sample_index, dimension_1, dimension_2, ..., dimension_k) ;
        output_m:variable_type = "output" ;
}