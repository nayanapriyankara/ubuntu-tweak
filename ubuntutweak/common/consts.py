__all__ = (
        'APP',
        'PACKAGE',
        'VERSION',
        'DATA_DIR',
        'init_locale',
        )

import os
import sys
import glob
import gettext

from gi.repository import GLib, Notify

from ubuntutweak import __version__

def applize(package):
    return ' '.join([a.capitalize() for a in package.split('-')])

PACKAGE = 'ubuntu-tweak'
VERSION = __version__
DATA_DIR = '/usr/share/ubuntu-tweak/'
APP = applize(PACKAGE)
CONFIG_ROOT = os.path.join(GLib.get_user_config_dir(), 'ubuntu-tweak')
TEMP_ROOT = os.path.join(CONFIG_ROOT, 'temp')
IS_INSTALLED = True
IS_TESTING = '+' in VERSION

if not os.path.exists(TEMP_ROOT):
    os.makedirs(TEMP_ROOT)

try:
    LANG = os.getenv('LANG').split('.')[0].lower().replace('_','-')
except:
    LANG = 'en-us'

if not __file__.startswith('/usr'):
    datadir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    DATA_DIR = os.path.join(datadir, 'data')
    IS_INSTALLED = False

def init_locale():
    global INIT
    try:
        INIT
    except:
        gettext.install(PACKAGE, unicode=True)

        INIT = True

def install_ngettext():
    #FIXME
    gettext.bindtextdomain(PACKAGE, "/usr/share/locale")
    gettext.textdomain(PACKAGE)

init_locale()

if not Notify.init('ubuntu-tweak'):
    pass

#TODO remove this in the future
OLD_CONFIG_ROOT = os.path.expanduser('~/.ubuntu-tweak/')
if not glob.glob(os.path.expanduser('~/.ubuntu-tweak/*')) and os.path.exists(OLD_CONFIG_ROOT):
    os.rmdir(OLD_CONFIG_ROOT)
