# interfaces/ai_interface.py
def query_ai(prompt):
    return {"prompt": prompt, "response": "AI placeholder response"}

def start_ai_loop():
    print("AI interface started")
    return {"status": "ai running"}

if __name__ == "__main__":
    print(start_ai_loop())
    print(query_ai("run doctor.status"))
