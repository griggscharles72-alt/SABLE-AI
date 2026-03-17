# services/device_lab_service.py
def check():
    return {"status": "device check complete"}

def status():
    return {"status": "operational"}

if __name__ == "__main__":
    print(check())
    print(status())
