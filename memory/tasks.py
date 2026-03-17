TASKS = []

def add_task(name, status="pending"):
    TASKS.append({"name": name, "status": status})
    return TASKS[-1]

def list_tasks():
    return TASKS

if __name__ == "__main__":
    add_task("Initialize system")
    add_task("Run diagnostics")
    print(list_tasks())
