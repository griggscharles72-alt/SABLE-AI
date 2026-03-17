class Persona:
    def __init__(self, name="SABLE", style="neutral", voice="default"):
        self.name = name
        self.style = style
        self.voice = voice
        self.memory = {}

    def remember(self, key, value):
        self.memory[key] = value

    def recall(self, key):
        return self.memory.get(key, None)

if __name__ == "__main__":
    p = Persona()
    p.remember("favorite_tool", "system_info")
    print(f"Memory: {p.memory}")
