class Clock:
	def __init__(self, value: int=0) -> None:
		self.value: int = value

	def tick(self) -> int:
		self.value += 1
		return self.value

	def get_value(self) -> int:
		return self.value
	
	def reset(self) -> None:
		self.value = 0
