# Command Line Interface
APP/src/cli.py

## Purpose
The CLI script acts as the interface between the user and the testing program.
It is also the sole entry point to the program.

## Functionality
The CLI is responsible for providing [root](root.md) with the configuration
directory the user wants to use. Currently, it will also automatically enable
[console output](output/views/console.md), [file output](output/views/file.md),
and [logs](output/views/logs.md).

Additionally, the CLI prompts the user to confirm that, after seeing what
plugins were able to load and how long the testing process should take, they
still wish to continue with testing. If the user confirms, the CLI will tell
the [tester](tester.md) to begin testing.

## Usage
```
python3 cli.py <path_to_config_dir>
```

See `cli.py -h` for more.
