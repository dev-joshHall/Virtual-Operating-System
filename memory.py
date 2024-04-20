from colorama import Fore, Back

class Memory:
	def __init__(self, process) -> None:
		# main memory is x*6
		# store the whole program together to make it easier
		# [
		#     (row0) [b'x00', '...', '...', '...', '...', '...'],
		#     (row1) [...]
		#     ...
		# ]
		self.page_count = 0
		self.main_memory = [[b'\x00' for x in range(6)] for y in range(100)]
		self.next_location = [0, 0] # location to add next byte in memory (r,c)
		self.process = process

	def load_6bytes(self, six_bytes: bytes, location: int=None) -> None:
		if location is None:
			location = self.get_loader()
		else:
			self.set_loader(location)
		row_number = self.get_row(location)
		# double main memory if running out of space
		l = len(self.main_memory)
		if row_number >= l - 2:
			for _ in range(l):
				self.main_memory.append([b'\x00' for x in range(6)])
		self.main_memory[row_number] = [int.to_bytes(i) for i in six_bytes]
		self.set_loader(self.get_loader() + 6)

	def double_size(self) -> None:
		l = len(self.main_memory)
		for _ in range(l):
			self.main_memory.append([b'\x00' for x in range(6)])

	def fetch_6bytes(self, location: int=None) -> list:
		if location is not None:
			self.set_pc(location)
		self.get_pc()
		return self.main_memory[self.get_row()]
	
	def set_loader(self, location: int) -> None:
		self.process.file_details.loader = location

	def get_loader(self) -> int:
		return self.process.file_details.loader
		
	def set_pc(self, location: int) -> None:
		self.process.registers.pc(location)
		self.get_pc()

	def get_pc(self) -> int:
		self.next_location[0] = self.process.registers.pc() // 6
		self.next_location[1] = self.process.registers.pc() % 6
		return self.process.registers.pc()

	def get_location(self) -> int:
		self.get_pc()
		return 6 * self.next_location[0] + self.next_location[1]
	
	def get_row(self, location: int=None) -> int:
		if location is None:
			location = self.get_location()
		row = None
		# if location is evenly divisible my 6
		if location % 6 == 0:
			# go to exact location
			row = location // 6
		else:
			# go to next empty row
			row = (location // 6) + 1
		return row
	
	def dump(self, verbose=False) -> None:
		print(Fore.BLUE, end='')
		counter = 0
		for row in self.main_memory:
			page_number: int = self.get_page_number(counter)
			if len(list(filter(lambda i: i != b'\x00', row))) > 0:
				print(Back.WHITE, end='')
			print(f'(Page={page_number}, Addr={counter}, FreePage={self.page_is_free(page_number)})', end='\t')
			print(row)
			print(Back.RESET, end='')
			counter += 6
		print(self.process.registers)
		print(f'mode = {self.process.shell.mode}')
		print(f'terminated processes: {len(self.process.op_sys.terminated_items)}')
		for p in self.process.op_sys.terminated_items:
			print('\t' + str(p))
		print(f'Total Pages:\t{self.get_page_count()}')
		print(f'Free Pages:\t{self.get_free_pages()}')
		print(f'Ocupied Pages:\t{self.get_full_pages()}')

	def row_is_empty(self, r: int) -> bool:
		row = self.main_memory[r]
		for n in row:
			if int.from_bytes(n) != 0:
				return False
		return True

	def is_free(self, lower_bound: int, upper_bound: int) -> bool:
		for i in range(lower_bound, upper_bound + 1):
			if not self.row_is_empty(self.get_row(i)):
				return False
		return True
	
	def clean(self, lower_bound: int, upper_bound: int) -> None:
		if self.is_free(lower_bound, upper_bound):
			return
		for i in range(lower_bound, upper_bound):
			self.main_memory[self.get_row(i)] = [b'\x00' for x in range(6)]

	def page_is_free(self, p_number: int) -> bool:
		page_start: int = p_number * self.process.op_sys.page_size
		page_end: int = page_start + self.process.op_sys.page_size
		try:
			return self.is_free(page_start, page_end - 6)
		except IndexError:
			return True
	
	def get_page_number(self, addr: int) -> int:
		return addr // self.process.op_sys.page_size

	def get_free_pages(self) -> int:
		free: int = 0
		self.page_count = 0
		for page in range(0, ((len(self.main_memory) * 6) // self.process.op_sys.page_size) + 1):
			self.page_count += 1
			if self.page_is_free(page):
				free += 1
		return free

	def get_full_pages(self) -> int:
		return self.get_page_count() - self.get_free_pages()

	def get_page_count(self) -> int:
		self.get_free_pages()
		return self.page_count
