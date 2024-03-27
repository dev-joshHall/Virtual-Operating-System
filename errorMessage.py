class ErrorMessage:
	def __init__(self, type: str, message: str) -> None:
		self.type = type
		self.message = message

	def __str__(self):
		return f'{self.type}: {self.message}'