# Tarantool kernel for Jupyter notebook

This is very simple implementation with a lot of known and hidden ~gems~ issues:

## Known problems
 - autocomplete is not yet realized and I have no idea how to do in easy way
 - when output is long enough and not finished by `...` then next code snippet can get output from this long output
 - `print()` output can be found in `stdout` of tarantool instance. If you need to get value of some variable or even function - just type it in new code cell and press `Run` 

# Installation

jupyter kernelspec install --user tntkernel
