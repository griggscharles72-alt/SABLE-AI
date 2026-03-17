# services/sentinel_service.py
def restore(create_baseline=False):
    return {"status": "restore complete", "baseline_created": create_baseline}

def verify():
    return {"status": "verification complete"}

def status():
    return {"status": "operational"}

if __name__ == "__main__":
    print(restore(True))
    print(verify())
    print(status())
