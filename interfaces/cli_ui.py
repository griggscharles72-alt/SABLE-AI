# interfaces/cli_ui.py
def run_command(command):
    return {"executed": command, "status": "ok"}

def start_cli():
    print("CLI Interface Started")
    return {"status": "cli running"}

if __name__ == "__main__":
    print(start_cli())
    print(run_command("doctor.status"))
