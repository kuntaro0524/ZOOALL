#!/bin/bash
# add all python scripts
find . -name '*.py' | xargs git add 

# beamline.ini files
git add Libs/beamline.ini*

# zoo.python
git add zoo.python*
