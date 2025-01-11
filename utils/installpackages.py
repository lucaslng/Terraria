import subprocess
import sys

_required  = {'numpy','pymunk'}

def installPackages():
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', *_required])