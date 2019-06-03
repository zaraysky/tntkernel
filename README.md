# Tarantool kernel for Jupyter notebook

This is very simple implementation with a lot of known and hidden ~gems~ issues:

## Known problems
 - autocomplete works correctly only in one-string cell. If someone knows how `console.completion_handler()` works please let me know
 - when output is long enough and not finished by `...` then next code snippet can get output from this long output
 - `print()` output can be found in `stdout` of tarantool instance. If you need to get value of some variable or even function - just type it in new code cell and press `Run` 

# Run Tarantool instance in Docker
You can use preconfigured docker image of tarantool 
`docker run -e TNT_ADDRESS='127.0.0.1' -p 3312:3312 -p 3301:3301 -e TNT_CONSOLE_PORT='3301' -e TNT_SOCKET_PORT=3312 --rm zaraysky/tntrepo:tntsocketserver`

# Run tarantool locally

If you want to use local tarantool, you can run it using command

`tarantool config.lua`

The source code of `config.lua` is:

```lua
box.cfg{listen=os.getenv('TNT_CONSOLE_PORT') or 3301}

local IP = os.getenv('TNT_ADDRESS') or '127.0.0.1'
local PORT = os.getenv('TNT_SOCKET_PORT') or '3312'
box.schema.user.grant('guest', 'read, write, execute', 'universe', nil, {if_not_exists=true})
require('console').listen(IP .. ':' .. PORT)
```

# Installation

>Please note in you have the kernel installed you have to uninstall it using
`jupyter kernelspec uninstall tntkernel`

```bash
# Clone kernel source from GitHub
mkdir jupyter
cd jupyter
python3 -m venv venv
source venv/bin/activate
pip install jupyter tarantool


git clone git@github.com:zaraysky/tntkernel.git

jupyter kernelspec install tntkernel
```

# Start it
Just run 
```bash
jupyter notebook
```


