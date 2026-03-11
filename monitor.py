import psutil

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
    def get_gpu_metrics():
        """
        Returns GPU utilization (%) and GPU memory usage (%) for the first GPU.
        Returns (None, None) if no GPU is detected or GPUtil is not installed.
        """
        if not _GPUTIL_AVAILABLE:
            return None, None
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = round(gpus[0].load * 100, 1)
                gpu_memory = round(gpus[0].memoryUtil * 100, 1)
                return gpu_usage, gpu_memory
        except Exception:
            pass
        return None, None

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
