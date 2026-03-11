import psutil
import subprocess
import os
import re

try:
    import GPUtil
    _GPUTIL_AVAILABLE = True
except ImportError:
    _GPUTIL_AVAILABLE = False


class ResourceMonitor:
    @staticmethod
    def get_cpu_usage():
        """Returns the current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.5)

    @staticmethod
    def get_ram_usage():
        """Returns the current RAM usage percentage."""
        return psutil.virtual_memory().percent

    @staticmethod
    def _parse_nvidia_smi():
        """
        Fallback parser for nvidia-smi if GPUtil fails on Windows.
        """
        # Common locations for nvidia-smi on Windows if not in PATH
        paths = [
            "nvidia-smi", # If in PATH
            r"C:\Windows\System32\nvidia-smi.exe",
            r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
        ]
        
        for path in paths:
            try:
                # Run nvidia-smi with query flag for usage and memory
                # util.gpu [%], util.memory [%]
                result = subprocess.run(
                    [path, "--query-gpu=utilization.gpu,utilization.memory", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output:
                        # Format is often "0, 0"
                        parts = output.split(",")
                        if len(parts) >= 2:
                            usage = float(parts[0].strip())
                            memory = float(parts[1].strip())
                            return usage, memory
            except Exception:
                continue
        return None, None

    @staticmethod
    def get_gpu_metrics():
        """
        Returns GPU utilization (%) and GPU memory usage (%) for the first GPU.
        Returns (None, None) if no GPU is detected.
        """
        # 1. Try GPUtil first
        if _GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_usage = round(gpus[0].load * 100, 1)
                    gpu_memory = round(gpus[0].memoryUtil * 100, 1)
                    return gpu_usage, gpu_memory
            except Exception:
                pass
        
        # 2. Try Fallback for Windows/Binary
        return ResourceMonitor._parse_nvidia_smi()

    @staticmethod
    def get_all_metrics():
        """
        Convenience method — returns a dict with cpu, ram, gpu_usage, gpu_memory.
        gpu_usage / gpu_memory are None when no GPU is available.
        """
        cpu = ResourceMonitor.get_cpu_usage()
        ram = ResourceMonitor.get_ram_usage()
        gpu_usage, gpu_memory = ResourceMonitor.get_gpu_metrics()
        return {
            "cpu": cpu,
            "ram": ram,
            "gpu_usage": gpu_usage,
            "gpu_memory": gpu_memory,
        }
