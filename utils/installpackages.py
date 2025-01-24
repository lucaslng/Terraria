import subprocess
import sys
import importlib.util

'''
Minimum version should be 3.10 but 3.10.12 is the most backward tested version
'''
requiredPythonVersion = (3, 10, 12)

def _checkPythonVersion():
    current_version = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    return current_version >= requiredPythonVersion

def _isPackageInstalled(name: str):
    """Check if a package is installed."""
    return importlib.util.find_spec(name) is not None

if not _checkPythonVersion():
    print(f"Error: Python {'.'.join(map(str, requiredPythonVersion))} or newer is required. "
          f"Current version is {sys.version.split()[0]}")
    sys.exit(1)

_requiredLibraries = {"pygame", "numpy", "pymunk", "dill"}
for package in _requiredLibraries:
    if not _isPackageInstalled(package):
        print(f'{package} is not installed, installing...')
        try:
            #Runs python -m pip install <package>
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                               stdout=subprocess.DEVNULL)
            print(f'Succesfully installed {package}')
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}.")