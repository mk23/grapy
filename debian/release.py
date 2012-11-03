#!/usr/bin/env python2.7

import datetime
import re
import subprocess
import sys

package = subprocess.check_output('dh_listpackages').strip()
v_major = datetime.date.today().strftime('%Y%m%d')
v_minor = '001'
changes = []

print 'finding ...'
find = re.match(r'%s\.(\d+)\.(\d+)$' % package, sorted(subprocess.check_output(['git', 'tag']).split('\n'))[-1])
if find:
    if v_major == find.group(1):
        v_minor = '%03d' % (int(find.group(2)) + 1)

    print 'looking ...'
    changes = subprocess.check_output(['git', 'log', '--oneline', '%s..HEAD' % find.group(0)]).strip().split('\n')[::-1]

print 'creating ...'
subprocess.check_output(['dch', '--newversion', '%s.%s' % (v_major, v_minor), 'Tagging %s.%s' % (v_major, v_minor)])
for line in xrange(len(changes)):
    if not changes[line]:
        continue

    print 'appending ...'
    subprocess.check_output(['dch', '--append', '[%03d] %s' % (line + 1, changes[line].strip().split(' ', 1)[1])])

if '--commit' in sys.argv:
    print 'adding ...'
    subprocess.check_output(['git', 'add', 'debian/changelog'])
    print 'committing ...'
    subprocess.check_output(['git', 'commit', '-m', 'Tagging %s.%s' % (v_major, v_minor)])
    print 'tagging ...'
    subprocess.check_output(['git', 'tag', '%s.%s.%s' % (package, v_major, v_minor)])
