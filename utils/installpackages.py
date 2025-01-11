import pip

_required  = {'numpy','pymunk'}

def installPackages():
	'''Somewhat sketchy way to install packages'''
	pip.main(['install', *_required])

# def installPackages():
# 	subprocess.check_call([sys.executable, '-m', 'pip', 'install', *_required])
