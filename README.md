# Model Testing Framework

## Purpose

The aim of this software is to enable testing of SPEL unit tests by automatically
updating constants used by the test, running it, and analyzing the results. It supports
plugins for both [generating "samples,"](docs/src/sampling_plugins/how_to_create_a_sampling_plugin.md)
or a set of values for each constant, and [analysis plugins](docs/src/analysis_plugins/how_to_create_an_analysis_plugin.md)
that can view the sample used as well as the resulting output values.

## Get Started

In order to run the program, you will need to provide a config directory. (Configuration
options are described in the `docs/config` directory.) You can run it like so:

```bash
mtf config
```

It is worth noting that, while the core program does not require any additional Python
packages, to run some of the plugins, you may need the packages in
`plugin_requirements.txt`.

To enable and disable certain plugins, see [whitelist](docs/config/plugin_whitelist).
