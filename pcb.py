# PCB is for M2
class PCB:
	states = {
		0: 'new',
		1: 'ready',
		2: 'running',
		3: 'waiting',
		4: 'terminated'
	}

	def __init__(self, f_name: str, state: int, p_number: int, pc: int, memory_u_limit: int, memory_l_limit: int, open_files: list) -> None:
		self.f_name = f_name
		self.state = state
		self.p_number = p_number
		self.pc = pc
		self.memory_u_limit = memory_u_limit
		self.memory_l_limit = memory_l_limit
		self.open_files = [x for x in open_files] # shallow copy
		self.regiters: dict = {}

	def is_at(self, loc: int) -> bool:
		if loc >= self.memory_u_limit and loc <= self.memory_u_limit + 7:
			return True
		return False

	def new(self):
		self.state = 0

	def ready(self):
		self.state = 1

	def running(self):
		self.state = 2

	def waiting(self):
		self.state = 3

	def terminated(self):
		self.state = 4

	def is_new(self) -> bool:
		return self.state == 0
	
	def is_ready(self) -> bool:
		return self.state == 1
	
	def is_running(self) -> bool:
		return self.state == 2
	
	def is_waiting(self) -> bool:
		return self.state == 3
	
	def is_terminated(self) -> bool:
		return self.state == 4
	
	def get_state(self) -> int:
		return self.state
	
	def get_state_str(self) -> str:
		return self.states[self.state]
	
	def set_state(self, s: int) -> None:
		if self.state in [x for x in range(5)]:
			self.state = s
			return
		raise ValueError('s must be int between 0 and 4 not {s}')