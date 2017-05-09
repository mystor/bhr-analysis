import sys
import os
import json
import urllib2 # NOTE: Using this instead of requests as I can't install python packages on people.m.o
import shutil

#URL = 'https://symbols.dev.mozaws.net'
URL = 'http://symbolapi.mozilla.org'

DATE = sys.argv[1]

FILENAME = 'dump-{}.json'.format(DATE)
print "loading " + FILENAME

OUTDIR = "symbolicated-{}".format(DATE)

with open(FILENAME) as f:
    hangs = json.load(f)

# Filter out uninteresting hangs
def good_hang(hang):
    return len(hang['nativeStack']['memoryMap']) > 0
hangs = [hang for hang in hangs if good_hang(hang)]

# Create the results directory
try:
    shutil.rmtree(OUTDIR)
except:
    pass
os.mkdir(OUTDIR)

# Handle each of the hangs
for (i, d) in enumerate(hangs):
    try:
        print "{}/{}".format(i, len(hangs))

        d['nativeStack']['version'] = 4
        nstack_data = json.dumps(d['nativeStack'])

        r = urllib2.urlopen(url=URL, data=nstack_data).read()
        d['nativeStack'] = json.loads(r)

        with open('{}/{}.json'.format(OUTDIR, i), 'w') as f:
            json.dump(d, f)

    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        print "There was an error while handling i = ", i
        print e

