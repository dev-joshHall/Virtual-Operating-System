class OsxFileDetails:
	def __init__(self, byte_size: int, pc: int, loader: int, starting_loader: int) -> None:
		self.byte_size = byte_size
		self.pc = pc
		self.loader = loader
		self.starting_loader = starting_loader

	def __str__(self) -> str:
		return f'OsxFileDetails(byte_size={self.byte_size}, pc={self.pc}, loader={self.loader})'
