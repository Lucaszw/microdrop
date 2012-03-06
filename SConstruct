import re
import os
import sys

from git_util import GitUtil
from path_find import path_find

AddOption('--wix-sval',
          dest='wix_sval',
          action="store_true",
          help='Skip WiX ICE validation')

env = Environment(ENV=os.environ)
Export('env')

ARGUMENTS['genrst'] = 'python sphinx-autopackage-script/generate_modules.py ../microdrop -d . -s rst -f'
#SConscript('doc/SConstruct')

if os.name == 'nt':
    g = GitUtil(None)
    m = re.match('v(\d+)\.(\d+)-(\d+)', g.describe())
    SOFTWARE_VERSION = "%s.%s.%s" % (m.group(1), m.group(2), m.group(3))
    Export('SOFTWARE_VERSION')

    pyinstaller_path = path_find('Build.py')
    if pyinstaller_path is None:
        raise IOError, 'Cannot find PyInstaller on PATH.'
    BUILD_PATH = pyinstaller_path.joinpath('Build.py')

    version_target = env.Command('microdrop/version.txt', None,
                            'echo %s > $TARGET' % SOFTWARE_VERSION)
    exe = env.Command('microdrop/dist/microdrop.exe', 'microdrop.spec',
                            '%s %s -y $SOURCE' % (sys.executable, BUILD_PATH))
    wxs = env.Command('microdrop.wxs', version_target,
                            'python generate_wxs.py -v %s > $TARGET' % SOFTWARE_VERSION)
    wixobj = env.Command('microdrop.wixobj', wxs,
                            'candle -o $TARGET $SOURCE')
    env.Clean(exe, 'dist') 
    env.Clean(exe, 'build') 
    env.Clean(wixobj, 'microdrop.wixpdb') 
    
    # option to skip ICE validation (buildbot fails without this option) 
    if GetOption('wix_sval'):
        SEVAL = '-sval'
    else:
        SEVAL = ''

    msi = env.Command('microdrop-%s.msi' % SOFTWARE_VERSION, wixobj,
            'light %s -ext WixUIExtension -cultures:en-us $SOURCE '
            '-out $TARGET' % SEVAL)
    AlwaysBuild(version_target)
    Depends(exe, version_target)
    Depends(wxs, exe)
    Depends(wxs, 'generate_wxs.py')
    Default(msi)
