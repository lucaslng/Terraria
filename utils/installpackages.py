import subprocess
import sys
import importlib.util

_required = {'numpy', 'pymunk'}

def _isPackageInstalled(name: str):
    """Check if a package is installed."""
    return importlib.util.find_spec(name) is not None


for package in _required:
		if not _isPackageInstalled(package):
				# print(f"{package} not found. Installing...")
				try:
						# runs python -m pip install <package>
						subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], stdout=subprocess.DEVNULL)
						# print(f"Succesfully installed {package}.")
				except subprocess.CalledProcessError as e:
						print(f"Failed to install {package}: {e}.")
		# else:
		# 		print(f"{package} is already installed.")