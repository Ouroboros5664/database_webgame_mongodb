
import os
import sys

SCRIPT = os.path.realpath(sys.argv[0])
PROJECT = os.path.dirname(SCRIPT)

print 'script:', SCRIPT
print 'projet:', PROJECT

HOME   = os.path.basename(sys.argv[0])
PUBLIC = HOME + '/public'

PATH_ACTION = os.path.basename(__file__)

print 'HOME', HOME
print 'PUBL', PUBLIC
print 'ACTN', PATH_ACTION

import compact
import template
import database
import http


