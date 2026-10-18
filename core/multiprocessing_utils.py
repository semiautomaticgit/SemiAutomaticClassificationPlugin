# This file is part of SemiAutomaticClassificationPlugin.
# SemiAutomaticClassificationPlugin is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

"""Helpers for running Python multiprocessing from an embedded QGIS."""

import os
import sys
from os import path


def _is_executable_file(candidate):
    return (
        candidate is not None
        and path.isfile(candidate)
        and os.access(candidate, os.X_OK)
    )


def python_multiprocessing_executable():
    """Return a Python launcher suitable for multiprocessing children.

    In an embedded QGIS session ``sys.executable`` can be the QGIS GUI binary,
    not Python. Using it with the ``spawn`` start method launches another QGIS
    instance for every child process. The macOS application bundle ships a
    ``Contents/MacOS/python`` wrapper which also sets the relocatable
    ``PYTHONHOME`` required by QGIS' bundled Python.
    """
    executable = path.abspath(sys.executable)
    executable_name = path.basename(executable).lower()

    if (
            executable_name.startswith('python')
            and _is_executable_file(executable)):
        return executable

    candidates = []
    if sys.platform.startswith('win'):
        candidates.extend([
            path.join(sys.exec_prefix, 'pythonw.exe'),
            path.join(sys.exec_prefix, '../../bin/pythonw.exe')
        ])
    elif sys.platform.startswith('darwin'):
        candidates.extend([
            # Current QGIS macOS bundle layout (QGIS 4 and recent QGIS 3).
            path.join(path.dirname(executable), 'python'),
            path.join(sys.exec_prefix, '../MacOS/python'),
            path.join(sys.prefix, '../MacOS/python'),
            # Older/custom bundle layouts.
            path.join(sys.exec_prefix, 'bin/python3'),
            path.join(sys.exec_prefix, '../Resources/bin/python3')
        ])
    else:
        return None

    checked = set()
    for candidate in candidates:
        candidate = path.abspath(candidate)
        if candidate not in checked and _is_executable_file(candidate):
            return candidate
        checked.add(candidate)
    return None


def configure_multiprocessing_executable(multiprocess_module):
    """Configure and return the child-process Python executable, if found."""
    python_path = python_multiprocessing_executable()
    if python_path is not None:
        multiprocess_module.set_executable(python_path)
    return python_path
