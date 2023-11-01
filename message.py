class Message:
    def __init__(self, role, content, citations=None):
        self.role = role
        self.content = content
        self.citations = citations

    def openai_format(self):
        return {"role": self.role, "content": self.content}