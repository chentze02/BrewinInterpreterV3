#Brewin# Interpreter V3

- `intbase.py`, the base class and enum definitions for the interpreter
- `bparser.py`, a static `parser` class to parse Brewin programs

- `interpreterv2.py`, a working top-level interpreter for project 2 that mostly delegates interpreting work to:
  - `classv2.py` which handles class, field, and method definitions
  - `env2.py` which handles the program environment (a stack-based approach to accommodate local variables)
  - `objectv2.py` which additional implements inheritance and method calling; most of the code is here!
  - `type_valuev2.py` which additionally manage type checking

- `interpreterv1.py`, a working top-level interpreter for project 1 that mostly delegates interpreting work to:
  - `classv1.py` which handles class, field, and method definitions
  - `env1.py` which handles the program environment (a map from variables to values)
  - `objectv1.py` which handles operations on *objects*, which include statements, expressions, etc; most of the code is here!
  - `type_valuev1.py` which has classes to create type tags

