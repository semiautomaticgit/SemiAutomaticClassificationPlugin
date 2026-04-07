"""
SCP Easy-Install Configuration.

Configuration constants for the automatic dependency installer.

Easy-Install feature contributed by TerraLab (https://terralab.fr).
"""

import os
import sys

# Cache directory for venv and downloaded tools
CACHE_DIR = os.environ.get("SCP_CACHE_DIR") or os.path.expanduser(
    os.path.join("~", ".scp_dependencies")
)

PYTHON_VERSION = "py{}.{}".format(sys.version_info.major, sys.version_info.minor)
VENV_DIR = os.path.join(CACHE_DIR, "venv_{}".format(PYTHON_VERSION))

# PyTorch CPU wheel index
TORCH_CPU_INDEX = "https://download.pytorch.org/whl/cpu"

# Required packages with version constraints
REQUIRED_PACKAGES = [
    ("remotior-sensus", ">=0.6.2"),
    ("scipy", ">1.0.0"),
    ("matplotlib", ">=3.0.0"),
    ("scikit-learn", ">1.1.0"),
    ("torch", ">=2.0.0"),
    ("torchvision", ">=0.15"),
]

# Map package names to their expected directory in site-packages
# Used for fast filesystem-based checks (no subprocess)
PACKAGE_MARKERS = {
    "remotior-sensus": "remotior_sensus",
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "scikit-learn": "sklearn",
    "torch": "torch",
    "torchvision": "torchvision",
}

# Bump this when install logic changes to force re-install
INSTALL_LOGIC_VERSION = "1"

LOG_TAG = "SCP"
