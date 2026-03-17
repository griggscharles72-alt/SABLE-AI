# services/traffic_service.py
def start():
    return {"status": "traffic monitoring started"}

def stop():
    return {"status": "traffic monitoring stopped"}

def status():
    return {"status": "operational"}

if __name__ == "__main__":
    print(start())
    print(status())
    print(stop())
