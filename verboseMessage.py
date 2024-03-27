class VerboseMessage:
	def __init__(self, text="") -> None:
		self.text = text

	def add(self, s="", start="", end="\n") -> None:
		if s.strip() == '' and len(self.text) > 0 and self.text.strip(' ')[-1] == '\n':
			return
		self.text += start + s + end

	def clear(self):
		self.text = ''

	def get_text(self) -> str:
		return self.text
	
	def __str__(self) -> str:
		return self.get_text()
