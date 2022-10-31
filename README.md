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
Locked build mode can be enabled by including the following in your `pyproject.toml`
file. When enabled, running `pdm build` or `pdm publish` will cause the resulting 
distribution will have all dependencies (including transitive ones) pinned to the 
versions specified in the lock file.

```toml
[tool.pdm.build]
buildlocked = true
```
