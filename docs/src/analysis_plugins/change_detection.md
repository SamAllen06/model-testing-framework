# Change Detection Plugin
APP/src/analysis_plugins/change_detection/

The Change Detection plugin is a [SampleGroupAnalyzer](../analysis/sample_group_analyzer.md)
meant for identifying which outputs change from a reference as a result of
changes to model constants across an entire Sample Group. For each Sample Group, it
generates two lists with the following headers, where j is the number of total constants
used and k is the number of total outputs changed:

Constants:\
&emsp; constant_1\
&emsp; constant_2\
&emsp; $\vdots$\
&emsp; constant_j

Outputs:\
&emsp; output_1\
&emsp; output_2\
&emsp; $\vdots$\
&emsp; output_k
