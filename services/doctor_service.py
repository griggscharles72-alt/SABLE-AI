# services/doctor_service.py
def scan():
    return {"status": "scan complete", "issues": []}

def status():
    return {"status": "operational"}

if __name__ == "__main__":
    print(scan())
    print(status())
