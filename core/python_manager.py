"""
Python Standalone Manager for SCP Easy-Install.

Downloads and manages a standalone Python interpreter that matches
the QGIS Python version, ensuring 100% compatibility.

Source: https://github.com/astral-sh/python-build-standalone

Easy-Install feature contributed by TerraLab (https://terralab.fr).
"""

import os
import sys
import platform
import subprocess
import tarfile
import zipfile
import tempfile
import shutil
from typing import Tuple, Optional, Callable

from qgis.core import QgsMessageLog, Qgis, QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from .scp_config import CACHE_DIR, LOG_TAG


STANDALONE_DIR = os.path.join(CACHE_DIR, "python_standalone")

# Release tag from python-build-standalone
RELEASE_TAG = "20251014"

# Mapping of Python minor versions to their latest patch versions in the release
PYTHON_VERSIONS = {
    (3, 9): "3.9.24",
    (3, 10): "3.10.19",
    (3, 11): "3.11.14",
    (3, 12): "3.12.12",
    (3, 13): "3.13.9",
    (3, 14): "3.14.0",
}


def _log(message, level=Qgis.Info):
    QgsMessageLog.logMessage(message, LOG_TAG, level=level)


def _safe_extract_tar(tar, dest_dir):
    """Safely extract tar archive with path traversal protection."""
    dest_dir = os.path.realpath(dest_dir)
    use_filter = sys.version_info >= (3, 12)
    for member in tar.getmembers():
        if member.issym() or member.islnk():
            continue
        member_path = os.path.realpath(os.path.join(dest_dir, member.name))
        if not member_path.startswith(dest_dir + os.sep) and member_path != dest_dir:
            raise ValueError("Attempted path traversal in tar archive: {}".format(member.name))
        if use_filter:
            tar.extract(member, dest_dir, filter='data')
        else:
            tar.extract(member, dest_dir)


def _safe_extract_zip(zip_file, dest_dir):
    """Safely extract zip archive with path traversal protection."""
    dest_dir = os.path.realpath(dest_dir)
    for member in zip_file.namelist():
        member_path = os.path.realpath(os.path.join(dest_dir, member))
        if not member_path.startswith(dest_dir + os.sep) and member_path != dest_dir:
            raise ValueError("Attempted path traversal in zip archive: {}".format(member))
        zip_file.extract(member, dest_dir)


def _get_windows_antivirus_help(plugin_path):
    return (
        "Installation failed - this may be caused by antivirus software blocking the extraction.\n"
        "Please try:\n"
        "  1. Temporarily disable your antivirus (Windows Defender, etc.)\n"
        "  2. Add an exclusion for the plugin folder\n"
        "  3. Try the installation again\n"
        "Folder to exclude: {}".format(plugin_path)
    )


def get_qgis_python_version():
    return (sys.version_info.major, sys.version_info.minor)


def get_python_full_version():
    version_tuple = get_qgis_python_version()
    if version_tuple in PYTHON_VERSIONS:
        return PYTHON_VERSIONS[version_tuple]
    _log(
        "Python {}.{} not in PYTHON_VERSIONS, falling back to 3.13".format(
            version_tuple[0], version_tuple[1]),
        Qgis.Warning)
    return PYTHON_VERSIONS[(3, 13)]


def _create_python_symlinks(python_dir):
    """Create python3 symlink if only versioned binary exists."""
    bin_dir = os.path.join(python_dir, "bin")
    python3_path = os.path.join(bin_dir, "python3")
    if os.path.exists(python3_path):
        return
    major, minor = get_qgis_python_version()
    versioned = os.path.join(bin_dir, "python{}.{}".format(major, minor))
    if os.path.exists(versioned):
        os.symlink("python{}.{}".format(major, minor), python3_path)
        _log("Created python3 symlink -> python{}.{}".format(major, minor))


def get_standalone_dir():
    return STANDALONE_DIR


def get_standalone_python_path():
    python_dir = os.path.join(STANDALONE_DIR, "python")
    if sys.platform == "win32":
        return os.path.join(python_dir, "python.exe")
    else:
        return os.path.join(python_dir, "bin", "python3")


def standalone_python_exists():
    return os.path.exists(get_standalone_python_path())


def standalone_python_is_current():
    python_path = get_standalone_python_path()
    if not os.path.exists(python_path):
        return False

    try:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        env["PYTHONIOENCODING"] = "utf-8"

        kwargs = {}
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = startupinfo

        result = subprocess.run(
            [python_path, "-c", "import sys; print(sys.version_info.major, sys.version_info.minor)"],
            capture_output=True, text=True, timeout=15, env=env, **kwargs,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) == 2:
                installed = (int(parts[0]), int(parts[1]))
                expected = get_qgis_python_version()
                if installed != expected:
                    _log(
                        "Standalone Python {}.{} doesn't match QGIS {}.{}".format(
                            installed[0], installed[1], expected[0], expected[1]),
                        Qgis.Warning)
                    return False
                return True
    except Exception as e:
        _log("Failed to check standalone Python version: {}".format(e), Qgis.Warning)

    return False


def _get_platform_info():
    system = sys.platform
    machine = platform.machine().lower()

    if system == "darwin":
        if machine in ("arm64", "aarch64"):
            return ("aarch64-apple-darwin", ".tar.gz")
        else:
            return ("x86_64-apple-darwin", ".tar.gz")
    elif system == "win32":
        return ("x86_64-pc-windows-msvc", ".tar.gz")
    else:
        if machine in ("arm64", "aarch64"):
            return ("aarch64-unknown-linux-gnu", ".tar.gz")
        else:
            return ("x86_64-unknown-linux-gnu", ".tar.gz")


def get_download_url():
    python_version = get_python_full_version()
    platform_str, ext = _get_platform_info()
    filename = "cpython-{}+{}-{}-install_only{}".format(
        python_version, RELEASE_TAG, platform_str, ext)
    url = "https://github.com/astral-sh/python-build-standalone/releases/download/{}/{}".format(
        RELEASE_TAG, filename)
    return url


def download_python_standalone(progress_callback=None, cancel_check=None):
    """
    Download and install Python standalone using QGIS network manager.

    Returns (success, message).
    """
    if standalone_python_exists():
        _log("Python standalone already exists", Qgis.Info)
        return True, "Python standalone already installed"

    url = get_download_url()
    python_version = get_python_full_version()

    _log("Downloading Python {} from: {}".format(python_version, url), Qgis.Info)

    if progress_callback:
        progress_callback(0, "Downloading Python {}...".format(python_version))

    fd, temp_path = tempfile.mkstemp(suffix=".tar.gz")
    os.close(fd)

    try:
        if cancel_check and cancel_check():
            return False, "Download cancelled"

        request = QgsBlockingNetworkRequest()
        qurl = QUrl(url)

        if progress_callback:
            progress_callback(5, "Connecting to download server...")

        err = request.get(QNetworkRequest(qurl))

        if err != QgsBlockingNetworkRequest.NoError:
            error_msg = request.errorMessage()
            if "404" in error_msg or "Not Found" in error_msg:
                error_msg = "Python {} not available for this platform. URL: {}".format(
                    python_version, url)
            else:
                error_msg = "Download failed: {}".format(error_msg)
            _log(error_msg, Qgis.Critical)
            return False, error_msg

        if cancel_check and cancel_check():
            return False, "Download cancelled"

        reply = request.reply()
        content = reply.content()

        content_size = len(content)
        if content_size == 0:
            return False, "Download failed: received empty file (0 bytes)"
        min_expected = 10 * 1024 * 1024
        if content_size < min_expected:
            _log("Download suspiciously small: {} bytes".format(content_size), Qgis.Warning)
            return False, (
                "Download failed: file too small ({:.1f} MB). "
                "A firewall or proxy may be blocking the download."
            ).format(content_size / (1024 * 1024))

        if progress_callback:
            total_mb = content_size / (1024 * 1024)
            progress_callback(50, "Downloaded {:.1f} MB, saving...".format(total_mb))

        with open(temp_path, 'wb') as f:
            f.write(content.data())

        _log("Download complete ({} bytes), extracting...".format(content_size), Qgis.Info)

        if progress_callback:
            progress_callback(55, "Extracting Python...")

        if os.path.exists(STANDALONE_DIR):
            shutil.rmtree(STANDALONE_DIR)

        os.makedirs(STANDALONE_DIR, exist_ok=True)

        if temp_path.endswith(".tar.gz") or temp_path.endswith(".tgz"):
            with tarfile.open(temp_path, "r:gz") as tar:
                _safe_extract_tar(tar, STANDALONE_DIR)
        else:
            with zipfile.ZipFile(temp_path, "r") as z:
                _safe_extract_zip(z, STANDALONE_DIR)

        if sys.platform != "win32":
            _create_python_symlinks(os.path.join(STANDALONE_DIR, "python"))

        if progress_callback:
            progress_callback(80, "Verifying Python installation...")

        success, verify_msg = verify_standalone_python()

        if success:
            if progress_callback:
                progress_callback(100, "Python {} installed".format(python_version))
            _log("Python standalone installed successfully", Qgis.Success)
            return True, "Python {} installed successfully".format(python_version)
        else:
            return False, "Verification failed: {}".format(verify_msg)

    except InterruptedError:
        return False, "Download cancelled"
    except Exception as e:
        error_msg = "Installation failed: {}".format(str(e))
        _log(error_msg, Qgis.Critical)

        if sys.platform == "win32":
            error_lower = str(e).lower()
            if "denied" in error_lower or "access" in error_lower or "permission" in error_lower:
                antivirus_help = _get_windows_antivirus_help(STANDALONE_DIR)
                _log(antivirus_help, Qgis.Warning)
                error_msg = "{}\n\n{}".format(error_msg, antivirus_help)

        return False, error_msg
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def verify_standalone_python():
    python_path = get_standalone_python_path()

    if not os.path.exists(python_path):
        return False, "Python executable not found at {}".format(python_path)

    if sys.platform != "win32":
        try:
            import stat
            os.chmod(python_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        except OSError:
            pass

    try:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        env["PYTHONIOENCODING"] = "utf-8"

        kwargs = {}
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = startupinfo

        result = subprocess.run(
            [python_path, "-c", "import sys; print(sys.version)"],
            capture_output=True, text=True, timeout=30, env=env, **kwargs,
        )

        if result.returncode == 0:
            version_output = result.stdout.strip().split()[0]
            if not version_output.startswith("{}.{}".format(
                    sys.version_info.major, sys.version_info.minor)):
                expected = get_python_full_version()
                _log("Python version mismatch: got {}, expected {}".format(
                    version_output, expected), Qgis.Warning)
                return False, "Version mismatch: downloaded {}, expected {}".format(
                    version_output, expected)

            _log("Verified Python standalone: {}".format(version_output), Qgis.Success)
            return True, "Python {} verified".format(version_output)
        else:
            error = result.stderr or "Unknown error"
            _log("Python verification failed: {}".format(error), Qgis.Warning)
            return False, "Verification failed: {}".format(error[:100])

    except subprocess.TimeoutExpired:
        return False, "Python verification timed out"
    except Exception as e:
        return False, "Verification error: {}".format(str(e)[:100])


def remove_standalone_python():
    if not os.path.exists(STANDALONE_DIR):
        return True, "Standalone Python not installed"

    try:
        shutil.rmtree(STANDALONE_DIR)
        _log("Removed standalone Python installation", Qgis.Success)
        return True, "Standalone Python removed"
    except Exception as e:
        error_msg = "Failed to remove: {}".format(str(e))
        _log(error_msg, Qgis.Warning)
        return False, error_msg
