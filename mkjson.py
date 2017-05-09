# If you're looking at this code, please know that I take no pride in it. It is
# some of the ugliest code I have ever written.
#
# If you want to make this web view actually usable, you probably want to scrap
# this and start again from square 0.

import sys
import os
import json
import cgi
import shutil

from collections import defaultdict

from util import DATE, NAME_BASE

# Read in the symbolicated data into memory
IN_PATH = 'symbolicated-{}'.format(DATE)

raw_hangs = []
for path in os.listdir(IN_PATH):
    with open(os.path.join(IN_PATH, path)) as f:
        raw_hangs.append(json.load(f))

print "Data read in successfully"

try:
    os.mkdir('out')
except:
    pass
try:
    os.mkdir('out/{}'.format(NAME_BASE))
except:
    pass

with open('out/{}/hangs.json'.format(NAME_BASE), 'w') as f:
    json.dump(raw_hangs, f, indent=2)
