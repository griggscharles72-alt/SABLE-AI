import platform
import psutil

def get_system_info():
    return {
        "platform": platform.platform(),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
    }

if __name__ == "__main__":
    info = get_system_info()
    for k, v in info.items():
        print(f"{k}: {v}")
