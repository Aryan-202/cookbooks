import psutil
import subprocess
import os
import re
import threading
import time

try:
    import GPUtil
    _GPUTIL_AVAILABLE = True
except ImportError:
    _GPUTIL_AVAILABLE = False


class ResourceMonitor:
    @staticmethod
    def get_cpu_usage():
        """Returns the current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.1)

    @staticmethod
    def get_ram_usage():
        """Returns the current RAM usage percentage."""
        return psutil.virtual_memory().percent

    @staticmethod
    def _parse_nvidia_smi():
        """Fallback parser for nvidia-smi if GPUtil fails on Windows."""
        paths = [
            "nvidia-smi",
            r"C:\Windows\System32\nvidia-smi.exe",
            r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
        ]
        
        for path in paths:
            try:
                result = subprocess.run(
                    [path, "--query-gpu=utilization.gpu,utilization.memory", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output:
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
        Returns GPU metrics by sampling a short window (0.3s) to catch recent activity.
        """
        samples_usage = []
        samples_mem = []
        
        for _ in range(3):
            u, m = None, None
            if _GPUTIL_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        u = round(gpus[0].load * 100, 1)
                        m = round(gpus[0].memoryUtil * 100, 1)
                except Exception:
                    pass
            
            if u is None:
                u, m = ResourceMonitor._parse_nvidia_smi()
            
            if u is not None:
                samples_usage.append(u)
                samples_mem.append(m)
            
            time.sleep(0.1)

        if not samples_usage:
            return None, None
            
        return max(samples_usage), max(samples_mem)

    @staticmethod
    def get_all_metrics():
        cpu = ResourceMonitor.get_cpu_usage()
        ram = ResourceMonitor.get_ram_usage()
        gpu_usage, gpu_memory = ResourceMonitor.get_gpu_metrics()
        return {
            "cpu": cpu,
            "ram": ram,
            "gpu_usage": gpu_usage,
            "gpu_memory": gpu_memory,
        }

class TelemetryMonitor(threading.Thread):
    """
    Background thread to monitor resource usage during a task and provide AVERAGES
    to avoid telemetry lag or impossible efficiency spikes.
    """
    def __init__(self, interval=0.1):
        super().__init__(daemon=True)
        self.interval = interval
        self.running = False
        
        self.cpu_samples = []
        self.gpu_samples = []
        self.gmem_samples = []

    def run(self):
        self.running = True
        while self.running:
            metrics = ResourceMonitor.get_all_metrics()
            self.cpu_samples.append(metrics["cpu"])
            if metrics["gpu_usage"] is not None:
                self.gpu_samples.append(metrics["gpu_usage"])
                self.gmem_samples.append(metrics["gpu_memory"])
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        
        def safe_avg(samples):
            if not samples: return None
            return round(sum(samples) / len(samples), 1)

        return {
            "avg_cpu": safe_avg(self.cpu_samples),
            "avg_gpu": safe_avg(self.gpu_samples),
            "avg_gmem": safe_avg(self.gmem_samples)
        }
