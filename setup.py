from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mtpl_api/__init__.py
from mtpl_api import __version__ as version

setup(
	name="mtpl_api",
	version=version,
	description="Mtpl Api",
	author="Midocean",
	author_email="midocean@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
