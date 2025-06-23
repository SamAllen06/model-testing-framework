# Main 
APP/config/main.ini

## Purpose
Configures Lake Temperature Mapper.

## Fields
All paths are relative to `app_root` which itself is relative to the parent
directory of the config directory.

### AppPaths
| Field Name | Type | Description          |
|------------|:----:|----------------------|
| app_root   | Path | Path to the app_root |

### Model
| Field Name         | Type   | Description                                 |
|--------------------|:------:|---------------------------------------------|
| binary             | Path   | Path to the model (executable)              |
| parameters         | Path   | Path to the parameters file (.txt)          |
| parameter_defaults | Path   | Path to the parameter defaults file (.txt)  |
| reference_output   | Path   | Path to the reference output (.txt)         |
| test_output        | Path   | Path to the test output (.txt)              |
| args               | String | Args to pass to the model (space separated) |
