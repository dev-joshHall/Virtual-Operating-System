from math import ceil

class PageTable:
	def __init__(self, op_sys) -> None:
		self.items: dict = {}
		self.op_sys = op_sys

	def add_process(self, p):
		page_start: int = p.pcb.memory_l_limit // self.op_sys.page_size
		page_end: int = ceil(p.pcb.memory_u_limit / self.op_sys.page_size)
		for page in range(page_start, page_end + 1):
			self.items[page] = p

	def remove_process(self, p):
		page_start: int = p.pcb.memory_l_limit // self.op_sys.page_size
		page_end: int = ceil(p.pcb.memory_u_limit / self.op_sys.page_size)
		for page in range(page_start, page_end + 1):
			if page in self.items:
				self.items.pop(page)
	
	def __str__(self) -> str:
		result = 'PageTable('
		if self.items:
			result += '\n'
		for page in range(max(list(self.items.keys()))):
			if page in self.items:
				result += f'\tPage {page} = "{self.items[page].p_id}"\n'
			else:
				result += f'\tPage {page} = EMPTY'
		result += ')'
