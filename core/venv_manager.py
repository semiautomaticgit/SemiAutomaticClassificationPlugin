"""
Virtual Environment Manager for SCP Easy-Install.

Manages venv creation, dependency installation, and verification
for the SemiAutomaticClassificationPlugin.

All CUDA/GPU logic removed - torch is always CPU-only.

Easy-Install feature contributed by TerraLab (https://terralab.fr).
"""

import subprocess
import sys
import os
import shutil
import platform
import tempfile
import time
import re
import hashlib
import traceback
from typing import Tuple, Optional, Callable, List

from qgis.core import QgsMessageLog, Qgis

from .scp_config import (
    CACHE_DIR, VENV_DIR, REQUIRED_PACKAGES, PACKAGE_MARKERS,
    TORCH_CPU_INDEX, INSTALL_LOGIC_VERSION, LOG_TAG,
)
from .uv_manager import (
    uv_exists, get_uv_path, download_uv, verify_uv, remove_uv,
)


# Module-level uv state (set during create_venv_and_install)
_uv_available = False
_uv_path = None  # type: Optional[str]

PYTHON_VERSION = "py{}.{}".format(sys.version_info.major, sys.version_info.minor)
DEPS_HASH_FILE = os.path.join(VENV_DIR, "deps_hash.txt")


def _compute_deps_hash():
    data = repr(REQUIRED_PACKAGES).encode("utf-8")
    data += INSTALL_LOGIC_VERSION.encode("utf-8")
    return hashlib.md5(data, usedforsecurity=False).hexdigest()


def _read_deps_hash():
    try:
        with open(DEPS_HASH_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (OSError, IOError):
        return None


def _write_deps_hash():
    try:
        os.makedirs(os.path.dirname(DEPS_HASH_FILE), exist_ok=True)
        with open(DEPS_HASH_FILE, "w", encoding="utf-8") as f:
            f.write(_compute_deps_hash())
    except (OSError, IOError) as e:
        _log("Failed to write deps hash: {}".format(e), Qgis.Warning)


def _log(message, level=Qgis.Info):
    QgsMessageLog.logMessage(message, LOG_TAG, level=level)


def _log_system_info():
    try:
        qgis_version = Qgis.QGIS_VERSION
    except Exception:
        qgis_version = "Unknown"

    custom_cache = os.environ.get("SCP_CACHE_DIR")
    info_lines = [
        "=" * 50,
        "SCP Installation Environment:",
        "  OS: {} ({} {})".format(sys.platform, platform.system(), platform.release()),
        "  Architecture: {}".format(platform.machine()),
        "  Python: {}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
        "  QGIS: {}".format(qgis_version),
        "  Install dir: {}".format(CACHE_DIR),
    ]
    if custom_cache:
        info_lines.append("  (via SCP_CACHE_DIR)")
    info_lines.append("=" * 50)
    for line in info_lines:
        _log(line, Qgis.Info)


# --- SSL / Network error detection ---

_SSL_ERROR_PATTERNS = [
    "ssl", "certificate verify failed", "CERTIFICATE_VERIFY_FAILED",
    "SSLError", "SSLCertVerificationError", "tlsv1 alert",
    "unable to get local issuer certificate",
    "self signed certificate in certificate chain",
]


def _is_ssl_error(stderr):
    stderr_lower = stderr.lower()
    return any(pattern.lower() in stderr_lower for pattern in _SSL_ERROR_PATTERNS)


def _is_hash_mismatch(output):
    output_lower = output.lower()
    return "do not match the hashes" in output_lower or "hash mismatch" in output_lower


def _get_pip_ssl_flags():
    return [
        "--trusted-host", "pypi.org",
        "--trusted-host", "pypi.python.org",
        "--trusted-host", "files.pythonhosted.org",
        "--trusted-host", "download.pytorch.org",
    ]


def _get_uv_ssl_flags():
    """Return SSL bypass flags in uv format (--allow-insecure-host)."""
    return [
        "--allow-insecure-host", "pypi.org",
        "--allow-insecure-host", "pypi.python.org",
        "--allow-insecure-host", "files.pythonhosted.org",
        "--allow-insecure-host", "download.pytorch.org",
    ]


def _is_ssl_module_missing(error_text):
    lower = error_text.lower()
    patterns = ["ssl module is not available", "no module named '_ssl'",
                "ssl module", "importerror: _ssl"]
    return any(p in lower for p in patterns)


def _get_ssl_error_help(error_text=""):
    if _is_ssl_module_missing(error_text):
        return (
            "Installation failed: Python's SSL module is not available.\n\n"
            "This usually means the Python installation is incomplete or corrupted.\n"
            "Please try:\n"
            "  1. Delete the folder: {}\n"
            "  2. Restart QGIS and try again\n"
            "  3. If the issue persists, reinstall QGIS".format(CACHE_DIR)
        )
    return (
        "Installation failed due to network restrictions.\n\n"
        "Please contact your IT department to allow access to:\n"
        "  - pypi.org\n"
        "  - files.pythonhosted.org\n"
        "  - download.pytorch.org\n\n"
        "You can also try checking your proxy settings in QGIS "
        "(Settings > Options > Network)."
    )


_NETWORK_ERROR_PATTERNS = [
    "connectionreseterror", "connection aborted",
    "connection was forcibly closed", "remotedisconnected",
    "connectionerror", "newconnectionerror", "maxretryerror",
    "protocolerror", "readtimeouterror", "connecttimeouterror",
    "urlib3.exceptions", "requests.exceptions.connectionerror",
    "network is unreachable", "temporary failure in name resolution",
    "name or service not known",
]


def _is_network_error(output):
    output_lower = output.lower()
    if _is_ssl_error(output):
        return False
    return any(p in output_lower for p in _NETWORK_ERROR_PATTERNS)


def _is_proxy_auth_error(output):
    output_lower = output.lower()
    patterns = ["407 proxy authentication", "proxy authentication required", "proxyerror"]
    return any(p in output_lower for p in patterns)


def _is_unable_to_create_process(output):
    return "unable to create process" in output.lower()


def _is_dll_init_error(output):
    lower = output.lower()
    patterns = ["winerror 1114", "dll initialization routine failed",
                "dll load failed", "_load_dll_libraries"]
    return any(p in lower for p in patterns)


def _get_vcpp_help():
    return (
        "A required DLL failed to initialize. This is usually caused by "
        "missing Visual C++ Redistributables.\n\n"
        "Please install the latest VC++ Redistributable:\n"
        "  https://aka.ms/vs/17/release/vc_redist.x64.exe\n\n"
        "Then restart your computer and try again."
    )


def _is_antivirus_error(stderr):
    stderr_lower = stderr.lower()
    patterns = [
        "access is denied", "winerror 5", "winerror 225",
        "permission denied",
        "operation did not complete successfully because the file contains a virus",
        "blocked by your administrator", "blocked by group policy",
        "application control policy", "applocker",
        "blocked by your organization",
    ]
    return any(p in stderr_lower for p in patterns)


def _get_pip_antivirus_help(venv_dir):
    steps = (
        "Installation was blocked, likely by antivirus software "
        "or security policy.\n\n"
        "Please try:\n"
        "  1. Temporarily disable real-time antivirus scanning\n"
        "  2. Add an exclusion for the plugin folder:\n"
        "     {}\n".format(venv_dir)
    )
    if sys.platform == "win32":
        steps += (
            "  3. Run QGIS as administrator "
            "(right-click > Run as administrator)\n"
            "  4. Try the installation again"
        )
    else:
        steps += (
            "  3. Check folder permissions: "
            "chmod -R u+rwX \"{}\"\n"
            "  4. Try the installation again".format(venv_dir)
        )
    return steps


_WINDOWS_CRASH_CODES = {
    3221225477, -1073741819,  # ACCESS_VIOLATION
    3221225725, -1073741571,  # STACK_OVERFLOW
    3221225781, -1073741515,  # DLL_NOT_FOUND
}


def _is_windows_process_crash(returncode):
    if sys.platform != "win32":
        return False
    return returncode in _WINDOWS_CRASH_CODES


def _get_crash_help(venv_dir):
    return (
        "The installer process crashed unexpectedly (access violation).\n\n"
        "This is usually caused by:\n"
        "  - Antivirus software (Windows Defender, etc.) blocking pip\n"
        "  - Corrupted virtual environment\n\n"
        "Please try:\n"
        "  1. Temporarily disable real-time antivirus scanning\n"
        "  2. Add an exclusion for the plugin folder:\n"
        "     {}\n"
        "  3. Delete the folder and restart QGIS to recreate the environment\n"
        "  4. If the issue persists, run QGIS as administrator"
    ).format(venv_dir)


# --- Venv path helpers ---

def get_venv_dir():
    return VENV_DIR


def get_venv_site_packages(venv_dir=None):
    if venv_dir is None:
        venv_dir = VENV_DIR

    if sys.platform == "win32":
        return os.path.join(venv_dir, "Lib", "site-packages")
    else:
        lib_dir = os.path.join(venv_dir, "lib")
        if os.path.exists(lib_dir):
            for entry in os.listdir(lib_dir):
                if entry.startswith("python") and os.path.isdir(os.path.join(lib_dir, entry)):
                    site_packages = os.path.join(lib_dir, entry, "site-packages")
                    if os.path.exists(site_packages):
                        return site_packages

        py_version = "python{}.{}".format(sys.version_info.major, sys.version_info.minor)
        return os.path.join(venv_dir, "lib", py_version, "site-packages")


def _add_windows_dll_directories(site_packages):
    """Register torch/torchvision DLL directories on Windows.

    Without this, importing torch from a foreign venv inside QGIS fails
    with 'DLL load failed' (WinError 126/127).
    """
    dll_dirs = [
        os.path.join(site_packages, "torch", "lib"),
        os.path.join(site_packages, "torch", "bin"),
        os.path.join(site_packages, "torchvision"),
    ]
    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    for dll_dir in dll_dirs:
        if os.path.isdir(dll_dir):
            try:
                os.add_dll_directory(dll_dir)
            except OSError as exc:
                _log("add_dll_directory({}) failed: {}".format(dll_dir, exc), Qgis.Warning)
            if dll_dir not in path_parts:
                path_parts.insert(0, dll_dir)
    os.environ["PATH"] = os.pathsep.join(path_parts)


def ensure_venv_packages_available():
    """Add venv site-packages to sys.path and handle DLL loading."""
    if not venv_exists():
        _log("Venv does not exist, cannot load packages", Qgis.Warning)
        return False

    site_packages = get_venv_site_packages()
    if not os.path.exists(site_packages):
        _log("Venv site-packages not found: {}".format(site_packages), Qgis.Warning)
        return False

    if site_packages not in sys.path:
        sys.path.insert(0, site_packages)
        _log("Added venv site-packages to sys.path: {}".format(site_packages), Qgis.Info)

    # Ensure child processes (multiprocessing spawn) can find venv packages
    existing = os.environ.get("PYTHONPATH", "")
    if site_packages not in existing:
        os.environ["PYTHONPATH"] = site_packages + (os.pathsep + existing if existing else "")

    # On Windows, register DLL directories for torch/torchvision
    if sys.platform == "win32":
        _add_windows_dll_directories(site_packages)

    # SAFE FIX for old QGIS with stale typing_extensions (missing TypeIs)
    if "typing_extensions" in sys.modules:
        try:
            te = sys.modules["typing_extensions"]
            if not hasattr(te, "TypeIs"):
                old_ver = getattr(te, "__version__", "unknown")
                del sys.modules["typing_extensions"]
                import typing_extensions as new_te
                _log(
                    "Reloaded typing_extensions {} -> {} from venv".format(
                        old_ver, new_te.__version__),
                    Qgis.Info
                )
        except Exception:
            _log("Failed to reload typing_extensions, torch may fail", Qgis.Warning)

    # Handle numpy version conflicts with QGIS bundled version.
    # Only fix if numpy is ALREADY loaded with an old version (<1.22.4).
    # If numpy isn't loaded yet, venv site-packages is already first in
    # sys.path so it will naturally pick up the venv version.
    needs_numpy_fix = False
    old_version = "unknown"
    try:
        if "numpy" in sys.modules:
            old_np = sys.modules["numpy"]
            old_version = getattr(old_np, "__version__", "0.0.0")
            parts = old_version.split(".")[:3]
            vn = [int(x) for x in parts] + [0] * (3 - len(parts))
            np_old = (vn[0] < 1) or (vn[0] == 1 and vn[1] < 22)
            np_old = np_old or (vn[0] == 1 and vn[1] == 22 and vn[2] < 4)
            needs_numpy_fix = np_old
    except Exception:
        needs_numpy_fix = False

    if not needs_numpy_fix:
        return True

    qgis_ver = Qgis.QGIS_VERSION.split("-")[0]
    _log(
        "QGIS {} with old numpy {} detected. Forcing venv numpy...".format(
            qgis_ver, old_version),
        Qgis.Info)

    removed_paths = []
    try:
        import importlib

        mods_to_clear = [
            k for k in list(sys.modules.keys())
            if k.startswith("numpy")
        ]
        for mod in mods_to_clear:
            del sys.modules[mod]

        for p in sys.path[:]:
            if p == site_packages:
                continue
            np_init = os.path.join(p, "numpy", "__init__.py")
            if os.path.exists(np_init):
                removed_paths.append(p)
                sys.path.remove(p)

        importlib.invalidate_caches()

        import numpy as new_numpy  # noqa: E402

        for p in removed_paths:
            if p not in sys.path:
                sys.path.append(p)
        removed_paths = []

        new_ver = new_numpy.__version__
        if new_ver == old_version and old_version != "not_loaded":
            _log(
                "WARNING: numpy reload did not change version (still {})".format(old_version),
                Qgis.Warning)
        else:
            _log("Reloaded numpy {} -> {} from venv".format(old_version, new_ver), Qgis.Info)

    except Exception as e:
        _log("Failed to reload numpy: {}".format(e), Qgis.Warning)

    finally:
        for p in removed_paths:
            if p not in sys.path:
                sys.path.append(p)

    return True


# --- Venv Python/pip paths ---

def get_venv_python_path(venv_dir=None):
    if venv_dir is None:
        venv_dir = VENV_DIR
    if sys.platform == "win32":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python3")


def get_venv_pip_path(venv_dir=None):
    if venv_dir is None:
        venv_dir = VENV_DIR
    if sys.platform == "win32":
        return os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_dir, "bin", "pip")


def _get_qgis_python():
    """Get path to QGIS's bundled Python on Windows (fallback)."""
    if sys.platform != "win32":
        return None

    python_path = os.path.join(sys.prefix, "python.exe")
    if not os.path.exists(python_path):
        python_path = os.path.join(sys.prefix, "python3.exe")

    if not os.path.exists(python_path):
        _log("QGIS bundled Python not found at sys.prefix", Qgis.Warning)
        return None

    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(
            [python_path, "-c", "import sys; print(sys.version)"],
            capture_output=True, text=True, timeout=15,
            env=env, startupinfo=startupinfo,
        )
        if result.returncode == 0:
            _log("QGIS Python verified: {}".format(result.stdout.strip()), Qgis.Info)
            return python_path
        else:
            _log("QGIS Python failed verification: {}".format(result.stderr), Qgis.Warning)
            return None
    except Exception as e:
        _log("QGIS Python verification error: {}".format(e), Qgis.Warning)
        return None


def _get_system_python():
    """Get the Python executable for creating venvs."""
    from .python_manager import standalone_python_exists, get_standalone_python_path

    if standalone_python_exists():
        python_path = get_standalone_python_path()
        _log("Using standalone Python: {}".format(python_path), Qgis.Info)
        return python_path

    if sys.platform == "win32":
        qgis_python = _get_qgis_python()
        if qgis_python:
            _log("Standalone Python unavailable, using QGIS Python as fallback", Qgis.Warning)
            return qgis_python

    raise RuntimeError(
        "Python standalone not installed. "
        "Please restart QGIS to trigger the dependency installer."
    )


def venv_exists(venv_dir=None):
    if venv_dir is None:
        venv_dir = VENV_DIR
    return os.path.exists(get_venv_python_path(venv_dir))


def _cleanup_partial_venv(venv_dir):
    if os.path.exists(venv_dir):
        try:
            shutil.rmtree(venv_dir, ignore_errors=True)
            _log("Cleaned up partial venv: {}".format(venv_dir), Qgis.Info)
        except Exception:
            _log("Could not clean up partial venv: {}".format(venv_dir), Qgis.Warning)


# --- Venv creation ---

def create_venv(venv_dir=None, progress_callback=None):
    if venv_dir is None:
        venv_dir = VENV_DIR

    _log("Creating virtual environment at: {}".format(venv_dir), Qgis.Info)

    if progress_callback:
        progress_callback(10, "Creating virtual environment...")

    system_python = _get_system_python()
    _log("Using Python: {}".format(system_python), Qgis.Info)

    env = _get_clean_env_for_venv()

    global _uv_available, _uv_path

    # Try uv venv creation first (faster)
    if _uv_available and _uv_path:
        _log("Creating venv with uv...", Qgis.Info)
        uv_cmd = [_uv_path, "venv", "--python", system_python, venv_dir]
        try:
            subprocess_kwargs = _get_subprocess_kwargs()
            result = subprocess.run(
                uv_cmd,
                capture_output=True, text=True, timeout=120,
                env=env, **subprocess_kwargs,
            )
            if result.returncode == 0:
                _log("Virtual environment created with uv", Qgis.Success)
                if progress_callback:
                    progress_callback(20, "Virtual environment created (uv)")
                return True, "Virtual environment created"
            else:
                error_msg = result.stderr or result.stdout or ""
                _log("uv venv creation failed: {}".format(error_msg[:200]), Qgis.Warning)
                _cleanup_partial_venv(venv_dir)
                remove_uv()
                _uv_available = False
                _uv_path = None
                _log("Falling back to python -m venv", Qgis.Warning)
        except Exception as e:
            _log("uv venv exception: {}\n{}".format(e, traceback.format_exc()), Qgis.Warning)
            _cleanup_partial_venv(venv_dir)
            remove_uv()
            _uv_available = False
            _uv_path = None

    # Standard venv creation
    cmd = [system_python, "-m", "venv", venv_dir]
    _log("Running: {}".format(" ".join(cmd)), Qgis.Info)
    try:
        subprocess_kwargs = _get_subprocess_kwargs()
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300,
            env=env, **subprocess_kwargs,
        )

        if result.returncode == 0:
            _log("Virtual environment created successfully", Qgis.Success)

            # Ensure pip is available
            pip_path = get_venv_pip_path(venv_dir)
            if not os.path.exists(pip_path):
                _log("pip not found in venv, bootstrapping with ensurepip...", Qgis.Info)
                python_in_venv = get_venv_python_path(venv_dir)
                ensurepip_cmd = [python_in_venv, "-m", "ensurepip", "--upgrade"]
                try:
                    ensurepip_result = subprocess.run(
                        ensurepip_cmd,
                        capture_output=True, text=True, timeout=120,
                        env=env, **subprocess_kwargs,
                    )
                    if ensurepip_result.returncode == 0:
                        _log("pip bootstrapped via ensurepip", Qgis.Success)
                    else:
                        err = ensurepip_result.stderr or ensurepip_result.stdout
                        _log("ensurepip failed: {}".format(err[:200]), Qgis.Warning)
                        _cleanup_partial_venv(venv_dir)
                        return False, "Failed to bootstrap pip: {}".format(err[:200])
                except Exception as e:
                    _log("ensurepip exception: {}\n{}".format(
                        e, traceback.format_exc()), Qgis.Warning)
                    _cleanup_partial_venv(venv_dir)
                    return False, "Failed to bootstrap pip: {}".format(str(e)[:200])

            if progress_callback:
                progress_callback(20, "Virtual environment created")
            return True, "Virtual environment created"
        else:
            error_msg = result.stderr or result.stdout or "Return code {}".format(result.returncode)
            _log("Failed to create venv: {}".format(error_msg), Qgis.Critical)
            _cleanup_partial_venv(venv_dir)
            return False, "Failed to create venv: {}".format(error_msg[:200])

    except subprocess.TimeoutExpired:
        _log("Venv creation timed out, retrying with --without-pip...", Qgis.Warning)
        _cleanup_partial_venv(venv_dir)
        try:
            nopip_cmd = [system_python, "-m", "venv", "--without-pip", venv_dir]
            result2 = subprocess.run(
                nopip_cmd, capture_output=True, text=True, timeout=300,
                env=env, **subprocess_kwargs,
            )
            if result2.returncode == 0:
                _log("Venv created (--without-pip), bootstrapping pip...", Qgis.Info)
                python_in_venv = get_venv_python_path(venv_dir)
                ensurepip_cmd = [python_in_venv, "-m", "ensurepip", "--upgrade"]
                ep_result = subprocess.run(
                    ensurepip_cmd,
                    capture_output=True, text=True, timeout=120,
                    env=env, **subprocess_kwargs,
                )
                if ep_result.returncode == 0:
                    _log("pip bootstrapped via ensurepip", Qgis.Success)
                    if progress_callback:
                        progress_callback(20, "Virtual environment created")
                    return True, "Virtual environment created"
                else:
                    err = ep_result.stderr or ep_result.stdout or ""
                    _cleanup_partial_venv(venv_dir)
                    return False, "Failed to bootstrap pip: {}".format(err[:200])
            else:
                err = result2.stderr or result2.stdout or ""
                _cleanup_partial_venv(venv_dir)
                return False, "Virtual environment creation timed out"
        except Exception as e2:
            _log("Retry venv creation failed: {}\n{}".format(
                e2, traceback.format_exc()), Qgis.Critical)
            _cleanup_partial_venv(venv_dir)
            return False, "Virtual environment creation timed out"
    except FileNotFoundError:
        _log("Python executable not found: {}".format(system_python), Qgis.Critical)
        return False, "Python not found: {}".format(system_python)
    except Exception as e:
        _log("Exception during venv creation: {}\n{}".format(
            str(e), traceback.format_exc()), Qgis.Critical)
        _cleanup_partial_venv(venv_dir)
        return False, "Error: {}".format(str(e)[:200])


# --- Install command builders ---

def _build_install_cmd(python_path, pip_args):
    """Build install command using uv (if available) or pip."""
    if _uv_available and _uv_path:
        cmd = [_uv_path, "pip"]
        skip_next = False
        for i, arg in enumerate(pip_args):
            if skip_next:
                skip_next = False
                continue
            if arg == "--disable-pip-version-check":
                continue
            elif arg == "--no-warn-script-location":
                continue
            elif arg == "--prefer-binary":
                continue
            elif arg == "--no-cache-dir":
                cmd.append("--no-cache")
                continue
            elif arg == "--force-reinstall":
                cmd.append("--reinstall")
                continue
            elif arg == "--trusted-host":
                cmd.append("--allow-insecure-host")
                continue
            elif arg == "--proxy":
                skip_next = True
                continue
            cmd.append(arg)
        cmd.extend(["--python", python_path])
        return cmd
    return [python_path, "-m", "pip"] + pip_args


# --- Pip install with progress ---

class _PipResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _parse_pip_download_line(line):
    m = re.search(r"Downloading\s+(\S+)\s+\(([^)]+)\)", line)
    if not m:
        return None
    raw_name = m.group(1)
    size = m.group(2)
    if "/" in raw_name:
        raw_name = raw_name.rsplit("/", 1)[-1]
    name_match = re.match(r"([A-Za-z][A-Za-z0-9_]*)", raw_name)
    pkg_name = name_match.group(1) if name_match else raw_name

    size_match = re.match(r"([\d.]+)\s*(kB|MB|GB)", size)
    if size_match:
        num = float(size_match.group(1))
        unit = size_match.group(2)
        if unit == "MB" and num >= 1000:
            size = "{:.1f} GB".format(num / 1000)

    return "Downloading {} ({})".format(pkg_name, size)


def _run_pip_install(
    cmd, timeout, env, subprocess_kwargs,
    package_name, package_index, total_packages,
    progress_start, progress_end,
    progress_callback=None, cancel_check=None,
):
    """Run a pip install command with real-time progress updates."""
    poll_interval = 2

    stdout_fd, stdout_path = tempfile.mkstemp(suffix="_stdout.txt", prefix="pip_")
    stderr_fd, stderr_path = tempfile.mkstemp(suffix="_stderr.txt", prefix="pip_")

    try:
        stdout_file = os.fdopen(stdout_fd, "w", encoding="utf-8")
        stderr_file = os.fdopen(stderr_fd, "w", encoding="utf-8")
    except Exception:
        try:
            os.close(stdout_fd)
        except Exception:
            pass
        try:
            os.close(stderr_fd)
        except Exception:
            pass
        raise

    process = None
    try:
        _log("Running: {}".format(" ".join(cmd)), Qgis.Info)
        process = subprocess.Popen(
            cmd, stdout=stdout_file, stderr=stderr_file,
            text=True, env=env, **subprocess_kwargs,
        )

        start_time = time.monotonic()
        last_download_status = ""

        while True:
            try:
                process.wait(timeout=poll_interval)
                break
            except subprocess.TimeoutExpired:
                pass

            elapsed = int(time.monotonic() - start_time)

            if cancel_check and cancel_check():
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                return _PipResult(-1, "", "Installation cancelled")

            if elapsed >= timeout:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                raise subprocess.TimeoutExpired(cmd, timeout)

            try:
                with open(stdout_path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(0, 2)
                    file_size = f.tell()
                    read_from = max(0, file_size - 4096)
                    f.seek(read_from)
                    tail = f.read()
                    lines = tail.strip().split("\n")
                    for line in reversed(lines):
                        parsed = _parse_pip_download_line(line)
                        if parsed:
                            last_download_status = parsed
                            break
            except Exception:
                pass

            if elapsed >= 60:
                elapsed_str = "{}m {}s".format(elapsed // 60, elapsed % 60)
            else:
                elapsed_str = "{}s".format(elapsed)

            if last_download_status:
                msg = "{}... {}".format(last_download_status, elapsed_str)
            elif package_name == "torch":
                msg = "Downloading PyTorch CPU (~300 MB)... {}".format(elapsed_str)
            else:
                msg = "Installing {}... {}".format(package_name, elapsed_str)

            progress_range = progress_end - progress_start
            if timeout > 0:
                fraction = min(elapsed / timeout, 0.9)
            else:
                fraction = 0
            interpolated = progress_start + int(progress_range * fraction)
            interpolated = min(interpolated, progress_end - 1)

            if progress_callback:
                progress_callback(interpolated, msg)

        stdout_file.close()
        stderr_file.close()
        stdout_file = None
        stderr_file = None

        try:
            with open(stdout_path, "r", encoding="utf-8", errors="replace") as f:
                full_stdout = f.read()
        except Exception:
            full_stdout = ""

        try:
            with open(stderr_path, "r", encoding="utf-8", errors="replace") as f:
                full_stderr = f.read()
        except Exception:
            full_stderr = ""

        if process.returncode != 0:
            _log("Command failed (rc={})\nstdout: {}\nstderr: {}".format(
                process.returncode, full_stdout[-1000:], full_stderr[-1000:]),
                Qgis.Warning)

        return _PipResult(process.returncode, full_stdout, full_stderr)

    except subprocess.TimeoutExpired:
        raise
    except Exception:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except Exception:
                process.kill()
        raise
    finally:
        if stdout_file is not None:
            try:
                stdout_file.close()
            except Exception:
                pass
        if stderr_file is not None:
            try:
                stderr_file.close()
            except Exception:
                pass
        try:
            os.unlink(stdout_path)
        except Exception:
            pass
        try:
            os.unlink(stderr_path)
        except Exception:
            pass


# --- Batch uv install (2 commands instead of 6) ---

def _try_batch_uv_install(venv_dir, progress_callback=None, cancel_check=None):
    """Install all packages in 2 uv batch commands instead of 6 per-package.

    Batch 1: PyPI packages (remotior-sensus, scipy, matplotlib, scikit-learn)
    Batch 2: torch packages with CPU index (torch, torchvision)

    Returns (True, msg) on success, (False, msg) on failure.
    Caller should fallback to per-package install on failure.
    """
    if not _uv_available or not _uv_path:
        return False, "uv not available"

    python_path = get_venv_python_path(venv_dir)
    env = _get_clean_env_for_venv()
    subprocess_kwargs = _get_subprocess_kwargs()

    # Split packages into PyPI batch and torch batch
    pypi_specs = []
    torch_specs = []
    for name, version_spec in REQUIRED_PACKAGES:
        spec = "{}{}".format(name, version_spec)
        if name in ("torch", "torchvision"):
            torch_specs.append(spec)
        else:
            pypi_specs.append(spec)

    # --- Batch 1: PyPI packages ---
    if pypi_specs:
        if cancel_check and cancel_check():
            return False, "Installation cancelled"

        if progress_callback:
            progress_callback(25, "Batch installing PyPI packages...")

        _log("Batch uv install (PyPI): {}".format(", ".join(pypi_specs)), Qgis.Info)

        cmd = [_uv_path, "pip", "install", "--upgrade"]
        cmd.extend(_get_uv_ssl_flags())
        cmd.extend(pypi_specs)
        cmd.extend(["--python", python_path])

        try:
            result = _run_pip_install(
                cmd=cmd, timeout=1200,
                env=env, subprocess_kwargs=subprocess_kwargs,
                package_name="PyPI packages", package_index=0,
                total_packages=2,
                progress_start=20, progress_end=55,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
            if result.returncode != 0:
                error = result.stderr or result.stdout or ""
                _log("Batch PyPI install failed: {}".format(error[:500]), Qgis.Warning)
                return False, "Batch PyPI install failed: {}".format(error[:200])
            _log("Batch PyPI install succeeded", Qgis.Success)
        except subprocess.TimeoutExpired:
            _log("Batch PyPI install timed out", Qgis.Warning)
            return False, "Batch PyPI install timed out"
        except Exception as e:
            _log("Batch PyPI install exception: {}".format(e), Qgis.Warning)
            return False, "Batch PyPI install error: {}".format(str(e)[:200])

    # --- Batch 2: torch packages (CPU index) ---
    if torch_specs:
        if cancel_check and cancel_check():
            return False, "Installation cancelled"

        if progress_callback:
            progress_callback(55, "Batch installing PyTorch CPU packages...")

        _log("Batch uv install (torch): {}".format(", ".join(torch_specs)), Qgis.Info)

        cmd = [_uv_path, "pip", "install", "--upgrade"]
        cmd.extend(_get_uv_ssl_flags())
        cmd.extend(["--index-url", TORCH_CPU_INDEX])
        cmd.extend(torch_specs)
        cmd.extend(["--python", python_path])

        try:
            result = _run_pip_install(
                cmd=cmd, timeout=3600,
                env=env, subprocess_kwargs=subprocess_kwargs,
                package_name="torch", package_index=1,
                total_packages=2,
                progress_start=55, progress_end=95,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
            if result.returncode != 0:
                error = result.stderr or result.stdout or ""
                _log("Batch torch install failed: {}".format(error[:500]), Qgis.Warning)
                return False, "Batch torch install failed: {}".format(error[:200])
            _log("Batch torch install succeeded", Qgis.Success)
        except subprocess.TimeoutExpired:
            _log("Batch torch install timed out", Qgis.Warning)
            return False, "Batch torch install timed out"
        except Exception as e:
            _log("Batch torch install exception: {}".format(e), Qgis.Warning)
            return False, "Batch torch install error: {}".format(str(e)[:200])

    if progress_callback:
        progress_callback(100, "All dependencies installed (batch)")

    _log("=" * 50, Qgis.Success)
    _log("All SCP dependencies installed via batch uv!", Qgis.Success)
    _log("=" * 50, Qgis.Success)

    return True, "All dependencies installed successfully (batch uv)"


# --- Main install_dependencies ---

def install_dependencies(venv_dir=None, progress_callback=None, cancel_check=None):
    if venv_dir is None:
        venv_dir = VENV_DIR

    if not venv_exists(venv_dir):
        return False, "Virtual environment does not exist"

    pip_path = get_venv_pip_path(venv_dir)
    _log("Installing dependencies using: {}".format(pip_path), Qgis.Info)

    # Upgrade pip (skip when using uv)
    python_path_pre = get_venv_python_path(venv_dir)
    if _uv_available:
        _log("Using uv for installation, skipping pip upgrade", Qgis.Info)
        if progress_callback:
            progress_callback(20, "Using uv package installer...")
    else:
        if progress_callback:
            progress_callback(20, "Upgrading pip...")
        try:
            upgrade_cmd = [
                python_path_pre, "-m", "pip", "install",
                "--upgrade", "pip",
                "--disable-pip-version-check",
                "--no-warn-script-location",
            ]
            upgrade_cmd.extend(_get_pip_ssl_flags())
            upgrade_result = subprocess.run(
                upgrade_cmd,
                capture_output=True, text=True, timeout=120,
                env=_get_clean_env_for_venv(),
                **_get_subprocess_kwargs(),
            )
            if upgrade_result.returncode == 0:
                _log("pip upgraded successfully", Qgis.Success)
            else:
                _log("pip upgrade failed (non-critical): {}".format(
                    (upgrade_result.stderr or upgrade_result.stdout or "")[:200]),
                    Qgis.Warning)
        except Exception as e:
            _log("pip upgrade failed (non-critical): {}\n{}".format(
                str(e)[:200], traceback.format_exc()), Qgis.Warning)

    total_packages = len(REQUIRED_PACKAGES)
    base_progress = 20
    progress_range = 80

    # Weighted progress: torch is the biggest download
    _weight_map = {
        "remotior-sensus": 10,
        "scipy": 10,
        "matplotlib": 10,
        "scikit-learn": 10,
        "torch": 35,
        "torchvision": 15,
    }
    _weights = [_weight_map.get(name, 10) for name, _ in REQUIRED_PACKAGES]
    weight_total = sum(_weights)
    _cumulative = [0]
    for w in _weights:
        _cumulative.append(_cumulative[-1] + w)

    def _pkg_progress_start(idx):
        return base_progress + int(progress_range * _cumulative[idx] / weight_total)

    def _pkg_progress_end(idx):
        return base_progress + int(progress_range * _cumulative[idx + 1] / weight_total)

    python_path = get_venv_python_path(venv_dir)

    # Try batch uv install first (2 commands instead of 6)
    if _uv_available and _uv_path:
        _log("Attempting batch uv install...", Qgis.Info)
        batch_ok, batch_msg = _try_batch_uv_install(
            venv_dir, progress_callback=progress_callback,
            cancel_check=cancel_check,
        )
        if batch_ok:
            return True, batch_msg
        _log("Batch uv install failed ({}), falling back to per-package install...".format(
            batch_msg), Qgis.Warning)
        if progress_callback:
            progress_callback(20, "Batch failed, installing packages individually...")

    for i, (package_name, version_spec) in enumerate(REQUIRED_PACKAGES):
        if cancel_check and cancel_check():
            _log("Installation cancelled by user", Qgis.Warning)
            return False, "Installation cancelled"

        package_spec = "{}{}".format(package_name, version_spec)
        pkg_start = _pkg_progress_start(i)
        pkg_end = _pkg_progress_end(i)

        # Determine if this package needs the PyTorch CPU index
        is_torch_package = package_name in ("torch", "torchvision")

        if progress_callback:
            if package_name == "torch":
                progress_callback(
                    pkg_start,
                    "Installing {} (CPU, ~300MB)... ({}/{})".format(
                        package_name, i + 1, total_packages))
            else:
                progress_callback(
                    pkg_start,
                    "Installing {}... ({}/{})".format(
                        package_name, i + 1, total_packages))

        _log("[{}/{}] Installing {}...".format(i + 1, total_packages, package_spec), Qgis.Info)

        pip_args = [
            "install", "--upgrade",
            "--no-warn-script-location",
            "--disable-pip-version-check",
            "--prefer-binary",
        ]
        pip_args.extend(_get_pip_ssl_flags())
        pip_args.extend(_get_pip_proxy_args())

        # torch/torchvision: use CPU index
        if is_torch_package:
            pip_args.extend([
                "--index-url", TORCH_CPU_INDEX,
            ])
            _log("Using CPU index for {}".format(package_name), Qgis.Info)

        pip_args.append(package_spec)

        env = _get_clean_env_for_venv()
        subprocess_kwargs = _get_subprocess_kwargs()

        # Timeouts
        if package_name == "torch":
            pkg_timeout = 3600
        elif package_name == "torchvision":
            pkg_timeout = 1200
        else:
            pkg_timeout = 600

        install_failed = False
        install_error_msg = ""
        last_returncode = None

        try:
            base_cmd = _build_install_cmd(python_path, pip_args)

            result = _run_pip_install(
                cmd=base_cmd, timeout=pkg_timeout,
                env=env, subprocess_kwargs=subprocess_kwargs,
                package_name=package_name, package_index=i,
                total_packages=total_packages,
                progress_start=pkg_start, progress_end=pkg_end,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )

            if result.returncode == -1 and "cancelled" in (result.stderr or "").lower():
                return False, "Installation cancelled"

            # Windows process crash retry
            if not _uv_available and _is_windows_process_crash(result.returncode):
                _log("Process crash detected, retrying with pip.exe...", Qgis.Warning)
                if progress_callback:
                    progress_callback(pkg_start, "Retrying {}...".format(package_name))
                fallback_cmd = [pip_path] + pip_args
                result = _run_pip_install(
                    cmd=fallback_cmd, timeout=pkg_timeout,
                    env=env, subprocess_kwargs=subprocess_kwargs,
                    package_name=package_name, package_index=i,
                    total_packages=total_packages,
                    progress_start=pkg_start, progress_end=pkg_end,
                    progress_callback=progress_callback,
                    cancel_check=cancel_check,
                )

            # "unable to create process" retry
            if not _uv_available and result.returncode != 0:
                error_output = result.stderr or result.stdout or ""
                if _is_unable_to_create_process(error_output):
                    _log("Unable to create process, retrying with pip.exe...", Qgis.Warning)
                    fallback_cmd = [pip_path] + pip_args
                    result = _run_pip_install(
                        cmd=fallback_cmd, timeout=pkg_timeout,
                        env=env, subprocess_kwargs=subprocess_kwargs,
                        package_name=package_name, package_index=i,
                        total_packages=total_packages,
                        progress_start=pkg_start, progress_end=pkg_end,
                        progress_callback=progress_callback,
                        cancel_check=cancel_check,
                    )

            # SSL error retry
            if result.returncode != 0 and not _is_windows_process_crash(result.returncode):
                error_output = result.stderr or result.stdout or ""
                if _is_ssl_error(error_output):
                    _log("SSL error, retrying with --trusted-host...", Qgis.Warning)
                    if progress_callback:
                        progress_callback(pkg_start, "SSL error, retrying {}...".format(package_name))
                    ssl_cmd = base_cmd + _get_pip_ssl_flags()
                    result = _run_pip_install(
                        cmd=ssl_cmd, timeout=pkg_timeout,
                        env=env, subprocess_kwargs=subprocess_kwargs,
                        package_name=package_name, package_index=i,
                        total_packages=total_packages,
                        progress_start=pkg_start, progress_end=pkg_end,
                        progress_callback=progress_callback,
                        cancel_check=cancel_check,
                    )

            # Hash mismatch retry
            if result.returncode != 0 and not _is_windows_process_crash(result.returncode):
                error_output = result.stderr or result.stdout or ""
                if _is_hash_mismatch(error_output):
                    _log("Hash mismatch, retrying with --no-cache-dir...", Qgis.Warning)
                    nocache_flag = "--no-cache" if _uv_available else "--no-cache-dir"
                    nocache_cmd = base_cmd + [nocache_flag]
                    result = _run_pip_install(
                        cmd=nocache_cmd, timeout=pkg_timeout,
                        env=env, subprocess_kwargs=subprocess_kwargs,
                        package_name=package_name, package_index=i,
                        total_packages=total_packages,
                        progress_start=pkg_start, progress_end=pkg_end,
                        progress_callback=progress_callback,
                        cancel_check=cancel_check,
                    )

            # Network error retry with backoff
            if result.returncode != 0 and not _is_windows_process_crash(result.returncode):
                error_output = result.stderr or result.stdout or ""
                if _is_network_error(error_output):
                    for attempt in range(1, 5):
                        wait = 5 * (2 ** (attempt - 1))
                        _log("Network error, retrying in {}s ({}/4)...".format(wait, attempt), Qgis.Warning)
                        if progress_callback:
                            progress_callback(pkg_start, "Network error, retry {}/4...".format(attempt))
                        time.sleep(wait)
                        if cancel_check and cancel_check():
                            return False, "Installation cancelled"
                        result = _run_pip_install(
                            cmd=base_cmd, timeout=pkg_timeout,
                            env=env, subprocess_kwargs=subprocess_kwargs,
                            package_name=package_name, package_index=i,
                            total_packages=total_packages,
                            progress_start=pkg_start, progress_end=pkg_end,
                            progress_callback=progress_callback,
                            cancel_check=cancel_check,
                        )
                        if result.returncode == 0:
                            break

            if result.returncode == 0:
                _log("Successfully installed {}".format(package_spec), Qgis.Success)
                if progress_callback:
                    progress_callback(pkg_end, "{} installed".format(package_name))
            else:
                error_msg = result.stderr or result.stdout or "Return code {}".format(result.returncode)
                _log("Failed to install {}: {}".format(package_spec, error_msg[:500]), Qgis.Critical)
                install_failed = True
                install_error_msg = error_msg
                last_returncode = result.returncode

        except subprocess.TimeoutExpired:
            _log("Installation of {} timed out".format(package_spec), Qgis.Critical)
            install_failed = True
            install_error_msg = "Installation of {} timed out".format(package_name)
        except Exception as e:
            tb = traceback.format_exc()
            _log("Exception installing {}:\n{}".format(package_spec, tb), Qgis.Critical)
            install_failed = True
            install_error_msg = "Error installing {}: {}".format(package_name, str(e)[:200])

        if install_failed:
            _log("pip error: {}".format(install_error_msg[:500]), Qgis.Critical)

            if last_returncode is not None and _is_windows_process_crash(last_returncode):
                _log(_get_crash_help(venv_dir), Qgis.Warning)
                return False, "Failed to install {}: process crashed".format(package_name)

            if sys.platform == "win32" and _is_dll_init_error(install_error_msg):
                _log(_get_vcpp_help(), Qgis.Warning)
                return False, "Failed to install {}: {}".format(package_name, _get_vcpp_help())

            if _is_ssl_error(install_error_msg):
                _log(_get_ssl_error_help(install_error_msg), Qgis.Warning)
                return False, "Failed to install {}: SSL error".format(package_name)

            if _is_proxy_auth_error(install_error_msg):
                return False, "Failed to install {}: proxy authentication required (407)".format(package_name)

            if _is_network_error(install_error_msg):
                return False, "Failed to install {}: network error".format(package_name)

            if _is_antivirus_error(install_error_msg):
                _log(_get_pip_antivirus_help(venv_dir), Qgis.Warning)
                return False, "Failed to install {}: blocked by antivirus".format(package_name)

            if _is_unable_to_create_process(install_error_msg):
                return False, (
                    "Failed to install {}: unable to create process.\n\n"
                    "Please try:\n"
                    "  1. Delete the folder: {}\n"
                    "  2. Restart QGIS".format(package_name, CACHE_DIR)
                )

            return False, "Failed to install {}: {}".format(
                package_name, install_error_msg[:200])

    if progress_callback:
        progress_callback(100, "All dependencies installed")

    _log("=" * 50, Qgis.Success)
    _log("All SCP dependencies installed successfully!", Qgis.Success)
    _log("Virtual environment: {}".format(venv_dir), Qgis.Success)
    _log("=" * 50, Qgis.Success)

    return True, "All dependencies installed successfully"


# --- Proxy / env helpers ---

def _get_qgis_proxy_settings():
    try:
        from qgis.core import QgsSettings
        from urllib.parse import quote as url_quote

        settings = QgsSettings()
        enabled = settings.value("proxy/proxyEnabled", False, type=bool)
        if not enabled:
            return None

        host = settings.value("proxy/proxyHost", "", type=str)
        if not host:
            return None

        port = settings.value("proxy/proxyPort", "", type=str)
        user = settings.value("proxy/proxyUser", "", type=str)
        password = settings.value("proxy/proxyPassword", "", type=str)

        proxy_url = "http://"
        if user:
            proxy_url += url_quote(user, safe="")
            if password:
                proxy_url += ":" + url_quote(password, safe="")
            proxy_url += "@"
        proxy_url += host
        if port:
            proxy_url += ":{}".format(port)

        return proxy_url
    except Exception as e:
        _log("Could not read QGIS proxy settings: {}".format(e), Qgis.Warning)
        return None


def _get_pip_proxy_args():
    proxy_url = _get_qgis_proxy_settings()
    if proxy_url:
        _log("Using QGIS proxy for pip: {}".format(
            proxy_url.split("@")[-1] if "@" in proxy_url else proxy_url),
            Qgis.Info)
        return ["--proxy", proxy_url]
    return []


def _get_clean_env_for_venv():
    env = os.environ.copy()

    vars_to_remove = [
        'PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV',
        'QGIS_PREFIX_PATH', 'QGIS_PLUGINPATH',
    ]
    for var in vars_to_remove:
        env.pop(var, None)

    env["PYTHONIOENCODING"] = "utf-8"

    # Propagate QGIS proxy settings to environment
    proxy_url = _get_qgis_proxy_settings()
    if proxy_url:
        env.setdefault("HTTP_PROXY", proxy_url)
        env.setdefault("HTTPS_PROXY", proxy_url)

    return env


def _get_subprocess_kwargs():
    os.makedirs(CACHE_DIR, exist_ok=True)
    kwargs = {"cwd": CACHE_DIR}
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    return kwargs


# --- Verification ---

def _get_verification_code(package_name):
    """Get verification code that actually tests the package works."""
    if package_name == "remotior-sensus":
        # Don't fully import — remotior_sensus depends on osgeo (GDAL)
        # which is only available inside the QGIS environment, not in the
        # standalone venv Python. Just check the package metadata exists.
        return (
            "from importlib.metadata import version; "
            "print(version('remotior-sensus'))"
        )
    elif package_name == "scipy":
        return "import scipy; from scipy.spatial.distance import euclidean; print(euclidean([0,0],[1,1]))"
    elif package_name == "matplotlib":
        return "import matplotlib; print(matplotlib.__version__)"
    elif package_name == "scikit-learn":
        return "import sklearn; print(sklearn.__version__)"
    elif package_name == "torch":
        return "import torch; t = torch.tensor([1, 2, 3]); print(t.sum())"
    elif package_name == "torchvision":
        return "import torchvision; print(torchvision.__version__)"
    else:
        import_name = package_name.replace("-", "_")
        return "import {}".format(import_name)


def _get_verification_timeout(package_name):
    if package_name == "torch":
        return 300
    elif package_name == "torchvision":
        return 180
    else:
        return 60


def _build_batch_verify_script():
    """Build a Python script that verifies all packages in a single process."""
    checks = []
    for package_name, _ in REQUIRED_PACKAGES:
        code = _get_verification_code(package_name)
        # Wrap each check so we get per-package status
        checks.append(
            "try:\n"
            "    " + code + "\n"
            "    print('OK: " + package_name + "')\n"
            "except Exception as e:\n"
            "    print('FAIL: " + package_name + ": ' + str(e))\n"
            "    failed.append('" + package_name + "')"
        )
    script = "import sys\nfailed = []\n" + "\n".join(checks)
    script += "\nif failed:\n    print('FAILED: ' + ','.join(failed))\n    sys.exit(1)\n"
    script += "else:\n    print('ALL_OK')\n    sys.exit(0)\n"
    return script


def _try_batch_verify(venv_dir):
    """Verify all packages in a single Python subprocess.

    Returns (True, msg) if all pass, (False, msg) otherwise.
    """
    python_path = get_venv_python_path(venv_dir)
    env = _get_clean_env_for_venv()
    subprocess_kwargs = _get_subprocess_kwargs()

    script = _build_batch_verify_script()

    # Write script to temp file to avoid command-line length issues
    script_fd, script_path = tempfile.mkstemp(suffix=".py", prefix="scp_verify_")
    try:
        with os.fdopen(script_fd, "w", encoding="utf-8") as f:
            f.write(script)

        cmd = [python_path, script_path]
        _log("Running batch verification...", Qgis.Info)

        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=300, env=env, **subprocess_kwargs,
        )

        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0 and "ALL_OK" in output:
            _log("Batch verification passed", Qgis.Success)
            return True, "All packages verified (batch)"
        else:
            _log("Batch verification failed: {}".format(output[:500]), Qgis.Warning)
            return False, output[:300]
    except subprocess.TimeoutExpired:
        _log("Batch verification timed out (300s)", Qgis.Warning)
        return False, "Batch verification timed out"
    except Exception as e:
        _log("Batch verification error: {}".format(e), Qgis.Warning)
        return False, "Batch verification error: {}".format(str(e)[:200])
    finally:
        try:
            os.unlink(script_path)
        except Exception:
            pass


def verify_venv(venv_dir=None, progress_callback=None):
    if venv_dir is None:
        venv_dir = VENV_DIR

    if not venv_exists(venv_dir):
        return False, "Virtual environment not found"

    # Try batch verification first (1 process instead of 6)
    if progress_callback:
        progress_callback(0, "Verifying all packages (batch)...")
    batch_ok, batch_msg = _try_batch_verify(venv_dir)
    if batch_ok:
        if progress_callback:
            progress_callback(100, "Verification complete")
        _log("Virtual environment verified successfully (batch)", Qgis.Success)
        return True, "Virtual environment ready"
    _log("Batch verify failed, falling back to per-package verification...", Qgis.Warning)

    python_path = get_venv_python_path(venv_dir)
    env = _get_clean_env_for_venv()
    subprocess_kwargs = _get_subprocess_kwargs()

    total_packages = len(REQUIRED_PACKAGES)
    for i, (package_name, _) in enumerate(REQUIRED_PACKAGES):
        if progress_callback:
            percent = int((i / total_packages) * 100)
            progress_callback(percent, "Verifying {}... ({}/{})".format(
                package_name, i + 1, total_packages))

        verify_code = _get_verification_code(package_name)
        cmd = [python_path, "-c", verify_code]
        pkg_timeout = _get_verification_timeout(package_name)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=pkg_timeout, env=env, **subprocess_kwargs,
            )

            if result.returncode != 0:
                error_detail = result.stderr[:300] if result.stderr else result.stdout[:300]
                _log("Package {} verification failed: {}".format(
                    package_name, error_detail), Qgis.Warning)

                if _is_dll_init_error(error_detail):
                    _log(_get_vcpp_help(), Qgis.Warning)
                    return False, "Package {} failed: {}".format(package_name, _get_vcpp_help())

                # Try force-reinstall for broken C extensions
                error_lower = error_detail.lower()
                broken_markers = [
                    "no module named", "_libs", "dll load failed",
                    "importerror", "applocker", "application control",
                ]
                if any(m in error_lower for m in broken_markers):
                    _log("Package {} has broken extensions, force-reinstalling...".format(
                        package_name), Qgis.Warning)
                    pkg_spec = package_name
                    for name, spec in REQUIRED_PACKAGES:
                        if name == package_name:
                            pkg_spec = "{}{}".format(name, spec)
                            break

                    reinstall_args = [
                        "install", "--force-reinstall", "--no-deps",
                        "--disable-pip-version-check", "--prefer-binary",
                    ] + _get_pip_ssl_flags()

                    if package_name in ("torch", "torchvision"):
                        reinstall_args.extend(["--index-url", TORCH_CPU_INDEX])

                    reinstall_args.append(pkg_spec)
                    reinstall_cmd = _build_install_cmd(python_path, reinstall_args)

                    try:
                        subprocess.run(
                            reinstall_cmd,
                            capture_output=True, text=True,
                            timeout=300, env=env, **subprocess_kwargs,
                        )
                    except Exception:
                        pass

                    # Retry verification
                    try:
                        result2 = subprocess.run(
                            cmd, capture_output=True, text=True,
                            timeout=pkg_timeout, env=env, **subprocess_kwargs,
                        )
                        if result2.returncode == 0:
                            _log("Package {} fixed after reinstall".format(package_name), Qgis.Success)
                            continue
                    except Exception:
                        pass

                    return False, "Package {} is broken: {}".format(
                        package_name, error_detail[:200])

                return False, "Package {} is broken: {}".format(
                    package_name, error_detail[:200])

        except subprocess.TimeoutExpired:
            _log("Verification of {} timed out, retrying...".format(package_name), Qgis.Info)
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    timeout=pkg_timeout, env=env, **subprocess_kwargs,
                )
                if result.returncode != 0:
                    error_detail = result.stderr[:300] if result.stderr else result.stdout[:300]
                    return False, "Package {} is broken: {}".format(
                        package_name, error_detail[:200])
            except subprocess.TimeoutExpired:
                return False, "Verification error: {} (timed out)".format(package_name)
            except Exception as e:
                return False, "Verification error: {}".format(package_name)

        except Exception as e:
            _log("Failed to verify {}: {}".format(package_name, str(e)), Qgis.Warning)
            return False, "Verification error: {}".format(package_name)

    if progress_callback:
        progress_callback(100, "Verification complete")

    _log("Virtual environment verified successfully", Qgis.Success)
    return True, "Virtual environment ready"


# --- Main orchestrator ---

def create_venv_and_install(progress_callback=None, cancel_check=None):
    """
    Complete installation: download Python + uv + create venv + install packages.

    Progress breakdown:
    - 0-10%:   Download Python standalone
    - 10-13%:  Download uv (non-fatal)
    - 13-18%:  Create virtual environment
    - 18-95%:  Install packages
    - 95-100%: Verify installation
    """
    from .python_manager import (
        standalone_python_exists, standalone_python_is_current,
        download_python_standalone, get_python_full_version,
        remove_standalone_python,
    )

    if sys.version_info < (3, 9):
        py_ver = "{}.{}.{}".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        return False, (
            "Python {} is too old. SCP requires Python 3.9+.\n"
            "Please upgrade to QGIS 3.22 or later.".format(py_ver)
        )

    _log_system_info()

    # Writability check
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        test_file = os.path.join(CACHE_DIR, ".write_test")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_file)
    except (OSError, IOError) as e:
        hint = (
            "Cannot write to install directory: {}\n"
            "Error: {}\n\n"
            "Set the SCP_CACHE_DIR environment variable "
            "to a writable directory, then restart QGIS."
        ).format(CACHE_DIR, e)
        _log(hint, Qgis.Critical)
        return False, hint

    # Clean up old venv directories from previous Python versions
    _cleanup_old_venv_directories()

    # Re-download standalone Python if version doesn't match QGIS
    if standalone_python_exists() and not standalone_python_is_current():
        _log("Standalone Python version mismatch, re-downloading...", Qgis.Warning)
        remove_standalone_python()
        if venv_exists():
            try:
                shutil.rmtree(VENV_DIR)
                _log("Removed stale venv after Python version mismatch", Qgis.Info)
            except Exception as e:
                _log("Failed to remove stale venv: {}".format(e), Qgis.Warning)

    # Step 1: Download Python standalone
    if not standalone_python_exists():
        python_version = get_python_full_version()
        _log("Downloading Python {} standalone...".format(python_version), Qgis.Info)

        def python_progress(percent, msg):
            if progress_callback:
                progress_callback(int(percent * 0.10), msg)

        success, msg = download_python_standalone(
            progress_callback=python_progress, cancel_check=cancel_check)

        if not success:
            if sys.platform == "win32":
                qgis_python = _get_qgis_python()
                if qgis_python:
                    _log("Standalone download failed, using QGIS Python: {}".format(msg), Qgis.Warning)
                    if progress_callback:
                        progress_callback(10, "Using QGIS Python (fallback)...")
                else:
                    return False, "Failed to download Python: {}".format(msg)
            else:
                return False, "Failed to download Python: {}".format(msg)

        if cancel_check and cancel_check():
            return False, "Installation cancelled"
    else:
        _log("Python standalone already installed", Qgis.Info)
        if progress_callback:
            progress_callback(10, "Python standalone ready")

    # Step 1b: Download uv (non-fatal)
    global _uv_available, _uv_path
    if uv_exists() and verify_uv():
        _uv_available = True
        _uv_path = get_uv_path()
        _log("uv already installed", Qgis.Info)
        if progress_callback:
            progress_callback(13, "uv package installer ready")
    else:
        if progress_callback:
            progress_callback(10, "Downloading uv package installer...")
        try:
            def uv_progress(percent, uv_msg):
                if progress_callback:
                    progress_callback(10 + int(percent * 0.03), uv_msg)

            uv_ok, uv_msg = download_uv(
                progress_callback=uv_progress, cancel_check=cancel_check)
            if uv_ok:
                _uv_available = True
                _uv_path = get_uv_path()
                _log("uv downloaded", Qgis.Info)
            else:
                _uv_available = False
                _uv_path = None
                _log("uv download failed (non-fatal): {}".format(uv_msg), Qgis.Warning)
        except Exception as e:
            _uv_available = False
            _uv_path = None
            _log("uv download failed (non-fatal): {}".format(e), Qgis.Warning)
        if progress_callback:
            progress_callback(13, "uv: {}".format(
                "ready" if _uv_available else "unavailable, using pip"))

    if cancel_check and cancel_check():
        return False, "Installation cancelled"

    # Step 2: Create virtual environment
    if venv_exists():
        _log("Virtual environment already exists", Qgis.Info)
        if progress_callback:
            progress_callback(18, "Virtual environment ready")
    else:
        def venv_progress(percent, msg):
            if progress_callback:
                progress_callback(13 + int(percent * 0.05), msg)

        success, msg = create_venv(progress_callback=venv_progress)
        if not success:
            return False, msg

        if cancel_check and cancel_check():
            return False, "Installation cancelled"

    # Step 3: Install dependencies
    def deps_progress(percent, msg):
        if progress_callback:
            mapped = 18 + int((percent - 20) * (95 - 18) / 80)
            progress_callback(min(mapped, 95), msg)

    success, msg = install_dependencies(
        progress_callback=deps_progress, cancel_check=cancel_check)

    if not success:
        return False, msg

    # Step 4: Verify (95-100%)
    def verify_progress(percent, msg):
        if progress_callback:
            mapped = 95 + int(percent * 0.04)
            progress_callback(min(mapped, 99), msg)

    is_valid, verify_msg = verify_venv(progress_callback=verify_progress)

    if not is_valid:
        return False, "Verification failed: {}".format(verify_msg)

    _write_deps_hash()

    if progress_callback:
        progress_callback(100, "All dependencies installed and verified")

    return True, "Virtual environment ready"


# --- Quick check (no subprocess) ---

def _quick_check_packages(venv_dir=None):
    """
    Fast filesystem-based check that packages exist in the venv site-packages.
    Does NOT spawn subprocesses - safe to call from the main thread.
    """
    if venv_dir is None:
        venv_dir = VENV_DIR

    site_packages = get_venv_site_packages(venv_dir)
    if not os.path.exists(site_packages):
        return False, "site-packages directory not found"

    for package_name, dir_name in PACKAGE_MARKERS.items():
        pkg_dir = os.path.join(site_packages, dir_name)
        if not os.path.exists(pkg_dir):
            _log("Quick check: {} not found at {}".format(package_name, pkg_dir), Qgis.Warning)
            return False, "Package {} not found".format(package_name)

    # Check deps hash
    stored_hash = _read_deps_hash()
    current_hash = _compute_deps_hash()
    if stored_hash is not None and stored_hash != current_hash:
        _log("Quick check: deps hash mismatch", Qgis.Warning)
        return False, "Dependencies need updating"
    if stored_hash is None:
        _write_deps_hash()

    _log("Quick check: all packages found", Qgis.Info)
    return True, "All packages found"


# --- Status / removal ---

def get_venv_status():
    from .python_manager import standalone_python_exists, get_python_full_version

    if not standalone_python_exists():
        return False, "Dependencies not installed"

    if not venv_exists():
        return False, "Virtual environment not configured"

    is_present, msg = _quick_check_packages()
    if is_present:
        python_version = get_python_full_version()
        return True, "Ready (Python {})".format(python_version)
    else:
        return False, "Virtual environment incomplete: {}".format(msg)


def remove_venv(venv_dir=None):
    if venv_dir is None:
        venv_dir = VENV_DIR

    if not os.path.exists(venv_dir):
        return True, "Virtual environment does not exist"

    try:
        shutil.rmtree(venv_dir)
        _log("Removed virtual environment: {}".format(venv_dir), Qgis.Success)
        return True, "Virtual environment removed"
    except Exception as e:
        _log("Failed to remove venv: {}".format(e), Qgis.Warning)
        return False, "Failed to remove venv: {}".format(str(e)[:200])


def _cleanup_old_venv_directories():
    """Remove old venv_pyX.Y directories that don't match current Python version."""
    current_venv_name = "venv_{}".format(PYTHON_VERSION)
    try:
        if not os.path.exists(CACHE_DIR):
            return
        for entry in os.listdir(CACHE_DIR):
            entry_cmp = os.path.normcase(entry)
            current_cmp = os.path.normcase(current_venv_name)
            if entry_cmp.startswith(os.path.normcase("venv_py")) and entry_cmp != current_cmp:
                old_path = os.path.join(CACHE_DIR, entry)
                if os.path.isdir(old_path):
                    try:
                        shutil.rmtree(old_path)
                        _log("Cleaned up old venv: {}".format(old_path), Qgis.Info)
                    except Exception as e:
                        _log("Failed to remove old venv {}: {}".format(old_path, e), Qgis.Warning)
    except Exception as e:
        _log("Error scanning for old venvs: {}".format(e), Qgis.Warning)
