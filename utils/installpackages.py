import subprocess
import sys
import importlib.util

_required = {'numpy', 'pymunk'}

def isPackageInstalled(name: str):
    """Check if a package is installed."""
    return importlib.util.find_spec(name) is not None

def installPackages():
    for package in _required:
        if not isPackageInstalled(package):
            print(f"{package} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package}: {e}")
        else:
            print(f"{package} is already installed.")