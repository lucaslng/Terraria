import subprocess
import sys
import importlib.util

# Define minimum required Python version as a tuple for easy comparison
MIN_PYTHON_VERSION = (3, 10, 12)

def _checkPythonVersion():
    current_version = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    return current_version >= MIN_PYTHON_VERSION

def _isPackageInstalled(name: str):
    """Check if a package is installed."""
    return importlib.util.find_spec(name) is not None

#check python version
if not _checkPythonVersion():
    print(f"Error: Python {'.'.join(map(str, MIN_PYTHON_VERSION))} or newer is required. "
          f"Current version is {sys.version.split()[0]}")
    sys.exit(1)

#required packages
_required = {'numpy', 'pymunk'}
for package in _required:
    if not _isPackageInstalled(package):
        try:
            #runs python -m pip install <package>
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                               stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}.")