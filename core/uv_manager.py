"""
UV Package Installer Manager for SCP Easy-Install.

Downloads and manages Astral's uv binary for faster package installation.
Falls back to pip seamlessly if uv is unavailable.

Source: https://github.com/astral-sh/uv

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
import stat
from typing import Tuple, Optional, Callable

from qgis.core import QgsMessageLog, Qgis, QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from .scp_config import CACHE_DIR, LOG_TAG


UV_DIR = os.path.join(CACHE_DIR, "uv")
UV_VERSION = "0.6.6"


def _log(message, level=Qgis.Info):
    QgsMessageLog.logMessage(message, LOG_TAG, level=level)


def get_uv_path():
    if sys.platform == "win32":
        return os.path.join(UV_DIR, "uv.exe")
    return os.path.join(UV_DIR, "uv")


def uv_exists():
    return os.path.isfile(get_uv_path())


def _get_uv_platform_info():
    system = sys.platform
    machine = platform.machine().lower()

    if system == "darwin":
        if machine in ("arm64", "aarch64"):
            return ("aarch64-apple-darwin", ".tar.gz")
        return ("x86_64-apple-darwin", ".tar.gz")
    elif system == "win32":
        return ("x86_64-pc-windows-msvc", ".zip")
    else:
        if machine in ("arm64", "aarch64"):
            return ("aarch64-unknown-linux-gnu", ".tar.gz")
        return ("x86_64-unknown-linux-gnu", ".tar.gz")


def _get_uv_download_url():
    triple, ext = _get_uv_platform_info()
    return (
        "https://github.com/astral-sh/uv/releases/download/"
        "{}/uv-{}{}".format(UV_VERSION, triple, ext)
    )


def _safe_extract_tar(tar, dest_dir):
    dest_dir = os.path.realpath(dest_dir)
    use_filter = sys.version_info >= (3, 12)
    for member in tar.getmembers():
        if member.issym() or member.islnk():
            continue
        member_path = os.path.realpath(os.path.join(dest_dir, member.name))
        if not member_path.startswith(dest_dir + os.sep) and member_path != dest_dir:
            raise ValueError("Path traversal in tar: {}".format(member.name))
        if use_filter:
            tar.extract(member, dest_dir, filter='data')
        else:
            tar.extract(member, dest_dir)


def _safe_extract_zip(zip_file, dest_dir):
    dest_dir = os.path.realpath(dest_dir)
    for member in zip_file.namelist():
        member_path = os.path.realpath(os.path.join(dest_dir, member))
        if not member_path.startswith(dest_dir + os.sep) and member_path != dest_dir:
            raise ValueError("Path traversal in zip: {}".format(member))
        zip_file.extract(member, dest_dir)


def _find_file_in_dir(directory, filename):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def download_uv(progress_callback=None, cancel_check=None):
    """Download uv from GitHub releases. Returns (success, message)."""
    if uv_exists():
        _log("uv already exists at {}".format(get_uv_path()))
        return True, "uv already installed"

    url = _get_uv_download_url()
    _log("Downloading uv {} from: {}".format(UV_VERSION, url))

    if progress_callback:
        progress_callback(0, "Downloading uv package installer...")

    if cancel_check and cancel_check():
        return False, "Download cancelled"

    request = QgsBlockingNetworkRequest()
    err = request.get(QNetworkRequest(QUrl(url)))

    if err != QgsBlockingNetworkRequest.NoError:
        error_msg = request.errorMessage()
        _log("uv download failed: {}".format(error_msg), Qgis.Warning)
        return False, "uv download failed: {}".format(error_msg)

    if cancel_check and cancel_check():
        return False, "Download cancelled"

    reply = request.reply()
    content = reply.content()
    content_bytes = content.data()

    if progress_callback:
        size_mb = len(content_bytes) / (1024 * 1024)
        progress_callback(50, "Downloaded uv ({:.1f} MB), extracting...".format(size_mb))

    _, ext = _get_uv_platform_info()
    suffix = ".zip" if ext == ".zip" else ".tar.gz"
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    try:
        with open(temp_path, 'wb') as f:
            f.write(content_bytes)

        if os.path.exists(UV_DIR):
            shutil.rmtree(UV_DIR)
        os.makedirs(UV_DIR, exist_ok=True)

        extract_dir = tempfile.mkdtemp(prefix="uv_extract_")
        try:
            if suffix == ".tar.gz":
                with tarfile.open(temp_path, "r:gz") as tar:
                    _safe_extract_tar(tar, extract_dir)
            else:
                with zipfile.ZipFile(temp_path, "r") as z:
                    _safe_extract_zip(z, extract_dir)

            binary_name = "uv.exe" if sys.platform == "win32" else "uv"
            found = _find_file_in_dir(extract_dir, binary_name)
            if not found:
                return False, "uv binary not found in archive"

            dest = get_uv_path()
            shutil.copy2(found, dest)

            if sys.platform != "win32":
                os.chmod(dest, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        finally:
            shutil.rmtree(extract_dir, ignore_errors=True)

        if progress_callback:
            progress_callback(80, "Verifying uv...")

        if verify_uv():
            _log("uv {} installed successfully".format(UV_VERSION), Qgis.Success)
            if progress_callback:
                progress_callback(100, "uv ready")
            return True, "uv {} installed".format(UV_VERSION)
        else:
            shutil.rmtree(UV_DIR, ignore_errors=True)
            return False, "uv verification failed after download"

    except Exception as e:
        _log("uv installation failed: {}".format(e), Qgis.Warning)
        shutil.rmtree(UV_DIR, ignore_errors=True)
        return False, "uv installation failed: {}".format(str(e)[:200])
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def verify_uv():
    uv_path = get_uv_path()
    if not os.path.isfile(uv_path):
        return False

    try:
        kwargs = {}
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = startupinfo

        result = subprocess.run(
            [uv_path, "--version"],
            capture_output=True, text=True, timeout=15,
            **kwargs,
        )
        if result.returncode == 0:
            version_out = result.stdout.strip()
            _log("uv verified: {}".format(version_out))
            return True
        else:
            _log("uv --version failed: {}".format(
                result.stderr or result.stdout), Qgis.Warning)
    except Exception as e:
        _log("uv verification failed: {}".format(e), Qgis.Warning)

    shutil.rmtree(UV_DIR, ignore_errors=True)
    return False


def remove_uv():
    if not os.path.exists(UV_DIR):
        return True, "uv not installed"
    try:
        shutil.rmtree(UV_DIR)
        _log("Removed uv installation", Qgis.Success)
        return True, "uv removed"
    except Exception as e:
        _log("Failed to remove uv: {}".format(e), Qgis.Warning)
        return False, "Failed to remove uv: {}".format(str(e)[:200])
