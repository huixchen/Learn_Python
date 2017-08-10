import os, re
from datetime import datetime

from fabric.api import *

env.user = 'cuichen'
env.sudo_user = 'root'
env.hosts = 'ubuntu@ec2-34-213-152-94.us-west-2.compute.amazonaws.com'

db_user = 'awesome'
db_password = 'awesome'


_TAR_FILE = 'dist-awesome.tar.gz'

def build():
    includes = ['static', 'template', '*.py']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    local('rm -f dist/{}'.format(_TAR_FILE))
    with lcd(os.path.join(_current_path(), 'www')):
        cmd = ['tar', '--dereference', '-czvf', '../dist/{}'.format(_TAR_FILE)]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cm.extend(includes)
        local(''.join(cmd))
