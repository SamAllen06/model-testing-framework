# Plugin Whitelist
APP/config/plugin_whitelist.json

## Purpose
The plugin whitelist is a json file listing the names of sampling and analysis
plugins that should be loaded. It provides a way to allow researchers to store
more plugins than they need to run at the current moment inside the plugin
directories.

## Example
With this directory structure:
```
sampling_plugins/
├── plugin1
├── plugin2
└── plugin3
analysis_plugins/
├── plugin1
├── plugin2
└── plugin3
```

And the plugin whitelist contents:
```
{
  "sampling": ["plugin2"],
  "analysis": ["plugin1", "plugin3"]
}
```

Only sampling plugin 2 and analysis plugins 1 and 3 will be loaded by
[PluginLoader](../src/plugin_loading/plugin_loader.md).
