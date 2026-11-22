# -*- coding: utf-8 -*-
# Blenderer Addon version 2026-08 v2.6.0 (Blender 5.2)
# with VisualComponents
# ################Thanks for Tang ###########################
import sys, os
sys.path.append('')
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
import bpy, mathutils, glob, re, random
import time, subprocess, importlib, json
from math import radians
import xml.etree.ElementTree as ET
import material_helper


# read arguments given on the command line
sys_argv = sys.argv
sys_argv = sys_argv[sys_argv.index("--") + 1:]  
uri_root = sys_argv[0]
result_path = sys_argv[1] if len(sys_argv) > 1 else None

video_container = 'MP4' # only MP4 is supported
importlib.reload(material_helper)
random.seed(1)

def write_render_progress(stage, done=0, total=0):
    if not result_path:
        return
    path = result_path + '.progress'
    temporary_path = path + '.tmp'
    try:
        with open(temporary_path, 'w', encoding='ascii') as stream:
            stream.write('%s %d %d' % (stage, done, total))
        os.replace(temporary_path, path)
    except OSError:
        # A progress read can briefly lock the file on Windows.
        pass


def render_animation_with_progress(stage, frame_count):
    if not result_path:
        return bpy.ops.render.render(animation=True)

    frames_done = 0
    last_update = 0.0

    def frame_rendered(scene, *args):
        nonlocal frames_done, last_update
        frames_done = min(frame_count, frames_done + 1)
        now = time.monotonic()
        if frames_done == frame_count or now - last_update >= 0.25:
            write_render_progress(stage, frames_done, frame_count)
            last_update = now

    write_render_progress(stage, 0, frame_count)
    handlers = bpy.app.handlers.render_post
    handlers.append(frame_rendered)
    try:
        return bpy.ops.render.render(animation=True)
    finally:
        handlers.remove(frame_rendered)


def write_export_result(status, path=None, detail=None, frames=None, fps=None, temporary=None):
    if result_path:
        with open(result_path, 'w', encoding='utf-8') as stream:
            json.dump({'status': status, 'path': path, 'detail': detail,
                       'frames': frames, 'fps': fps, 'temporary': temporary}, stream)


def render_destination(path, output_dir=None):
    if not result_path:
        return path
    return os.path.join(output_dir or os.path.dirname(path),
                        os.path.basename(result_path) + '.partial' + os.path.splitext(path)[1].lower())


def publish_rendered_file(result, temporary, destination):
    require_rendered_file(result, temporary)
    if temporary != destination:
        os.rename(temporary, destination)  # On Windows, never replaces an existing output.
    return destination


def require_rendered_file(result, path):
    if 'FINISHED' not in result or not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise RuntimeError('Blender did not finish writing: %s' % path)
    return path


def auto_increment_filename(filename):
    if not os.path.isfile(filename):
        return filename
    filepathroot, file_extension = os.path.splitext(filename)
    search_name = filepathroot + '*' + file_extension
    current_pics = glob.glob(search_name)
    list_of_numbers = [0]
    for pic in current_pics:
        fname = os.path.splitext(pic)[0]
        try:
            number = re.findall('[0-9]+$', fname)[0]
            list_of_numbers.append(int(number))
        except IndexError:
            pass
    list_of_numbers = sorted(list_of_numbers)
    new_number = list_of_numbers[-1]+1
    filename = '%s %d%s' % (filepathroot, new_number , file_extension)
    return filename


def create_frame_output_folder(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    index = 0
    while True:
        name = 'Picture_frames %d' % index if index else 'Picture_frames'
        folder = os.path.join(output_dir, name)
        try:
            os.mkdir(folder)
            return folder
        except FileExistsError:
            index += 1


def set_cpu_affinity(cpu_indices):
    # Bind the Blender process to specific CPU cores via Windows API.
    # cpu_indices: list of CPU numbers, e.g. [1,2,3,4,5] → mask 0b111110 = 0x3E
    # CPU0 and any CPU not in the list are excluded from rendering threads.
    # Uses SetProcessAffinityMask (64-bit safe via c_ulonglong pointers).
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # 64-bit safe: DWORD_PTR is 8 bytes on x64
        kernel32.GetProcessAffinityMask.restype = ctypes.c_int
        kernel32.GetProcessAffinityMask.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
        ]
        kernel32.SetProcessAffinityMask.restype = ctypes.c_int
        kernel32.SetProcessAffinityMask.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ulonglong,
        ]
        handle = kernel32.GetCurrentProcess()
        mask = 0
        for idx in cpu_indices:
            mask |= (1 << idx)
        ret = kernel32.SetProcessAffinityMask(handle, mask)
        if ret:
            print('CPU affinity set to CPUs %s (mask=%s)' % (cpu_indices, bin(mask)))
        else:
            print('Warning: SetProcessAffinityMask failed')
        return ret != 0
    except Exception as e:
        print('Warning: CPU affinity setup failed (%s)' % e)
        return False


def reset_cpu_affinity():
    # Restore CPU affinity to all logical processors the OS allows for this process.
    # Reads the system affinity mask via GetProcessAffinityMask and writes it back,
    # so we don't hard-code any CPU index (works on any core count / P+E mix).
    # Safe no-op on non-Windows / if the API fails: render keeps current affinity.
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.GetProcessAffinityMask.restype = ctypes.c_int
        kernel32.GetProcessAffinityMask.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
        ]
        kernel32.SetProcessAffinityMask.restype = ctypes.c_int
        kernel32.SetProcessAffinityMask.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ulonglong,
        ]
        handle = kernel32.GetCurrentProcess()
        proc_mask = ctypes.c_ulonglong()
        sys_mask  = ctypes.c_ulonglong()
        ret = kernel32.GetProcessAffinityMask(handle, ctypes.byref(proc_mask), ctypes.byref(sys_mask))
        if not ret:
            print('Warning: GetProcessAffinityMask failed, keeping current affinity.')
            return False
        ret = kernel32.SetProcessAffinityMask(handle, sys_mask.value)
        if ret:
            print('CPU affinity reset to all available cores (mask=%s)' % bin(sys_mask.value))
        else:
            print('Warning: reset_cpu_affinity failed, keeping current affinity.')
        return ret != 0
    except Exception as e:
        print('Warning: CPU affinity reset failed (%s)' % e)
        return False


# ---------------------------------------------------------------------------
# GPU vendor / driver pre-detection (no GPU driver DLLs loaded — zero crash risk)
# ---------------------------------------------------------------------------

def _detect_gpu_info_via_wmi():
    """Query PCI GPU adapters + Intel driver version via PowerShell CIM.

    Does NOT load any GPU driver DLL. Uses Win32_VideoController CIM class,
    which reads already-cached plug-and-play info from the registry.

    Returns
    -------
    tuple : (vendors: set, intel_driver_version: str|None)
        vendors              : {'NVIDIA', 'AMD', 'Intel'} found via PCI Vendor ID
        intel_driver_version : Intel display driver version string,
                               None if no Intel adapter or query failed.
    """
    import subprocess
    vendors = set()
    intel_drv = None
    CREATE_NO_WINDOW = 0x08000000
    ps_script = r'''
$ErrorActionPreference = 'Stop'
Get-CimInstance Win32_VideoController | ForEach-Object {
    $pnp = $_.PNPDeviceID
    if (-not $pnp -or $pnp -notlike 'PCI\*') { return }
    $name = $_.Name
    $drv  = $_.DriverVersion
    Write-Output "$pnp|$name|$drv"
}
'''
    try:
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_script],
            capture_output=True, text=True, timeout=15,
            creationflags=CREATE_NO_WINDOW
        )
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if not line or line.count('|') < 2:
                    continue
                pnp, _name, drv = line.split('|', 2)
                pnp_up = pnp.upper()
                if 'VEN_10DE' in pnp_up:
                    vendors.add('NVIDIA')
                elif 'VEN_1002' in pnp_up:
                    vendors.add('AMD')
                elif 'VEN_8086' in pnp_up:
                    vendors.add('Intel')
                    drv = (drv or '').strip()
                    if drv and not intel_drv:
                        intel_drv = drv
    except Exception:
        pass
    return vendors, intel_drv


def _intel_driver_version_is_bad(version_str):
    """Check whether an Intel display driver version is in the known
    ze_loader.dll SEH-crashing range.

    Ranges (4-part format MAJOR.MINOR.BUILD.REVISION):
      - 32.0.100.4723 .. 32.0.100.4778 : known bad (2026-03 WU push)
      - 32.0.100.4779 .. 32.0.100.4799 : borderline (treat as bad / safe skip)
      - >= 32.0.100.4800               : fixed
      - <= 32.0.100.4022 (and other older builds) : historically safe

    Returns
    -------
    tuple : (is_bad: bool, parsed_tuple: tuple|None, reason: str|None)
    """
    if not version_str:
        return False, None, None
    try:
        parts = [int(x) for x in version_str.split('.')]
        while len(parts) < 4:
            parts.append(0)
        major, minor, build, rev = parts[0], parts[1], parts[2], parts[3]
    except (ValueError, AttributeError):
        return False, None, None

    parsed = (major, minor, build, rev)

    # We only have confirmed regression data for the 32.0.100.* series.
    # Everything else: don't flag as bad.
    if (major, minor, build) != (32, 0, 100):
        return False, parsed, None

    BAD_LO, BAD_HI = 4723, 4778
    FIXED_LO = 4800

    if BAD_LO <= rev <= BAD_HI:
        return True, parsed, 'driver in known Level Zero crashing range (4723-4778)'
    if rev < 4500:
        return False, parsed, 'pre-4500 driver build (historically safe)'
    if rev >= FIXED_LO:
        return False, parsed, 'post-fix driver build (%d+)' % FIXED_LO
    # 4779 - 4799 gap: conservative, treat as bad
    return True, parsed, 'borderline pre-fix driver build (4779-4799)'


def _is_nvidia_rtx_card(name):
    """Return True if the GPU device name indicates an NVIDIA RTX series
    card that supports the OptiX backend.

    RTX cards (Turing/Ampere/Ada/Hopper) carry the 'RTX' keyword.  GTX 10xx
    and older do not.  Titan RTX and Titan Ada are also classified as RTX.
    """
    if not name:
        return False
    low = name.lower()
    if 'rtx' in low:
        return True
    if 'gtx 10' in low or 'gtx10' in low or 'gtx 9' in low or 'gtx 7' in low:
        return False
    return False


def setup_cycles_render(config_dict):
    """Configure Cycles render settings: samples, GPU backend, and devices.

    NEW PROBING STRATEGY (v2.6.1 — ze_loader.dll safe):
        * The user selects ONE backend in the VC UI.  We probe ONLY that
          backend's vendor — no cross-vendor fallback, no auto-switch.
        * Before touching the Cycles prefs (which can trigger ze_loader.dll
          loading / SEH crashes on bad Intel drivers), we run a WMI-based
          PCI vendor pre-check and (for oneAPI) a driver-version pre-check.
        * CUDA / OptiX  -> requires NVIDIA GPU                (never touch oneAPI)
        * HIP          -> requires AMD GPU                   (never touch oneAPI)
        * oneAPI       -> requires Intel GPU + driver NOT in known-bad range
        * OptiX        -> requires RTX-capable card within the NVIDIA group,
                         with same-vendor fallback to CUDA if not RTX.
        * Pass 2 (iGPU last-resort retry) is REMOVED — iGPU only usable when
          the user explicitly chooses oneAPI (allow_igpu is True there).

    Called only when engine == 'CYCLES'.  EEVEE settings are left untouched.
    """
    scn = bpy.context.scene
    # ---------------------------------------------------------------
    # Samples / denoising (unaffected by the backend choice change)
    # ---------------------------------------------------------------
    cycles_samples = int(config_dict.get('cycles_samples', 64))
    scn.cycles.samples = cycles_samples
    scn.cycles.use_denoising = True
    scn.cycles.denoising_use_gpu = True

    # ---------------------------------------------------------------
    # CPU branch — still not supported, keep original error + exit
    # ---------------------------------------------------------------
    device = config_dict.get('cycles_device', 'CPU')
    if device != 'GPU':
        print('=' * 60)
        print('You need GPU!你需要一张独立显卡渲染更合适！')
        print('=' * 60)
        os.system('pause')
        sys.exit(0)

    scn.cycles.device = 'GPU'

    # ---------------------------------------------------------------
    # Backend identity: UI label -> Blender API enum -> required vendor
    # ---------------------------------------------------------------
    BACKEND_MAP = {'CUDA': 'CUDA', 'OptiX': 'OPTIX', 'HIP': 'HIP', 'oneAPI': 'ONEAPI'}
    BACKEND_REQUIRED_VENDOR = {
        'CUDA':   'NVIDIA',
        'OPTIX':  'NVIDIA',
        'HIP':    'AMD',
        'ONEAPI': 'Intel',
    }
    requested_label = config_dict.get('cycles_backend', 'CUDA')
    requested_api = BACKEND_MAP.get(requested_label, 'CUDA')
    req_vendor = BACKEND_REQUIRED_VENDOR[requested_api]
    friendly_label = {v: k for k, v in BACKEND_MAP.items()}.get(requested_api, requested_api)

    # ---------------------------------------------------------------
    # Step 1 — PCI vendor pre-check (WMI CIM, no driver DLL loaded)
    # ---------------------------------------------------------------
    present_vendors, intel_drv_version = _detect_gpu_info_via_wmi()
    if present_vendors and req_vendor not in present_vendors:
        print('=' * 60)
        print('Cycles backend "%s" requires a %s GPU, but WMI PCI scan'
              % (requested_label, req_vendor))
        print('did not find a %s display adapter on this machine.' % req_vendor)
        if present_vendors:
            print('Detected display adapter vendors: %s'
                  % ', '.join(sorted(present_vendors)))
        else:
            print('Detected display adapter vendors: (none / WMI unavailable)')
        print('')
        if 'NVIDIA' in present_vendors:
            print('Recommendation: change Cycles Backend to "CUDA" or "OptiX".')
        if 'AMD' in present_vendors:
            print('Recommendation: change Cycles Backend to "HIP".')
        if 'Intel' in present_vendors:
            print('Recommendation: change Cycles Backend to "oneAPI" (Intel Arc / iGPU).')
        if not present_vendors:
            print('Recommendation: install an NVIDIA, AMD, or Intel Arc discrete GPU.')
        print('')
        print('You need GPU!你需要一张独立显卡渲染更合适！')
        print('=' * 60)
        os.system('pause')
        sys.exit(0)

    # ---------------------------------------------------------------
    # Step 2 — oneAPI path: driver version pre-check
    # ---------------------------------------------------------------
    if requested_api == 'ONEAPI':
        is_bad, parsed_ver, reason = _intel_driver_version_is_bad(intel_drv_version)
        if is_bad:
            ver_str = ('.'.join(str(p) for p in parsed_ver)
                       if parsed_ver else (intel_drv_version or 'unknown'))
            print('=' * 60)
            print('Intel GPU driver version "%s" has a known Level Zero compatibility'
                  % ver_str)
            print('issue: %s.' % (reason or 'driver confirmed problematic'))
            print('Loading ze_loader.dll with this driver will crash Blender with an')
            print('unrecoverable 0xc0000005 SEH access violation.  To protect your render')
            print('the oneAPI backend has been SKIPPED before any GPU driver DLL was loaded.')
            print('')
            print('Fix options:')
            print('  1. Upgrade Intel GPU driver to >= 32.0.100.4800   (confirmed fixed)')
            print('  2. Downgrade Intel GPU driver to 31.0.101.4500    (historically safe)')
            print('  3. If you have a second discrete GPU (NVIDIA / AMD), switch Cycles')
            print('     Backend to CUDA / OptiX / HIP in the Blenderer UI instead.')
            print('=' * 60)
            os.system('pause')
            sys.exit(0)

    # ---------------------------------------------------------------
    # Step 3 — Now safe to touch the Cycles preferences API
    # ---------------------------------------------------------------
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
    except Exception as e:
        print('=' * 60)
        print('Cycles: cannot access Cycles preferences: %s' % e)
        print('You need GPU!你需要一张独立显卡渲染更合适！')
        print('=' * 60)
        os.system('pause')
        sys.exit(0)

    # ---------------------------------------------------------------
    # Reusable local helpers
    # ---------------------------------------------------------------
    INTEL_IGPU_KEYWORDS = (
        'intel(r) hd graphics', 'intel(r) uhd graphics',
        'intel(r) iris(tm) graphics', 'intel(r) iris(r) xe graphics',
        'intel iris plus', 'intel uhd', 'intel hd',
    )
    INTEL_ARC_KEYWORDS = ('arc a', 'intel(r) arc(tm)')

    def _looks_like_intel_igpu(name):
        low = (name or '').lower()
        if any(k in low for k in INTEL_ARC_KEYWORDS):
            return False  # Arc = discrete, keep it
        return any(k in low for k in INTEL_IGPU_KEYWORDS)

    def _looks_like_amd_igpu(name):
        """Return True if the AMD device name looks like an integrated APU
        GPU (Radeon Graphics, R5/R7/R9 Graphics, Vega 3/8/11).  Discrete
        AMD cards (RX 4xx/5xx/5000/6000/7000, Radeon Pro, R9 2xx/3xx,
        Vega 56/64, VII, Instinct) return False.
        """
        low = (name or '').lower()
        if 'amd' not in low and 'radeon' not in low:
            return False  # not an AMD device

        # ---- Discrete AMD GPU patterns — keep these ----
        # RX series: RX 480 / RX 570 / RX 5700 / RX 6700 / RX 7900 ...
        if re.search(r'\brx\s+\d', low):
            return False
        # Workstation / datacenter / enthusiast discrete
        if any(k in low for k in ('pro', 'instinct', 'vii')):
            return False
        # Old R-series discrete: R5/R7/R9 followed by a MODEL NUMBER
        # (e.g. R7 260X, R9 390).  APUs are "R5 Graphics" / "R7 Graphics"
        # (no number after R-series).
        if re.search(r'\br[579]\s+\d', low):
            return False
        # Discrete Vega: Vega 56 / Vega 64.  APU Vega is Vega 3 / 8 / 11.
        if re.search(r'\bvega\s+(56|64)\b', low):
            return False

        # ---- Everything else AMD Radeon = integrated APU iGPU ----
        return True

    def _looks_like_igpu(name):
        """Unified iGPU check: True for Intel HD/UHD/Iris(non-Arc) and
        AMD Radeon APUs.  Discrete GPUs (NVIDIA, Intel Arc, AMD RX/Pro/
        Vega-discrete) return False.
        """
        return _looks_like_intel_igpu(name) or _looks_like_amd_igpu(name)

    def _reset_prefs(prefs):
        # NOTE: do NOT call prefs.get_devices() / prefs.refresh_devices() here.
        # In Blender 5.2 those helpers enumerate EVERY backend
        # (CUDA, OPTIX, HIP, METAL, ONEAPI) which loads ze_loader.dll and
        # crashes Blender with an 0xc0000005 access violation on systems
        # with a broken Intel Level Zero driver.  We only set the type to
        # NONE and clear the "use" flags of already-known device entries.
        try:
            prefs.compute_device_type = 'NONE'
        except Exception:
            pass
        try:
            for dev in prefs.devices:
                dev.use = False
        except Exception:
            pass

    def _try_backend(prefs_in, backend_api, allow_igpu=False, filter_fn=None):
        """Try a SINGLE backend.  Returns (list_of_gpus, error_or_None).

        If filter_fn(name) is provided, non-CPU devices that fail the filter
        are skipped (logged in the error string) so OptiX can restrict to
        RTX-only cards while still enumerating all CUDA-family devices.
        """
        errors = []
        try:
            _reset_prefs(prefs_in)
        except Exception as e:
            errors.append('prefs-reset: %s' % e)
        try:
            prefs_in.compute_device_type = backend_api
        except Exception as e:
            return [], 'compute_device_type="%s" raised: %s' % (backend_api, e)
        # Enumerate ONLY the requested backend.  Using get_devices() would
        # call refresh_devices() which probes every backend (incl. ONEAPI)
        # and crashes via ze_loader.dll on broken Intel Level Zero drivers.
        try:
            prefs_in.get_device_list(backend_api)
        except Exception as e:
            return [], 'get_device_list("%s") raised: %s' % (backend_api, e)
        try:
            raw = list(getattr(prefs_in, 'devices', []))
        except Exception as e:
            return [], 'reading devices raised: %s' % e
        gpus = []
        for d in raw:
            try:
                dtype = getattr(d, 'type', 'CPU')
                dname = getattr(d, 'name', '')
            except Exception:
                continue
            if dtype == 'CPU':
                continue
            # Only keep devices that belong to the backend we just probed.
            # prefs.devices may still hold entries from earlier probes.
            if dtype != backend_api:
                continue
            if not allow_igpu and _looks_like_igpu(dname):
                errors.append('skipping iGPU "%s" (integrated graphics not allowed, use discrete GPU)' % dname)
                continue
            if filter_fn is not None and not filter_fn(dname):
                errors.append('skipping "%s" (failed backend device filter)'
                              % dname)
                continue
            gpus.append(d)
        return gpus, ('; '.join(errors) if errors else None)

    # ---------------------------------------------------------------
    # Step 4 — Probe ONLY the requested backend (no cross-vendor fallback)
    # ---------------------------------------------------------------
    probe_log = []
    chosen_gpus = []
    final_api = requested_api
    final_friendly = friendly_label

    # allow_igpu policy:
    #   ALL backends (CUDA / OPTIX / HIP / ONEAPI) = False
    #   Integrated GPUs (Intel HD/UHD/Iris-non-Arc, AMD Radeon APU) are
    #   unreliable for Cycles rendering and are NEVER used.  Only discrete
    #   GPUs (NVIDIA, Intel Arc, AMD RX/Pro/Vega-discrete) are accepted.
    allow_igpu = False

    probe_filter = _is_nvidia_rtx_card if requested_api == 'OPTIX' else None

    chosen_gpus, err = _try_backend(prefs, requested_api,
                                    allow_igpu=allow_igpu,
                                    filter_fn=probe_filter)
    if chosen_gpus:
        probe_log.append('%s: OK (%d device(s))'
                         % (friendly_label, len(chosen_gpus)))
    else:
        probe_log.append('%s: %s'
                         % (friendly_label, err or 'no usable GPU devices'))

        # -----------------------------------------------------------
        # OPTIX ONLY — same-vendor fallback to CUDA (e.g. GTX 10xx
        # has NVIDIA vendor ID but no OptiX support).  This is the
        # ONLY "switch" path we keep; it does NOT change vendor.
        # -----------------------------------------------------------
        if requested_api == 'OPTIX':
            print('OptiX: no RTX-capable NVIDIA devices found.  '
                  'Trying CUDA (same-vendor fallback)...')
            cuda_gpus, cuda_err = _try_backend(prefs, 'CUDA', allow_igpu=False)
            if cuda_gpus:
                probe_log.append('CUDA: OK (%d device(s))' % len(cuda_gpus))
                final_api = 'CUDA'
                final_friendly = 'CUDA'
                chosen_gpus = cuda_gpus
            else:
                probe_log.append('CUDA: %s'
                                 % (cuda_err or 'no usable GPU devices'))

    if not chosen_gpus:
        print('=' * 60)
        print('No usable Cycles GPU device found for backend "%s".'
              % requested_label)
        if requested_label == 'OptiX' and final_api == 'CUDA':
            print('(OptiX required RTX; CUDA same-vendor fallback also failed.)')
        elif requested_label == 'OptiX':
            print('(OptiX requires an NVIDIA RTX series card.  If your card is a')
            print(' GTX 10xx / older NVIDIA, switch Cycles Backend to "CUDA".)')
        elif requested_label == 'oneAPI':
            print('(If you have an Intel Arc card, ensure the driver is installed')
            print(' and updated.  Pure Intel iGPU (HD/UHD/Iris non-Arc) is NOT')
            print(' reliably supported by Cycles oneAPI — use a discrete GPU.)')
        print('')
        print('Probe log:')
        for line in probe_log:
            print('  - %s' % line)
        print('')
        print('You need GPU!你需要一张独立显卡渲染更合适！')
        print('=' * 60)
        os.system('pause')
        sys.exit(0)

    # ---------------------------------------------------------------
    # Step 5 — Final backend activation + enable chosen devices,
    #           disable everything else (esp. CPU)
    # ---------------------------------------------------------------
    _reset_prefs(prefs)
    try:
        prefs.compute_device_type = final_api
        # Enumerate ONLY the final backend (avoids ze_loader.dll crash).
        prefs.get_device_list(final_api)
    except Exception as e:
        print('=' * 60)
        print('Cycles final backend setup failed: %s' % e)
        print('Probe log:')
        for line in probe_log:
            print('  - %s' % line)
        print('You need GPU!你需要一张独立显卡渲染更合适！')
        print('=' * 60)
        os.system('pause')
        sys.exit(0)

    chosen_names = set()
    for g in chosen_gpus:
        try:
            chosen_names.add(getattr(g, 'name', ''))
        except Exception:
            pass
    try:
        for dev in prefs.devices:
            dname = getattr(dev, 'name', '')
            dev.use = (dname in chosen_names)
    except Exception:
        pass

    # ---------------------------------------------------------------
    # Step 6 — Report
    # ---------------------------------------------------------------
    igpu_used = any(_looks_like_igpu(getattr(g, 'name', ''))
                    for g in chosen_gpus)
    if igpu_used:
        print('!' * 60)
        print('WARNING: an integrated GPU (Intel iGPU or AMD APU) is being')
        print('used for Cycles rendering.  This is unreliable — render errors')
        print('and driver crashes are likely.  Use a discrete GPU instead.')
        print('!' * 60)

    print('Cycles GPU backend: %s (%d device(s))'
          % (final_friendly, len(chosen_gpus)))
    print('Cycles GPU devices: %s'
          % ', '.join('%s (%s)' % (getattr(g, 'name', '?'),
                                   getattr(g, 'type', '?'))
                      for g in chosen_gpus))
    if probe_log:
        print('Cycles backend probe log:')
        for line in probe_log:
            print('  - %s' % line)
    print('Cycles: device=GPU, samples=%d, denoising=%s (gpu=%s)' % (
        scn.cycles.samples, scn.cycles.use_denoising,
        scn.cycles.denoising_use_gpu))


def do_import_vc():
    '''
    ------------------------------------------------------------------------
    one function wonder:
        read scene settings from xml file and set blender properties accordingly
        read scene structure from .vcbx file: lights, camera, nodes
        generate geometry based on the obj data and keyframe it
        add lights and camera
        and bunch of other things
    ------------------------------------------------------------------------
    '''
    global video_container
    #
    # parse recording.vcbx keyframe data into list of lists
    #
    # New format (>=2.6.0): JSON with 6-decimal float precision (fast + compact).
    # Old format (<2.6.0): Python repr + eval() (slow, full-precision, unsafe).
    # We try JSON first and fall back to eval for legacy recordings.
    import json
    rec_file_uri = os.path.join(uri_root, 'recording.vcbx' )
    rec_file = open(rec_file_uri, 'r', encoding='utf8')
    mydata = rec_file.read()
    rec_file.close()
    mydata_stripped = mydata.lstrip()
    if mydata_stripped.startswith('[') or mydata_stripped.startswith('{'):
        # JSON format: arrays start with '[' or '{'
        rec_data = json.loads(mydata)
    else:
        # Legacy repr format: fall back to eval for backward compatibility
        rec_data = eval(mydata)
    #
    # parse config.xml into a dictionary
    #
    config_file_uri = os.path.join(uri_root, 'render_config.xml' )
    tree = ET.parse(config_file_uri)
    root = tree.getroot()
    config_dict = {}
    for kid in root:
        config_dict[kid.tag] = kid.text
    #
    # set some render setting 
    # 
    bpy.context.scene.render.engine = config_dict['engine']
    bpy.context.scene.render.resolution_x = int(config_dict['resolution_x'])
    bpy.context.scene.render.resolution_y = int(config_dict['resolution_y'])
    bpy.context.scene.render.resolution_percentage = int(config_dict['resolution_percentage'])
    bpy.context.scene.render.use_border = False
    # EEVEE samples — harmless when engine is CYCLES (EEVEE settings exist but unused)
    bpy.context.scene.eevee.taa_render_samples = int(config_dict['samples'])
    # Cycles-specific: samples, device, GPU compute backend
    if config_dict['engine'] == 'CYCLES':
        setup_cycles_render(config_dict)
    # CPU thread tuning: Blender default is AUTO (all cores, e.g. 16 threads).
    # EEVEE is GPU-driven; 5 threads bound to CPU1-CPU5 are enough for scene
    # prep + compositing, cutting CPU usage on other cores (CPU0, CPU6+).
    # Cycles GPU also uses this binding. Cycles CPU mode keeps all cores.
    if (config_dict.get('openinblender') == 'True' or
            (config_dict['engine'] == 'CYCLES' and config_dict.get('cycles_device', 'CPU') == 'CPU')):
        bpy.context.scene.render.threads_mode = 'AUTO'
    else:
        bpy.context.scene.render.threads_mode = 'FIXED'
        bpy.context.scene.render.threads = 5
        # Bind process to CPU1,CPU2,CPU3,CPU4,CPU5 (mask 0b111110 = 0x3E)
        # CPU0 and CPU6+ are left free for OS / other tasks
        set_cpu_affinity([1, 2, 3, 4, 5])
    # PNG compression: 15 ≈ zlib level 1, lightweight with small size benefit.
    # Higher values (25+) add CPU load with minimal size benefit.
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.compression = 15
    # Persistent data: reuse scene data across animation frames.
    # EEVEE benchmark: 1.9x faster (2.1s → 1.1s for 5-frame anim).
    # Cycles: marginal effect (BVH rebuilt per frame anyway); kept on for both.
    bpy.context.scene.render.use_persistent_data = True
    # Compositor GPU acceleration (Blender 5.2+).
    # Match user's screenshot settings: GPU device, FULL precision, GPU denoise,
    # BALANCED preview quality, HIGH final quality.
    bpy.context.scene.render.compositor_device = 'GPU'
    bpy.context.scene.render.compositor_denoise_device = 'GPU'
    bpy.context.scene.render.compositor_precision = 'FULL'
    bpy.context.scene.render.compositor_denoise_final_quality = 'HIGH'
    bpy.context.scene.render.compositor_denoise_preview_quality = 'BALANCED'
    print('Compositor: device=GPU, denoise_device=GPU, precision=FULL, final_quality=HIGH')
    bpy.context.scene.frame_start = frameS = int(config_dict['frame_start'])
    bpy.context.scene.frame_end = frameE = int(config_dict['frame_end'])
    bpy.context.scene.render.fps = int(config_dict['anim_fps'])
    if config_dict.get('is_animation') == '1':
        bpy.context.scene.render.fps_base = 1.0
    bpy.context.scene.render.filepath = config_dict['filepath']
    video_container = config_dict['video_container']
    bpy.context.scene.view_settings.exposure = envstrength = float(config_dict['exposure'])
    # Blender 4.2+/5.x EEVEE Next: use_soft_shadows/use_gtao/use_ssr removed (AO & soft shadows always on)
    bpy.context.scene.render.filter_size = 2 # smoother edges
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.view_settings.look = 'Medium High Contrast'

    # bpy.context.scene.eevee.use_motion_blur = True
    # bpy.context.scene.eevee.motion_blur_samples = 8
    # bpy.context.scene.eevee.motion_blur_shutter = 0.5

    # Bloom (Blender 4.2+/5.x: EEVEE bloom removed, implemented via compositor Glare node)
    use_bloom = config_dict['bloom'] == 'True'
    bloom_intensity = float(config_dict['bloomintensity'])
    # Edge rendering i.e. freestyle
    bpy.context.scene.render.use_freestyle = config_dict['use_renderedges'] == 'True'
    if bpy.context.scene.render.use_freestyle:
        bpy.data.linestyles["LineStyle"].thickness = int(config_dict['edge_line_thickness'])
    
    #
    # read rest of the settings to variables
    #
    depthOFnode = config_dict['depthOFnode']
    depthOfFieldObject = None
    depth_fstop = float(config_dict['depth_fstop'])
    re_render = config_dict['re_render'] == 'True'
    openinblender = config_dict['openinblender'] == 'True'
    if config_dict['envimage']:
        envimage = config_dict['envimage'].replace('file:///' , '')
    else:
        envimage = None
    envstrength = float(config_dict['envstrength'])
    envrotation = float(config_dict['envrotation'])
    envtype = config_dict['envtype']
    envcolorgb = [float(x) for x in config_dict['envcolor'].split(';')]
    envvisible = config_dict['envvisible'] == 'True'
    floorvisible = config_dict['floorvisible']
    floorsize = config_dict['floorsize']
    floortype = config_dict['floortype']
    if config_dict.get('floorcolorimage'):
        floorcolorimage = config_dict.get('floorcolorimage').replace('file:///' , '')
    else:
        floorcolorimage = ''
    if config_dict.get('floorbumpimage'):
        floorbumpimage = config_dict.get('floorbumpimage').replace('file:///' , '')
    else:
        floorbumpimage = ''
    floorbumpstrength = float(config_dict.get('floorbumpstrength'))
    floortexturesize = float(config_dict['floortexturesize'])
    floorcolor = [float(x) for x in config_dict['floorcolor'].split(';')]
    scene_bound = eval(config_dict['scene_bound'])
    floor_overshoot = float(config_dict['floor_overshoot'])
    floor_corners = scene_bound[:] # [-X, +X, -Y, +Y, -Z, +Z]
    floor_corners[0] -= floor_overshoot
    floor_corners[1] += floor_overshoot
    floor_corners[2] -= floor_overshoot
    floor_corners[3] += floor_overshoot
    floor_corners[4] -= floor_overshoot
    floor_corners[5] += floor_overshoot
    CameraFOV = float(config_dict['CameraFOV'])
    #
    # init scene
    #
    clearScene(re_render)
    #
    # Collections
    #
    if re_render: # find existing collections
        collection_utils = bpy.data.collections['Utils']
        collection_comps = bpy.data.collections['Components']
    else: # create new collections
        collection_utils = bpy.data.collections.new('Utils')
        bpy.context.scene.collection.children.link(collection_utils)
        collection_comps = bpy.data.collections.new('Components')
        bpy.context.scene.collection.children.link(collection_comps)
    #
    # Set HDRI (env map)
    #
    print('Setting Environment HDRI map...')
    scn = bpy.context.scene
    scn.world.use_nodes = True
    wd = scn.world
    nt = bpy.data.worlds[wd.name].node_tree
    env_strength_node = None
    for node in nt.nodes:
        nt.nodes.remove(node) # clear if there's any pre-existing nodes
    backNode = nt.nodes.new(type="ShaderNodeBackground")
    outputNode = nt.nodes.new(type="ShaderNodeOutputWorld")
    if envtype == 'Image' and envimage:
        envNode = nt.nodes.new(type="ShaderNodeTexEnvironment")
        envTexture_img = bpy.data.images.load(envimage)
        envNode.image = envTexture_img
        envNode.location.x = backNode.location.x-300
        outputNode.location.x = backNode.location.x+200
        envNode.location.y = backNode.location.y
        envNodeOut = envNode.outputs['Color']
        backColIn = backNode.inputs['Color']
        backNode.inputs[1].default_value = envstrength
        env_strength_node = backNode
        textcoordNode = nt.nodes.new(type="ShaderNodeTexCoord")
        textcoordNode.location.x = backNode.location.x-900
        mappingNode = nt.nodes.new(type="ShaderNodeMapping")
        mappingNode.location.x = backNode.location.x-700
        mappingNode.inputs['Rotation'].default_value[2] = -radians(envrotation)
        nt.links.new(envNodeOut, backColIn)
        nt.links.new(textcoordNode.outputs[0], mappingNode.inputs[0])
        nt.links.new(mappingNode.outputs[0], envNode.inputs[0])
        nt.links.new(backNode.outputs[0], outputNode.inputs[0])
    else: #color RGB
        # backNode was already created above; no need to look it up by name
        # (Blender 5.x localized node names break the old nt.nodes['Background'] lookup)
        backColIn = backNode.inputs['Color']
        if len(envcolorgb) == 3:
            ccolor = [0,0,0,1]
            ccolor[:3] = envcolorgb
            envcolorgb = tuple(ccolor)
        envcolorgb = [x**2.2 for x in envcolorgb] # gamma correction
        backColIn.default_value = envcolorgb
        backNode.inputs[1].default_value = envstrength
        env_strength_node = backNode
        nt.links.new(backNode.outputs[0], outputNode.inputs[0])
    if envvisible:
        bpy.context.scene.world.cycles_visibility.camera = True
        bpy.context.scene.render.film_transparent = False
        if use_bloom:
            setup_bloom_compositor(bloom_intensity)

    else:
        bpy.context.scene.world.cycles_visibility.camera = False
        bpy.context.scene.render.film_transparent = True
        set_up_backdrop(config_dict, use_bloom, bloom_intensity)
    #
    # Load materials
    #
    matData = loadMAT(os.path.join(uri_root,'VC_to_Blender_materials.mtl'))
    blender_materials = {}
    monochrome = config_dict['monochrome']
    simple_transparents = config_dict['use_simple_transparent'] == 'True'
    # Material version: OLD keeps legacy pipeline; NEW uses accurate sRGB
    # conversion + glass transmission + physical light correspondence.
    material_version = config_dict.get('material_version', 'OLD')
    setup_func = material_helper.setupMaterialNew if material_version == 'NEW' else material_helper.setupMaterial
    for materialname in matData:
            mObj = matData[materialname]
            if material_version == 'NEW':
                # NEW pipeline: pass VC specular (Ks) and emission (Ke) for
                # accurate VC<->Blender material correspondence.
                mat = setup_func(materialname,
                                mObj.Color,
                                mObj.ColorMap,
                                mObj.Metallic,
                                mObj.Roughness,
                                mObj.NormalMap,
                                mObj.Bumpiness,
                                mObj.Clearcoat,
                                mObj.ClearcoatRougness,
                                mObj.Opacity,
                                mObj.Style,
                                monochrome,
                                simple_transparents,
                                mObj.Specular,
                                mObj.Emission,
                                mObj.Color)  # reuse base color as emission tint when Ke > 0
            else:
                mat = setup_func(materialname,
                                mObj.Color,
                                mObj.ColorMap,
                                mObj.Metallic,
                                mObj.Roughness,
                                mObj.NormalMap,
                                mObj.Bumpiness,
                                mObj.Clearcoat,
                                mObj.ClearcoatRougness,
                                mObj.Opacity,
                                mObj.Style,
                                monochrome,
                                simple_transparents)
            blender_materials[materialname] = mat
    #
    # Loop rec_data to create objects and set the keyframe data
    #
    mycounter = 0
    allcount = len(rec_data)
    lamps = []
    sparks_on_off = []
    for item in rec_data:
        mycounter += 1 
        name = item[0]
        # v2.6.1-fix: Remove the broken encode('raw-unicode-escape') + decode('utf-8')
        # dance. It was a legacy Python 2 workaround that converted real Chinese
        # Unicode chars "信号升降机" into literal "\u4fe1..." text strings, causing
        # FileNotFoundError when looking up the OBJ file on disk.
        if isinstance(name, bytes):
            try:
                name = name.decode('utf-8')
            except UnicodeDecodeError:
                name = name.decode('latin-1', errors='replace')
        item_type = item[1]
        object_data = item[2]
        position_data_list = item[3]
        inipos = position_data_list[0]
        if re_render:
            print('Updating %i/%i: "%s"' % (mycounter, allcount, name) )
        else:
            print('Generating %i/%i: "%s"' % (mycounter, allcount, name) )
        if item_type == 'CAMERA':
            new_camera= bpy.ops.object.add(type='CAMERA', location=inipos[1:4])
            camera_object = bpy.context.selected_objects[0]
            camera_object.name = name
            collection_utils.objects.link(camera_object)
            point = mathutils.Vector((inipos[4], inipos[5], inipos[6]))
            look_at(camera_object, point)
            camera_object.data.clip_start = 0.01
            camera_object.data.clip_end = 150000
            camera_object.data.lens_unit = 'FOV'
            camera_object.data.angle = radians(CameraFOV)
            bpy.context.scene.camera = camera_object
            obj_object = camera_object
        elif '_LIGHT' in item_type:
            lamp_object = createLampEevee(name, inipos, item_type.replace('_LIGHT', ''), object_data, material_version)
            collection_utils.objects.link(lamp_object)
            obj_object = lamp_object
            lamps.append( [lamp_object, object_data] )
        elif item_type == 'NODE':
            if re_render:
                # find existing object in the opened  *.blend file
                geometry_object = bpy.data.objects[name] 
            else:
                # fresh scene. create new content
                uri = os.path.join(uri_root, name)
                uri += '.obj'
                geometry_object = loadmodel(uri, name, blender_materials, collection_comps)
            geometry_object.location = inipos[1:4]
            # Use quaternion rotation to avoid Euler angle gimbal-lock / ±180°
            # wrap-around jumps. VC's WPR can cross the ±180° boundary (e.g.
            # 170° → -170° = actual +200° rotation). Blender's LINEAR Euler
            # interpolation would reverse-rotate -340°, causing joints to
            # suddenly spin backwards. Quaternion SLERP always takes the
            # shortest path.
            geometry_object.rotation_mode = 'QUATERNION'
            _euler = mathutils.Euler((inipos[4], inipos[5], inipos[6]), 'XYZ')
            geometry_object.rotation_quaternion = _euler.to_quaternion()
            geometry_object.scale = inipos[7:]
            obj_object = geometry_object
            if depthOFnode and depthOFnode == name:
                depthOfFieldObject = geometry_object
        elif item_type == 'SPARKS':
            #
            # SPARKS
            #
            if re_render:
                # find existing object in the opened  *.blend file
                geometry_object = bpy.data.objects[name] 
            else:
                # fresh scene. create new content
                uri = os.path.join(uri_root, name)
                uri += '.obj'
                geometry_object = loadmodel(uri, name, blender_materials, collection_comps)
            geometry_object.location = inipos[1:4]
            geometry_object.rotation_mode = 'QUATERNION'
            _euler = mathutils.Euler((inipos[4], inipos[5], inipos[6]), 'XYZ')
            geometry_object.rotation_quaternion = _euler.to_quaternion()
            geometry_object.scale = inipos[7:10]
            obj_object = geometry_object
            if depthOFnode and depthOFnode == name:
                depthOfFieldObject = geometry_object
            spark_geo = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, enter_editmode=False, location=(200, 0, 0))
            spark_geo = bpy.context.selected_objects[0]
            spark_geo.scale[0] = 0.3
            spark_geo.scale[1] = 7
            spark_geo.scale[2] = 0.3
            spark_geo.name = 'VC_TO_BLENDER_SPARK_GEO'
            #spark_color1 = (0.3, 0.6, 1.0, 0.0)
            spark_color1 = object_data[0]
            sparks_material = material_helper.setupSparks('SparksEmission', spark_color1)
            spark_geo.data.materials.append( sparks_material )
            #2
            spark_geo = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, enter_editmode=False, location=(200, 0, 0))
            spark_geo = bpy.context.selected_objects[0]
            spark_geo.scale[0] = 0.5
            spark_geo.scale[1] = 5
            spark_geo.scale[2] = 0.5
            spark_geo.name = 'VC_TO_BLENDER_SPARK_GEO2'
            #spark_color2 = (0.15, 0.3, 1.0, 0.0)
            spark_color2 = object_data[0]
            sparks_material2 = material_helper.setupSparks('SparksEmission2', spark_color2)
            spark_geo.data.materials.append( sparks_material2 ) 
        else:
            continue
        t=0
        prev_spark_on = 0.0
        spark_lamp = None
        # Track previous quaternion per object for double-cover fix.
        # A quaternion q and -q represent the same rotation, but Blender's
        # SLERP interpolation takes the long path if dot(prev, curr) < 0.
        # Flip the sign when the dot product is negative so that successive
        # keyframes always take the shortest rotational path.
        prev_quat = None
        for i,L in enumerate(position_data_list):
            keyframe_index = L[0]
            new_loc = mathutils.Vector((L[1], L[2], L[3]))
            obj_object.location = new_loc
            if item_type in ['CAMERA', 'AREA_LIGHT', 'SPOT_LIGHT', 'POINT_LIGHT', 'SUN_LIGHT']:
                point = mathutils.Vector((L[4], L[5], L[6]))
                look_at(obj_object, point)
                # Double-cover fix for camera/lights too — look_at returns
                # a quaternion whose sign is unpredictable across frames.
                _quat = obj_object.rotation_quaternion.copy()
                if prev_quat is not None:
                    dot = prev_quat.dot(_quat)
                    if dot < 0.0:
                        _quat = -_quat
                prev_quat = _quat
                obj_object.rotation_quaternion = _quat
                if '_LIGHT' in item_type and len(L) > 7:
                    # NEW pipeline: apply physical unit correspondence for Sun lights
                    if material_version == 'NEW' and item_type == 'SUN_LIGHT':
                        obj_object.data.energy = L[7] / 100.0
                    else:
                        obj_object.data.energy = L[7]
                    obj_object.data.keyframe_insert( data_path = 'energy', frame = keyframe_index )
            else:
                # Convert Euler angles to quaternion and set rotation.
                # This prevents ±180° wrap-around jumps from causing
                # reverse-rotation during LINEAR interpolation.
                if obj_object.rotation_mode != 'QUATERNION':
                    obj_object.rotation_mode = 'QUATERNION'
                _euler = mathutils.Euler((L[4], L[5], L[6]), 'XYZ')
                _quat = _euler.to_quaternion()
                # Double-cover fix: ensure successive quaternions are in the
                # same hemisphere. If dot(prev, curr) < 0, flip the sign of
                # the current quaternion so SLERP takes the shortest path.
                if prev_quat is not None:
                    dot = prev_quat.dot(_quat)
                    if dot < 0.0:
                        _quat = -_quat
                prev_quat = _quat
                obj_object.rotation_quaternion = _quat
            if item_type == 'NODE':
                obj_object.scale = L[7], L[8], L[9]
            if item_type == 'SPARKS':
                spark_on = L[10]
                if spark_on and not prev_spark_on:
                    # create new spark lamp and particle system
                    # lamp1
                    lamp_data = ([x*255 for x in spark_color1[0:3]], 0, 0.1)
                    lamp_loc = list(new_loc[:])
                    lamp_loc.insert(0,0)
                    lamp_loc.extend([0,0,0])
                    lamp_loc = tuple(lamp_loc)
                    spark_lamp = createLampEevee(obj_object.name+'_lamp', lamp_loc, 'POINT', lamp_data )
                    spark_lamp.data.energy = 3.14
                    collection_utils.objects.link(spark_lamp)
                    spark_lamp.keyframe_insert( data_path = 'location', frame = keyframe_index )
                    spark_lamp.data.energy = 0.0
                    spark_lamp.data.keyframe_insert( data_path = 'energy', frame = keyframe_index )
                    spark_lamp.data.use_custom_distance = False
                    spark_lamp.data.cutoff_distance = 0.1
                    spark_lamp.data.use_shadow = True
                    # lamp2
                    lamp_data = ([x*255 for x in spark_color2[0:3]], 0, 0.1)
                    spark_lamp2 = createLampEevee(obj_object.name+'_lamp', lamp_loc, 'POINT', lamp_data )
                    spark_lamp2.data.energy = 3.14
                    collection_utils.objects.link(spark_lamp2)
                    spark_lamp2.keyframe_insert( data_path = 'location', frame = keyframe_index )
                    spark_lamp2.data.energy = 0.0
                    spark_lamp2.data.keyframe_insert( data_path = 'energy', frame = keyframe_index )
                    spark_lamp2.data.use_custom_distance = True
                    spark_lamp2.data.cutoff_distance = 0.1
                    spark_lamp2.data.use_shadow = False

                    children = getChildren(obj_object)
                    for child_mesh in children:
                        child_mesh.modifiers.new("part", type='PARTICLE_SYSTEM')
                        particles = child_mesh.particle_systems[-1]
                        particle_settings = particles.settings
                        particle_settings.frame_end = bpy.context.scene.frame_end
                        particle_settings.frame_start = keyframe_index
                        particle_settings.lifetime = 2 # edit this for intensity (integer)
                        particle_settings.lifetime_random = 1.0
                        particle_settings.normal_factor = 3.0
                        particle_settings.normal_factor = 6.0
                        particle_settings.factor_random = 0.4
                        particle_settings.emit_from = 'FACE'
                        particle_settings.distribution = 'RAND'
                        particle_settings.render_type = 'OBJECT'
                        particle_settings.instance_object = bpy.data.objects["VC_TO_BLENDER_SPARK_GEO"]
                        particle_settings.particle_size = 0.002
                        particle_settings.size_random = 0.99
                        particle_settings.use_rotations = True
                        #2
                        child_mesh.modifiers.new("part2", type='PARTICLE_SYSTEM')
                        particles = child_mesh.particle_systems[-1]
                        particle_settings2 = particles.settings
                        particle_settings2.frame_end = bpy.context.scene.frame_end
                        particle_settings2.frame_start = keyframe_index
                        particle_settings2.lifetime = 1 # edit this for intensity (integer)
                        particle_settings2.lifetime_random = 1.0
                        particle_settings2.normal_factor = 1.5
                        particle_settings2.factor_random = 0.6
                        particle_settings2.emit_from = 'FACE'
                        particle_settings2.distribution = 'RAND'
                        particle_settings2.render_type = 'OBJECT'
                        particle_settings2.instance_object = bpy.data.objects["VC_TO_BLENDER_SPARK_GEO2"]
                        particle_settings2.particle_size = 0.002
                        particle_settings2.size_random = 0.99
                        particle_settings2.use_rotations = True
                    # turn off env map light
                    sparks_on_off.append( [True,object_data[1], keyframe_index] )
                elif spark_on and prev_spark_on:
                    # keep particle system going and flicker the lights
                    if spark_lamp:
                        spark_lamp.location = new_loc
                        spark_lamp2.location = new_loc
                        spark_lamp.keyframe_insert( data_path = 'location', frame = keyframe_index )
                        spark_lamp2.keyframe_insert( data_path = 'location', frame = keyframe_index )
                        R = random.random()
                        if R < .4:
                            R=0
                        spark_lamp.data.energy = R*50.0#(R*50.0+spark_lamp.data.energy)/2
                        spark_lamp2.data.energy = R*250.0#(R*250.0+spark_lamp.data.energy)/2
                        spark_lamp.data.keyframe_insert( data_path = 'energy', frame = keyframe_index )
                        spark_lamp2.data.keyframe_insert( data_path = 'energy', frame = keyframe_index )
                elif not spark_on and prev_spark_on:
                    # turn particle system down
                    spark_lamp.data.energy = 0.0
                    spark_lamp.data.keyframe_insert( data_path = 'energy', frame = keyframe_index )
                    spark_lamp2.data.energy = 0.0
                    spark_lamp2.data.keyframe_insert( data_path = 'energy', frame = keyframe_index )
                    children = getChildren(obj_object)
                    # for child_mesh in children:
                    #     for i, particles in enumerate(child_mesh.particle_systems):
                    #         particle_settings = particles.settings
                    particle_settings.frame_end = keyframe_index
                    duration = particle_settings.frame_end - particle_settings.frame_start
                    particle_settings.count = int(100 * duration)
                    particle_settings2.frame_end = keyframe_index
                    duration = particle_settings2.frame_end - particle_settings2.frame_start
                    particle_settings2.count = int(200 * duration)
                    sparks_on_off.append( [False, object_data[1], keyframe_index] )
                prev_spark_on = spark_on
            obj_object.keyframe_insert( data_path = 'location', frame = keyframe_index )
            obj_object.keyframe_insert( data_path = 'rotation_quaternion', frame = keyframe_index )
            obj_object.keyframe_insert( data_path = 'scale', frame = keyframe_index )
            t+=1
    #
    # Turn other lighting on/off while sparks
    #
    for on_off,dim_rate, keyframe in sparks_on_off:
        strength_input = env_strength_node.inputs[1]
        strength_input.default_value = envstrength if on_off else dim_rate*envstrength
        strength_input.keyframe_insert('default_value', frame=keyframe)
        strength_input.default_value = dim_rate*envstrength if on_off else envstrength
        strength_input.keyframe_insert('default_value', frame=keyframe+3)
        for lamp, object_data in lamps:
            default_energy = object_data[1]
            lamp.data.energy = default_energy if on_off else dim_rate*default_energy
            lamp.data.keyframe_insert('energy', frame=keyframe)
            lamp.data.energy = dim_rate*default_energy if on_off else default_energy
            lamp.data.keyframe_insert('energy', frame=keyframe+3)
    #
    # Set LINEAR interpolation for all keyframes.
    # Blender's default BEZIER interpolation creates ease-in/ease-out speed
    # variation between keyframe pairs. With sparse keyframes (from long
    # animations or any OnRender gaps), this produces visible stutter/pulsing.
    # LINEAR gives constant-speed motion between keyframes for smooth playback.
    # This is a safety net complementing RealTimeMode=True in Blenderer.py.
    #
    def _set_linear_interp(anim_data):
        if not (anim_data and anim_data.action):
            return
        action = anim_data.action
        # Blender's animation API changed across versions:
        # - Blender <=4.3: action.fcurves (legacy, direct access)
        # - Blender 4.4+: slotted animation system. fcurves live inside
        #   action.layers[i].channelbags[j].fcurves
        # - Blender 5.2: legacy action.fcurves property removed entirely
        # Try each approach in order; if all fail, print available attributes
        # for debugging and skip (LINEAR interp is a secondary optimization;
        # the main stutter fix is RealTimeMode=True in Blenderer.py).
        try:
            if hasattr(action, 'fcurves'):
                # Legacy: Blender <=4.3
                for fcurve in action.fcurves:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'
            elif hasattr(action, 'layers'):
                # Slotted animation: Blender 4.4+/5.2+
                for layer in action.layers:
                    # channelbags hold the fcurves, one per slot
                    if hasattr(layer, 'channelbags'):
                        for channelbag in layer.channelbags:
                            for fcurve in channelbag.fcurves:
                                for kf in fcurve.keyframe_points:
                                    kf.interpolation = 'LINEAR'
                    else:
                        # Fallback: try strips (older slotted API variant)
                        for strip in getattr(layer, 'strips', []):
                            if hasattr(strip, 'channelbags'):
                                for channelbag in strip.channelbags:
                                    for fcurve in channelbag.fcurves:
                                        for kf in fcurve.keyframe_points:
                                            kf.interpolation = 'LINEAR'
        except Exception as e:
            print('Warning: Could not set LINEAR interpolation on %s: %s' % (
                action.name if hasattr(action, 'name') else '?', e))
    for obj in bpy.data.objects:
        _set_linear_interp(obj.animation_data)
        if obj.data and hasattr(obj.data, 'animation_data'):
            _set_linear_interp(obj.data.animation_data)
    if scn.world and scn.world.node_tree:
        _set_linear_interp(scn.world.node_tree.animation_data)
    print('Keyframe interpolation set to LINEAR for all objects.')
    #
    # Depth Of Field
    #
    if depthOfFieldObject:
        # depthOfFieldObject was cached during recdata loop (if defined by user)
        camera_object.data.dof.use_dof = True
        camera_object.data.dof.focus_object = depthOfFieldObject
        camera_object.data.dof.aperture_fstop = float(depth_fstop)
    else:
        camera_object.data.dof.use_dof = False
    #
    # Floor
    #
    Lx = floor_corners[1]-floor_corners[0]
    Ly = floor_corners[3]-floor_corners[2]
    Lz = floor_corners[5]-floor_corners[4]
    MidX = (floor_corners[0]+floor_corners[1])/2.0
    MidY = (floor_corners[2]+floor_corners[3])/2.0
    MidZ = (floor_corners[4]+floor_corners[5])/2.0
    if re_render:
        bpy.ops.object.select_all(action='DESELECT')
        if 'VC_TO_BLENDER_FLOOR_OBJECT' in bpy.data.objects:
            bpy.data.objects['VC_TO_BLENDER_FLOOR_OBJECT'].select_set(True) # Blender 2.8x
            bpy.ops.object.delete()
    if floorvisible == 'True':
        plane = bpy.ops.mesh.primitive_plane_add(location=(MidX,MidY,-0.001), size = .5)
        plane_object = bpy.context.selected_objects[0]
        plane_object.name = 'VC_TO_BLENDER_FLOOR_OBJECT'
        bpy.context.object.dimensions = (Lx,Ly,0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.object.editmode_toggle()

        scale = floortexturesize
        uvs = [(0,0),(Lx/scale,0),(Lx/scale,Ly/scale),(0,Ly/scale)]
        for loop, coords in zip(plane_object.data.loops, uvs):
            uv_coords = plane_object.data.uv_layers.active.data[loop.index].uv
            uv_coords[0] = coords[0]
            uv_coords[1] = coords[1]
        ob = bpy.context.active_object
        if len(floorcolor) == 3:
            ccolor = [0,0,0,1]
            ccolor[:3] = floorcolor
            floorcolor = tuple(ccolor)
        floorcolor = [x**2.2 for x in floorcolor] # gamma correction
        metallic = 0.0
        roughness = {
            'Factory Green Rubber': 0.66,
            'Blue Grey Epoxy': 0.38,
            'Charcoal Studded Rubber': 0.72,
        }.get(floortype, 0.6)
        clearcoat = 0.0
        clearcoat_rouhness = 0.0
        bumpiness = 1.0
        opacity = 1.0
        style = ''
        simple_transparents = config_dict['use_simple_transparent'] == 'True'
        materialname = "FLOORMATERIAL_BlenderToVC_X"
        if floortype == '<ShadowCatcher>':
            mat = material_helper.setupShadowCatcher(materialname, floorcolor)
        else:
            mat = material_helper.setupMaterial(materialname,
                                floorcolor,
                                floorcolorimage,
                                metallic,
                                roughness,
                                floorbumpimage,
                                floorbumpstrength,
                                clearcoat,
                                clearcoat_rouhness,
                                opacity,
                                style,
                                monochrome,
                                simple_transparents)
        ob.data.materials.append(mat)


    #
    # indirect_lighting
    #
    if config_dict['indirect_lighting'] != 'Off' :
        print('Baking indirect lighting.')
        iLx = scene_bound[1]-scene_bound[0]
        iLy = scene_bound[3]-scene_bound[2]
        iLz = scene_bound[5]-scene_bound[4]
        iMidX = (scene_bound[0]+scene_bound[1])/2.0
        iMidY = (scene_bound[2]+scene_bound[3])/2.0
        iMidZ = (scene_bound[4]+scene_bound[5])/2.0
        # Blender 5.x: lightprobe type 'GRID' renamed to 'VOLUME'; grid_resolution_* renamed to resolution_*
        bpy.ops.object.lightprobe_add(type='VOLUME', enter_editmode=False, location=(iMidX,iMidY,iMidZ))
        lightprobe_obj = bpy.context.object
        lightprobe_obj.scale[0] = iLx*.5
        lightprobe_obj.scale[1] = iLy*.5
        lightprobe_obj.scale[2] = iLz*.5
        desired_dist = {'Fast':5,'Normal':2,'HQ':0.5}[ config_dict['indirect_lighting'] ]
        lightprobe_obj.data.resolution_x = max(2, int(iLx/desired_dist))
        lightprobe_obj.data.resolution_y = max(2, int(iLy/desired_dist))
        lightprobe_obj.data.resolution_z = max(2, int(iLz/desired_dist))
        # Blender 5.x: scene.light_cache_bake moved to object.lightprobe_cache_bake
        # and requires the lightprobe to be the active object with correct override context.
        try:
            bpy.context.view_layer.objects.active = lightprobe_obj
            lightprobe_obj.select_set(True)
            bpy.ops.object.lightprobe_cache_bake()
        except Exception as e:
            print('Warning: lightprobe cache bake skipped (%s)' % e)
        # Reflection probe (SPHERE) for glass / glossy material environment reflection.
        # EEVEE Next removed screen-space reflection; a baked SPHERE lightprobe captures
        # the surrounding scene into a cubemap that transparent and metallic materials
        # can reflect, giving glass realistic environment mirroring instead of a flat look.
        # Probe is placed at scene centre with influence radius covering the whole scene,
        # and clip_end set to the scene's largest dimension so far-away geometry is included.
        try:
            print('Baking reflection probe (SPHERE)...')
            scene_radius = max(iLx, iLy, iLz) * 0.5
            bpy.ops.object.lightprobe_add(type='SPHERE', enter_editmode=False, location=(iMidX,iMidY,iMidZ))
            reflection_probe = bpy.context.object
            # Influence volume: cover whole scene (ellipsoid), with falloff for smooth transition.
            reflection_probe.data.influence_type = 'ELIPSOID'
            reflection_probe.data.influence_distance = scene_radius * 1.2
            reflection_probe.data.falloff = 0.3
            # Clip range: include whole scene bounds (avoid near-plane artefacts on big scenes).
            reflection_probe.data.clip_start = 0.1
            reflection_probe.data.clip_end = max(iLx, iLy, iLz) * 2.0
            # Link to Utils collection (kept alongside the irradiance volume).
            try:
                collection_utils.objects.link(reflection_probe)
                # unlink from default scene collection if linked there
                if scn.collection.objects.get(reflection_probe.name):
                    scn.collection.objects.unlink(reflection_probe)
            except Exception:
                pass
            bpy.context.view_layer.objects.active = reflection_probe
            reflection_probe.select_set(True)
            bpy.ops.object.lightprobe_cache_bake()
            print('Reflection probe baked.')
        except Exception as e:
            print('Warning: reflection probe bake skipped (%s)' % e)
    #
    # done
    #
    print('Finishing scene...')
    return openinblender, config_dict


def get_compositor_ntree():
    '''Blender 5.x: create/assign a CompositorNodeTree via scene.compositing_node_group
    (replaces deprecated scene.use_nodes + scene.node_tree).'''
    scn = bpy.context.scene
    ntree = scn.compositing_node_group
    if ntree is None:
        ntree = bpy.data.node_groups.new("BlendererCompositor", type='CompositorNodeTree')
        scn.compositing_node_group = ntree
    # clear existing nodes
    for node in list(ntree.nodes):
        ntree.nodes.remove(node)
    return ntree


def set_up_backdrop(config_dict, use_bloom=False, bloom_intensity=0.1):
    backdroptype = config_dict['backdroptype']
    if backdroptype == 'None' and not use_bloom:
        return
    if config_dict['backdropimage']:
        backdropimage = config_dict['backdropimage'].replace('file:///' , '')
    else:
        backdropimage = None
    backdropcolor = [float(x) for x in config_dict['backdropcolor'].split(';')]
    while len(backdropcolor) < 4:
        backdropcolor.append(1.0)

    # Blender 5.x: use compositing_node_group instead of scene.node_tree
    node_tree = get_compositor_ntree()
    # create nodes
    render_node = node_tree.nodes.new(type='CompositorNodeRLayers')
    render_node.location = 0,-100
    # Blender 5.x: CompositorNodeComposite removed; use NodeGroupOutput as final output
    output_node = node_tree.nodes.new(type='NodeGroupOutput')
    output_node.location = 900,0
    links = node_tree.links

    # If no backdrop needed, just set up bloom-only chain
    if backdroptype == 'None':
        prev_output = render_node.outputs[0]
        if use_bloom:
            prev_output = add_glare_node(node_tree, links, prev_output, bloom_intensity)
        links.new(prev_output, output_node.inputs[0])
        return

    # Blender 5.x: AlphaOver inputs reordered: [0]=Background, [1]=Foreground, [2]=Factor
    alpha_node = node_tree.nodes.new(type='CompositorNodeAlphaOver')
    alpha_node.location = 500,0
    if backdroptype == 'ColorRGB':
        color_node = node_tree.nodes.new(type='CompositorNodeRGB')
        color_node.outputs[0].default_value = backdropcolor
        color_node.location = 0,100
    elif backdroptype == 'Image':
        color_node = node_tree.nodes.new(type='CompositorNodeImage')
        color_node.location = 0,200
        if backdropimage and os.path.exists(backdropimage):
            texture_img = bpy.data.images.load(backdropimage)
            color_node.image = texture_img
    # Blender 5.x: CompositorNodeScale.space/frame_method removed; use defaults
    scale_node = node_tree.nodes.new(type='CompositorNodeScale')

    # connect nodes with links (AlphaOver: Background=0, Foreground=1, Factor=2)
    links.new(color_node.outputs[0], scale_node.inputs[0])             # color -> scale
    links.new(scale_node.outputs[0], alpha_node.inputs['Background'])  # scaled backdrop -> background
    links.new(render_node.outputs[0], alpha_node.inputs['Foreground']) # render image -> foreground
    links.new(render_node.outputs[1], alpha_node.inputs['Factor'])     # render alpha -> factor
    # optionally add bloom (Glare) between alpha-over and group output
    prev_output = alpha_node.outputs[0]
    if use_bloom:
        prev_output = add_glare_node(node_tree, links, prev_output, bloom_intensity)
    links.new(prev_output, output_node.inputs[0])


def setup_bloom_compositor(bloom_intensity):
    '''Set up a minimal compositor chain for bloom-only (no backdrop).'''
    node_tree = get_compositor_ntree()
    render_node = node_tree.nodes.new(type='CompositorNodeRLayers')
    render_node.location = 0, 0
    output_node = node_tree.nodes.new(type='NodeGroupOutput')
    output_node.location = 600, 0
    links = node_tree.links
    prev_output = add_glare_node(node_tree, links, render_node.outputs[0], bloom_intensity)
    links.new(prev_output, output_node.inputs[0])


def add_glare_node(node_tree, links, from_output, bloom_intensity):
    '''Add a Glare node (FOG_GLOW) to approximate EEVEE bloom. Returns the node's output.
    Blender 5.x: glare_type is now an input ('Type'), not a property.'''
    glare_node = node_tree.nodes.new(type='CompositorNodeGlare')
    # Blender 5.x: glare_type property removed; set via 'Type' input (MENU enum)
    type_input = glare_node.inputs['Type']
    try:
        type_input.default_value = 'FOG_GLOW'
    except (TypeError, ValueError):
        # if string doesn't work, try matching enum item by identifier
        for item in getattr(type_input, 'enum_items', []) or []:
            if item.identifier == 'FOG_GLOW':
                type_input.default_value = item.value
                break
    # Strength and Size are now inputs
    glare_node.inputs['Strength'].default_value = bloom_intensity * 10.0
    glare_node.inputs['Size'].default_value = max(6, int(bloom_intensity * 10))
    links.new(from_output, glare_node.inputs['Image'])
    return glare_node.outputs['Image']


def getChildren(myObject): 
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == myObject: 
            children.append(ob) 
    return children 


def look_at(object_, point):
    loc_object_ = object_.location
    direction = point - loc_object_
    rot_quat = direction.to_track_quat('-Z', 'Y') # point camera -Z axis (Y-vec up)
    object_.rotation_mode = 'QUATERNION'
    object_.rotation_quaternion = rot_quat


def createLampEevee(lampname, location, lamptype, object_data, material_version='OLD'):
    scene = bpy.context.scene
    lamp_data = bpy.data.lights.new(name=lampname, type=lamptype)
    rgb = object_data[0]
    strength = object_data[1]
    rgb = tuple([x/255.0 for x in rgb])
    lamp_data.color = rgb
    if material_version == 'NEW':
        # Physical unit correspondence: VC light strength -> Blender energy.
        # Point/Spot/Area are power in Watts (1:1 with VC strength).
        # Sun is irradiance in W/m^2 (VC strength / 100, typical VC 500 -> 5 W/m^2).
        if lamptype == 'SUN':
            lamp_data.energy = strength / 100.0
        else:
            lamp_data.energy = strength
    else:
        lamp_data.energy = strength
    # Blender 5.x: use_contact_shadow/contact_shadow_*/shadow_buffer_bias removed

    if lamptype == 'AREA':
        lamp_data.shape = 'RECTANGLE'
        lamp_data.size = object_data[2]
        lamp_data.size_y = object_data[3]
    elif lamptype in ['SPOT']:
        size = object_data[2]
        lamp_data.spot_size = radians(object_data[3])
    elif lamptype in ['POINT']:
        size = object_data[2]
        lamp_data.shadow_soft_size = float(size)
        lamp_data.use_shadow = True
    elif lamptype == 'SUN' and len(object_data) > 3:
        lamp_data.angle = radians(object_data[3])
    lamp_object = bpy.data.objects.new(name=lampname, object_data=lamp_data)
    lamp_object.location = location[1:4]
    point = mathutils.Vector((location[4], location[5], location[6]))
    look_at(lamp_object, point)
    return lamp_object




def clearScene(re_render):
    if re_render:
        # CLEAR just lights and camera
        for bpy_data_iter in (
                bpy.data.lights,
                bpy.data.cameras,
                            ):
            for id_data in bpy_data_iter:
                bpy_data_iter.remove(id_data)
    else:
        # CLEAR complete scene
        for bpy_data_iter in (
                bpy.data.objects,
                bpy.data.meshes,
                bpy.data.lights,
                bpy.data.collections,
                bpy.data.cameras,
                            ):
            for id_data in bpy_data_iter:
                bpy_data_iter.remove(id_data)


##########################################
############# OBJ IMPORTING ##############
##########################################
import bpy, os
class ObjGroup:
    def __init__(self,name):
        self.Name = name
        self.MaterialName = ""
        self.Faces = []
        self.TextureCoords = []
        self.TextureCoordsFlat = []
        self.Verts = []

class ObjMaterial:
    def __init__(self,name):
        self.Name = name
        self.Opacity = 1.0
        self.Color = 0.0, 0.0, 0.0
        self.ColorMap = ''
        self.Emission = 0.0
        self.EmissionColor = 0.0, 0.0, 0.0
        self.Specular = 0.0, 0.0, 0.0
        self.Ambient = 0.0, 0.0, 0.0
        self.Metallic = 0.0
        self.Roughness = 0.0
        self.NormalMap = ''
        self.Bumpiness = 0.0
        self.Clearcoat = 0.0
        self.ClearcoatRougness = 0.0
        self.Style = 'N/A'
        #self.ProceduralDisplacement = 'N/A'
        #self.DisplacementValue = 5.0
        #self.DisplacementScale = 5.0

def stripNonAscii(s):
    ss = ""
    for c in s:
        if ord(c) <128:
            ss += c
    return ss


def loadMAT(filename):
    materials = {}
    DIR = os.path.dirname(filename)
    material_name = 'OBJ_import_material'
    current_mat = None
    if not os.path.isfile(filename):
        print('Warning: material file not found: %s (using default materials)' % filename)
        return materials
    with open(filename, "r", encoding='utf8') as mtlfile:
        for line in mtlfile:
            #line = stripNonAscii(line.strip())
            line = line.strip()
            if not line or line[0] == '#':
                # skip empty or comment lines
                continue
            vals = line.split()
            line_id = vals[0].lower()
            if line_id == "newmtl":
                material_name = ' '.join(vals[1:]).strip(',.-#')
                if material_name not in materials:
                    materials[material_name] = ObjMaterial(material_name)
                current_mat = materials[material_name]
            elif line_id == 'kd':
                current_mat.Color = (float(vals[1]), float(vals[2]), float(vals[3]))
            elif line_id == 'ks':
                current_mat.Specular = (float(vals[1]), float(vals[2]), float(vals[3]))
            elif line_id == 'ka':
                current_mat.Ambient = (float(vals[1]), float(vals[2]), float(vals[3]))
            elif line_id == 'ke':
                current_mat.Emission = float(vals[1])
            elif line_id == 'd':  # dissolve (transparency)
                current_mat.Opacity = float(vals[1])
            elif line_id == 'bumpiness':  
                current_mat.Bumpiness = float(vals[1])
            elif line_id == 'clearcoat': 
                current_mat.Clearcoat = float(vals[1])
            elif line_id == 'roughness':  
                current_mat.Roughness = float(vals[1])
            elif line_id == 'metallic':  
                current_mat.Metallic = float(vals[1])
            elif line_id == 'map_kd':
                current_mat.ColorMap = os.path.join(str(DIR), vals[1] )
            elif line_id == 'map_bump':
                current_mat.NormalMap = os.path.join(str(DIR), vals[1] )
            elif line_id == 'style':
                current_mat.Style = vals[1]
    return materials


def loadOBJ(filename):
    global matData
    groups = {}
    group_name = os.path.splitext(os.path.basename(filename))[0]
    verts = []  
    texts = []
    vindex = 0
    mtllib = ""
    base_group_name = group_name
    currentline = 0
    prev_verts_count = 0
    #with open(filename, "r", encoding='latin-1') as objfile:
    with open(filename, "r", encoding='utf8') as objfile:
        for line in objfile:
            currentline+=1
            #line = stripNonAscii(line.strip())
            line = line.strip()
            if not line or line[0] == '#':
                # skip empty or comment lines
                continue
            vals = line.split() 
            if vals[0] == "mtllib":
                mtllib = ' '.join(vals[1:])
            if vals[0] == "v":
                # vertices
                v = tuple(map(float, vals[1:4]))
                verts.append(v)
            if vals[0] == "vt":
                # vertex texture coordinates
                t = tuple(map(float, vals[1:3])) # use only 2 coordinates (u,v)
                texts.append(t) #e.g. texts.append( (0.175, 0.791) )
            if vals[0] == "g":
                group_name = ' '.join(vals[1:])
                if group_name not in groups:
                    groups[group_name] = ObjGroup(group_name) 
                groups[group_name].Verts = verts[:]
                groups[group_name].TextureCoords = texts[:]
                vindex += prev_verts_count
                prev_verts_count = len(verts[:])
                verts = []
                texts = []
                base_group_name = group_name
            if vals[0] == "usemtl":
                matname = ' '.join(vals[1:]).strip(',.-#')
                #group_name = base_group_name + '_' + matname
                #if group_name not in groups:
                #    groups[group_name] = ObjGroup(group_name) 
                groups[group_name].MaterialName = matname
            if vals[0] == "f":
                face = []
                text = []
                # FACE
                for f in vals[1:]:  
                    w = f.split("/")  
                    # FACE VERTEX
                    try:face.append( int(w[0])-1-vindex ) # obj indexing starts from 1
                    except:
                        print(currentline,'<= on line. Error: vertex indexing', len(verts), [int(w[0])-1-vindex])
                        return
                    # FACE TEXTURE COORDINATE
                    # try:     text.append( texts[int(w[1])-1-tindex] )
                    # try:     groups[group_name].TextureCoordsFlat.extend( groups[group_name].TextureCoords[int(w[1])-1] )
                    # except:  groups[group_name].TextureCoordsFlat.extend( [0,0] )
                    try:text.extend( groups[group_name].TextureCoords[int(w[1])-1-vindex] )
                    except:
                        print(currentline,'<= on line. Error: vertex indexing', len(verts), [int(w[0])-1-vindex])
                        return
                # ADD FACE TO THIS GROUP 
                groups[group_name].Faces.append(face)  #(groups ~ dictionary)
                groups[group_name].TextureCoordsFlat.extend(text)
    if verts and group_name in groups:
        # store previous group's verts
        groups[group_name].Verts = verts[:]
        verts = []
    # remove if there are any empty groups
    emptygroups = []
    for g in groups.keys():
        if not groups[g].Faces:
            emptygroups.append(g)
    for e in emptygroups:
        del groups[e]
    return groups#, texts

EMPTY_TYPE = None
import numpy as np
def loadmodel(filename, name, blender_materials, collection):
    #basename, extension = os.path.splitext(os.path.basename(filename))
    items = loadOBJ(filename) 
    empty_object = bpy.data.objects.new( name, EMPTY_TYPE )
    collection.objects.link(empty_object)
    for item_name in items:
        item = items[item_name]
        mat = blender_materials.get(item.MaterialName)
        read_mesh(  empty_object,
                        collection,
                        item_name, 
                        item.Verts, 
                        item.Faces, 
                        item.TextureCoordsFlat,
                        mat)
    return empty_object


def read_mesh(  parent_object,
                collection,
                item_name, 
                vertices, 
                faces, 
                text_coords,
                material):
    # rint('-'*99)
    # rint(item_name)
    # rint('vertices',len(vertices),vertices)
    # rint('text_coords',len(text_coords),text_coords)
    mesh_data = bpy.data.meshes.new(item_name)
    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update(calc_edges=False)
    scene_object = bpy.data.objects.new(item_name, mesh_data)
    scene_object.parent = parent_object
    collection.objects.link(scene_object)
    scene_object.data.materials.append(material)
    scene_object.data.polygons.foreach_set("use_smooth", [True]*len(scene_object.data.polygons))
    # UV
    uv = scene_object.data.uv_layers.active
    if uv is None:
        uv = scene_object.data.uv_layers.new(name="UVMap")
    uv.data.foreach_set("uv", text_coords)

##########################################
############# OBJ IMPORTING funcs end ####
##########################################
def convertToVideo(file_sequence, filepathroot, config_dict):
    # Merge the PNG frames already rendered into Picture_frames into a single
    # MP4 video file using Blender's Video Sequence Editor + FFMPEG.
    #
    # Blender 5.2 LTS changed the movie-output API: setting
    #   image_settings.file_format = 'FFMPEG'
    # is rejected in --background mode (the enum is filtered at runtime).
    # The new, correct entry point is:
    #   image_settings.media_type = 'VIDEO'
    # which works in BOTH background and GUI mode, sets file_format to FFMPEG
    # internally, and flips render.is_movie_format to True.
    #
    # The PNG frames in file_sequence are reused directly as VSE image strips —
    # no re-rendering and no extra "_video_frames" folder is created.
    #
    # VIDEO ENCODING PHASE: 3D rendering is complete. Unlock CPU affinity
    # (from the 5-core GPU-support limit used during 3D rendering) and switch
    # Blender render threads to AUTO, so libx264 can use every logical core
    # for parallel slice encoding. This cuts encoding wall-clock encode time
    # ~2-4x on multi-core CPUs while leaving the SAME visual output identical.
    reset_cpu_affinity()
    scn = bpy.context.scene
    # Preserve old thread settings, restore on exit (in case this Blender
    # instance stays alive, e.g. Open-in-Blender mode).
    old_threads_mode = scn.render.threads_mode
    old_threads      = scn.render.threads
    scn.render.threads_mode = 'AUTO'
    try:
        seq_editor = scn.sequence_editor
        if seq_editor is None:
            scn.sequence_editor_create()
            seq_editor = scn.sequence_editor
        for i, uri in enumerate( file_sequence ):
            # unique strip name per frame (Blender auto-renames duplicates, but be explicit)
            seq_editor.strips.new_image( 'frame_%05d' % i, uri, 2, i )
        scn.frame_start = 0
        scn.frame_end = len(file_sequence) - 1 if file_sequence else 0
        scn.render.resolution_x = int(config_dict['resolution_x'])
        scn.render.resolution_y = int(config_dict['resolution_y'])
        scn.render.resolution_percentage = 100
        # Render the sequencer output (the PNG strips), NOT the 3D scene again.
        scn.render.use_sequencer = True
        scn.render.use_compositing = False
        video_uri = filepathroot + '.mp4'
        video_uri = auto_increment_filename(video_uri)
        temporary = render_destination(video_uri)
        scn.render.filepath = temporary
        scn.render.image_settings.media_type = 'VIDEO'
        # MP4 container (MPEG4 format) + H.264 codec: best compression & compatibility
        scn.render.ffmpeg.format = 'MPEG4'
        scn.render.ffmpeg.codec = 'H264'
        # Apply user-selected video quality (same scale as DIRECT_VIDEO mode).
        video_quality = config_dict.get('video_quality') or 'High'
        if video_quality == 'Lossless':
            scn.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
            scn.render.ffmpeg.ffmpeg_preset = 'BEST'
        elif video_quality == 'Low':
            scn.render.ffmpeg.constant_rate_factor = 'LOW'
            scn.render.ffmpeg.ffmpeg_preset = 'GOOD'
        else:
            scn.render.ffmpeg.constant_rate_factor = 'HIGH'
            scn.render.ffmpeg.ffmpeg_preset = 'GOOD'
        result = render_animation_with_progress('encode', len(file_sequence))
        require_rendered_file(result, temporary)
        return video_uri, temporary
    finally:
        scn.render.threads_mode = old_threads_mode
        scn.render.threads      = old_threads


def render_direct_video(filepathroot, config_dict):
    # Render the animation directly to an MP4 video file with NO PNG
    # intermediate frames on disk. Blender 5.2 supports this in both GUI and
    # --background mode via image_settings.media_type='VIDEO' (which flips
    # render.is_movie_format to True and routes the output through FFMPEG).
    #
    # Video quality is controlled by config_dict['video_quality']:
    #   'Lossless'    : perceptually lossless (CRF ~0, very large files)
    #   'High'        : high quality (CRF ~18, balanced size/quality)  [default]
    #   'Low'         : low quality / small file (CRF ~28)
    # These settings apply only to video rendering.
    #
    # Encoding phase: 3D scene prep is done, so unlock CPU affinity (from the
    # 5-core GPU-support limit set during do_import_vc) and switch Blender
    # render threads to AUTO so libx264 can use every logical core.
    reset_cpu_affinity()
    scn = bpy.context.scene
    old_threads_mode = scn.render.threads_mode
    old_threads      = scn.render.threads
    old_use_seq      = scn.render.use_sequencer
    old_use_comp     = scn.render.use_compositing
    old_media_type   = scn.render.image_settings.media_type
    scn.render.threads_mode = 'AUTO'
    try:
        video_uri = filepathroot + '.mp4'
        video_uri = auto_increment_filename(video_uri)
        temporary = render_destination(video_uri)
        scn.render.filepath = temporary
        scn.render.resolution_percentage = 100
        # Render the 3D scene directly to video (no PNG intermediates).
        scn.render.use_sequencer = False
        scn.render.use_compositing = True
        scn.render.image_settings.media_type = 'VIDEO'
        # MP4 container (MPEG4 format) + H.264 codec
        scn.render.ffmpeg.format = 'MPEG4'
        scn.render.ffmpeg.codec = 'H264'
        # H.264 supports both CRF (quality) and max-bitrate modes.
        # Use CRF for all quality levels; enable max-bitrate only for Low.
        scn.render.ffmpeg.use_lossless_output = False
        # config_dict['video_quality'] may be None if the XML element was empty;
        # normalize to 'High' (the default) in that case.
        video_quality = config_dict.get('video_quality') or 'High'
        if video_quality == 'Lossless':
            # Perceptually lossless (CRF ~18 is visually indistinguishable
            # from source). Use BEST preset (slowest, best compression).
            scn.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
            scn.render.ffmpeg.ffmpeg_preset = 'BEST'
        elif video_quality == 'Low':
            # Low quality / small file. GOOD preset balances speed/size.
            scn.render.ffmpeg.constant_rate_factor = 'LOW'
            scn.render.ffmpeg.ffmpeg_preset = 'GOOD'
        else:
            # 'High' (default)
            scn.render.ffmpeg.constant_rate_factor = 'HIGH'
            scn.render.ffmpeg.ffmpeg_preset = 'GOOD'
        result = render_animation_with_progress('render', scn.frame_end - scn.frame_start + 1)
        require_rendered_file(result, temporary)
        return video_uri, temporary
    finally:
        scn.render.threads_mode = old_threads_mode
        scn.render.threads      = old_threads
        scn.render.use_sequencer = old_use_seq
        scn.render.use_compositing = old_use_comp
        scn.render.image_settings.media_type = old_media_type


import webbrowser
def main():
    profiler_in = time.perf_counter()
    try:
        write_render_progress('prepare')
        openinblender, config_dict = do_import_vc()
        frameS = bpy.context.scene.frame_start
        frameE = bpy.context.scene.frame_end
        frames = frameE - frameS + 1
        fps = bpy.context.scene.render.fps
        is_animation = config_dict.get('is_animation', '1' if frames > 1 else '0') == '1'
        filepathroot, file_extension = os.path.splitext(bpy.context.scene.render.filepath)
        save_file_uri = os.path.join(uri_root, 'blender_scene.blend' )
        saved = bpy.ops.wm.save_as_mainfile(filepath=save_file_uri)
        if openinblender:
            write_export_result('scene', require_rendered_file(saved, save_file_uri))
        else:
            if not is_animation:
                bpy.context.scene.frame_set( 0 )
                image_uri = auto_increment_filename(bpy.context.scene.render.filepath)
                temporary = render_destination(image_uri)
                bpy.context.scene.render.filepath = temporary
                write_render_progress('render', 0, 1)
                rendered = bpy.ops.render.render( write_still=True )
                require_rendered_file(rendered, temporary)
                if result_path:
                    write_export_result('image', image_uri, temporary=temporary)
                else:
                    webbrowser.open(image_uri)
            else:
                # Video mode. Two rendering strategies are available; the choice
                # is driven by config_dict['video_mode']:
                #   'PNG_SEQUENCE' : render each frame to PNG (Picture_frames),
                #                    then merge them via the VSE + FFMPEG.
                #   'DIRECT_VIDEO' : render the animation straight to a video
                #                    file (no PNG intermediates on disk).
                video_mode = config_dict.get('video_mode') or 'PNG_SEQUENCE'
                if video_mode == 'DIRECT_VIDEO':
                    video_uri, temporary = render_direct_video(filepathroot, config_dict)
                    write_export_result('video', video_uri, frames=frames, fps=fps, temporary=temporary)
                else:
                    file_sequence = []
                    froot, fname = os.path.split(filepathroot)
                    # Reserve a fresh folder so another render cannot overwrite earlier frames.
                    frames_dir = create_frame_output_folder(froot)
                    if result_path:
                        with open(result_path + '.frames.tmp', 'w', encoding='utf-8') as stream:
                            json.dump({'path': frames_dir}, stream)
                        os.replace(result_path + '.frames.tmp', result_path + '.frames')
                    # Iterate from frame_start to frame_end INCLUSIVE.
                    # The old `range(frameCount)` stopped at frame_end-1, dropping the last frame.
                    # In long recordings (>2 min) the last frame is essential to capture the
                    # final state of the animation, so we add +1 here.
                    write_render_progress('render', 0, frames)
                    last_update = 0.0
                    for i in range(frameS, frameE + 1):
                        bpy.context.scene.frame_set( i )
                        i_filename = os.path.join(frames_dir, fname+str(i)+file_extension)
                        file_sequence.append( i_filename )
                        temporary = render_destination(i_filename, froot)
                        bpy.context.scene.render.filepath = temporary
                        rendered = bpy.ops.render.render( write_still=True )
                        publish_rendered_file(rendered, temporary, i_filename)
                        now = time.monotonic()
                        if i == frameE or now - last_update >= 0.25:
                            write_render_progress('render', i - frameS + 1, frames)
                            last_update = now
                    bpy.context.scene.view_settings.exposure = 0.0
                    try:
                        video_uri, temporary = convertToVideo(file_sequence, filepathroot, config_dict)
                    except Exception as error:
                        print('Warning: video encoding failed (%s).' % error)
                        print('PNG image sequence is available in:', frames_dir)
                        write_export_result('frames_only', frames_dir, str(error))
                    else:
                        write_export_result('video', video_uri, frames=frames, fps=fps, temporary=temporary)
        write_render_progress('finishing')
        profiler_out = time.perf_counter()
        print('Total Blender time:', round((profiler_out - profiler_in), 3), "s")
    except Exception as e:
        import traceback
        traceback.print_exc()
        write_export_result('failed', detail=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()



