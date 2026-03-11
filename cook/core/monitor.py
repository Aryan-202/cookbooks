"""
System resource monitoring utilities
"""
import psutil
import time

class ResourceMonitor:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def get_cpu_usage():
        """Returns the current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.5)
    
    @staticmethod
    def get_ram_usage():
        """Returns the current RAM usage percentage."""
        return psutil.virtual_memory().percent
    
    @staticmethod
    def get_system_stats():
        """Returns comprehensive system stats"""
        return {
            "cpu": psutil.cpu_percent(interval=0.5),
            "cpu_count": psutil.cpu_count(),
            "ram": psutil.virtual_memory().percent,
            "ram_available": psutil.virtual_memory().available // (1024**2),  # MB
            "ram_total": psutil.virtual_memory().total // (1024**2),  # MB
            "disk": psutil.disk_usage('/').percent,
            "timestamp": time.time()
        }
    
    @staticmethod
    def monitor_resources(duration=10, interval=1):
        """Monitor resources over time"""
        stats = []
        for _ in range(int(duration / interval)):
            stats.append(ResourceMonitor.get_system_stats())
            time.sleep(interval)
        return stats