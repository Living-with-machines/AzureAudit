import io
import os

from setuptools import find_packages, setup

# Package meta-data.
AUTHOR = "Sarah Gibson"
DESCRIPTION = "A Python package for auditing Azure Storage Accounts"
EMAIL = "sgibson@turing.ac.uk"
LICENSE = "MIT"
LICENSE_TROVE = "License :: OSI Approved :: MIT License"
NAME = "az_audit"
REQUIRES_PYTHON = ">=3.7"
URL = "https://github.com/Living-with-Machines/AzureAudit"
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = []

# When these are changed, update clevercsv/_optional.py accordingly
full_require = []

docs_require = []
test_require = full_require + [
    "coverage",
    "freezegun",
    "pytest",
]
dev_require = []

# What packages are optional?
EXTRAS = {
    "full": full_require,
    "docs": docs_require,
    "tests": test_require,
    "dev": docs_require + test_require + dev_require,
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license=LICENSE,
    ext_modules=[],
    entry_points={"console_scripts": ["az-audit = az_audit.cli:main"]},
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        LICENSE_TROVE,
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
