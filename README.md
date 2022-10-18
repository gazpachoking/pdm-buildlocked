# pdm-buildlocked

Adds the ability to build the project using locked dependencies.

This is useful when distributing an application via PyPi. It should probably not be
used if you are developing a library. Packages built this way can cause version 
conflicts when installed alongside other packages. It should be clearly documented that
projects built in this way should be installed with `pipx`, or in their own isolated
virtual environment.

## Installation
This pdm plugin can be installed with the command:

`pdm plugin add pdm-buildlocked`

## Usage
This plugin modifies the built in `pdm build` command to include the `--locked` argument. 
When specified the resulting artifacts will have all their dependencies (including 
transitive ones) pinned to the versions specified in the lock file.

`pdm build --locked`
