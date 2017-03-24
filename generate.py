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

DATE = sys.argv[1]

BOOTSTRAP_CSS_URL = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
BOOTSTRAP_CSS_LINK = '<link rel="stylesheet" href="{}">'.format(BOOTSTRAP_CSS_URL)

# Read in the symbolicated data into memory
IN_PATH = 'symbolicated-{}'.format(DATE)

raw_hangs = []
for path in os.listdir(IN_PATH):
    with open(os.path.join(IN_PATH, path)) as f:
        raw_hangs.append(json.load(f))

by_stack = defaultdict(list)
for hang in raw_hangs:
    by_stack[json.dumps(hang['stack'])].append(hang)

count_by_stack = defaultdict(int)
for key, hangs in by_stack.iteritems():
    for hang in hangs:
        count_by_stack[key] += 1

sorted_stacks = sorted(count_by_stack.keys(), key=lambda k: -count_by_stack[k])

# Generate the output HTML data
try:
    os.mkdir('out')
except:
    pass
try:
    os.mkdir('out/{}'.format(DATE))
except:
    pass

# Create the index file
with open('out/{}.html'.format(DATE), 'w') as f:
    f.write("<!doctype html>\n")
    f.write(BOOTSTRAP_CSS_LINK + "\n")

    f.write('<div class="container">\n')
    f.write('<h1>{}</h1>\n'.format(DATE))

    f.write('<table class="table">\n')
    f.write("<tr><th>Count</th><th>Stack</th><th>Link</th></tr>\n")
    for idx, stack in enumerate(sorted_stacks):
        f.write("<tr>\n")

        # Count
        f.write("<td>{}</td>\n".format(count_by_stack[stack]))

        # (pseudo-)Stack
        f.write("<td>\n")
        for seg in json.loads(stack):
            f.write(cgi.escape(seg) + "<br>\n")
        f.write("</td>\n")

        # Link to native stacks
        f.write('<td><a href="{}/{}.html">link</a></td>'.format(DATE, idx))

        f.write("</tr>\n")
    f.write("</table>\n")
    f.write("</div>\n")


# Create each of the individual files
for idx, stack in enumerate(sorted_stacks):
    count_by_native_stack = defaultdict(int)
    for hang in by_stack[stack]:
        native = hang['nativeStack']['symbolicatedStacks'][0]
        count_by_native_stack[json.dumps(native)] += 1

    sorted_native_stacks = sorted(count_by_native_stack.iteritems(), key=lambda (ns, cnt): -cnt)

    with open('out/{}/{}.html'.format(DATE, idx), 'w') as f:
        f.write("<!doctype html>\n")
        f.write(BOOTSTRAP_CSS_LINK + "\n")

        f.write('<div class="container">\n')
        f.write('<h1>{}</h1>\n'.format(DATE))

        # Histogram table
        f.write('<table class="table table-condensed">\n')
        f.write('<tr><th>Bucket</th><th>Count</th></tr>\n')
        final_hist = defaultdict(int)
        for hang in by_stack[stack]:
            for k, v in hang['histogram']['values'].iteritems():
                final_hist[k] += v

        for k, v in sorted(final_hist.iteritems(), key=lambda (k, v): int(k)):
            f.write('<tr><td>{}</td><td>{}</td></tr>'.format(k, v))

        f.write('</table>')

        # Native Stacks Table
        f.write('<table class="table">')
        f.write('<tr><th>Count</th><th>Native Stack</th></tr>')
        for ns, cnt in sorted_native_stacks:
            f.write('<tr>\n')
            f.write('<td>{}</td>\n'.format(cnt))
            f.write('<td>\n')
            for frame in json.loads(ns):
                f.write(cgi.escape(frame) + "<br>\n")
            f.write('</td>\n')
            f.write('</tr>\n')

        f.write('</table>\n')

        f.write('</div>\n')
