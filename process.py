'''
Notes:
2D array for main memory - x*6

should not need a CPU (use fetch, decode, execute cycle)

file.asm -> osx.exe -> file.osx -> load reads instructions into main memory -> run using process control block

use a table to keep error messages

Use a load bit to indicate if shell is in user or kernal mode

'''

import os
import sys
from pcb import PCB
from osxFileDetails import OsxFileDetails
from operations import Operations
from registers import Registers
from errorMessage import ErrorMessage
from verboseMessage import VerboseMessage
from clock import Clock
from colorama import Fore

class Process:

	def __init__(self, op_sys, shell, p_id: int, verbose: bool, file_name: str, arrival_time: int=0) -> None:
		self.op_sys = op_sys
		self.shell = shell
		self.clock: Clock = self.shell.clock
		self.verbose = verbose
		self.verbose_results = VerboseMessage("")
		self.file_name = file_name
		self.offset = 0
		self.page_number = 0
		self.registers = Registers()
		self.p_id = p_id
		self.response_time = 0
		self.turnaround_time = 0
		self.running_time = 0
		self.waiting_time = 0
		self.quantum = 99999999999
		self.hit_swi = False
		self.mlq_swi_hits = 0
		self.mlq_bursts = 0
		self.finish_time = None
		self.arrival_time = arrival_time
		# has run is used to tell if a program can go into an occupied location
		# if True, the location is its own location and it is safe to return to that location
		self.is_running = False
		# resume time is the time that the program last started or resumed
		self.resume_time = self.arrival_time
		self.pcb: PCB = PCB(self.file_name, 0, 0, self.registers.pc(), 0, 1000, [])
		# error for div by zero
		# error for memory overlap
		# error for out of space
		self.errors = []
		self.file_details = None
		self.memory = op_sys.memory
		self.op_methods = Operations(self)
		if self.file_name:
			self.preload()
		self.clear_file_details()

		self.op_names = {
			0: 'adr',
			1: 'mov',
			2: 'str', # store int
			3: 'strb', # store byte
			4: 'ldr', # load int
			5: 'ldrb', # load byte
			6: 'bx', # jump to address
			7: 'b', # jump to label
			8: 'bne', # jump to label if Z register is not zero
			9: 'bgt', # jump to label if Z register is gt zero
			10: 'blt', # jump to label if Z register is lt zero
			11: 'beq', # jump to label if Z register is zero
			12: 'cmp', # compare
			13: 'and', # and
			14: 'orr', # or
			15: 'eor', # exclusive or
			16: 'add', # add
			17: 'sub', # subtract
			18: 'mul', # multiply
			19: 'div', # divide
			20: 'swi', # software interupt (0: read from keyboard, 1: print, 2: error)
			21: 'bl', # jump to label and link
			22: 'mvi'
		}

	def __str__(self) -> str:
		return f"Process(p_id='{self.p_id}', file_name='{self.file_name}', arrival_time='{self.arrival_time}', finish_time='{self.finish_time}', running_time='{self.running_time}', waiting_time='{self.waiting_time}', response_time='{self.response_time}', turnaround_time='{self.turnaround_time}')"

	def update_stats(self):
		if (self.is_running and self in self.op_sys.ready_queue) or (self.arrival_time < self.clock.get_value() and not self.is_running and self is not self.op_sys.running_item and self not in self.op_sys.terminated_items):
			self.waiting_time += 1
		if self.arrival_time < self.clock.get_value() and not self.is_running and self is not self.op_sys.running_item and self not in self.op_sys.terminated_items:
			self.response_time += 1
		if self.is_running and self is self.op_sys.running_item:
			self.running_time += 1
		self.page_number = self.registers.pc() // self.op_sys.get_page_size()
		if self.page_number > 0:
			self.offset = self.registers.pc() % self.op_sys.get_page_size()
		else:
			self.offset = self.registers.pc()

	def clear_file_details(self) -> None:
		self.file_details = OsxFileDetails(
				0,
				0,
				0,
				0
			)
		
	def garbage_cleanup(self) -> None:
		self.op_sys.memory.clean(self.pcb.memory_l_limit, self.pcb.memory_u_limit)

	def send(self, message):
		pass

	def receive(self):
		print()

	def preload(self) -> bool:
		try:
			with open(self.file_name, 'rb') as f:
				# file = f.read() # warning! debug only!
				byte_size = int.from_bytes(f.read(1))
				f.read(3)
				pc = f.read(4) # skip pc
				loader = int.from_bytes(f.read(1)) * self.op_sys.page_size
				f.read(3)
				self.pcb.memory_u_limit = int(loader) + int(byte_size)
				self.pcb.memory_l_limit = int(loader)
				return True
		except:
			self.errors.append(ErrorMessage('PreloadError', 'An error has occurred.'))
			return False

	def load(self) -> None:
		#TODO: don't load process until its arrival time
		self.pcb.state = 0
		self.registers = Registers()
		self.verbose_results.clear()
		self.verbose_results.add('')
		try:
			with open(self.file_name, 'rb') as f:
				byte_size = int.from_bytes(f.read(1))
				f.read(3)
				pc = int.from_bytes(f.read(1))
				f.read(3)
				loader = int.from_bytes(f.read(1)) * self.op_sys.page_size
				f.read(3)
				pc += loader
				if pc % 6 != 0:
					pc = (pc // 6 + 1) * 6
				self.file_details = OsxFileDetails(
					byte_size,
					pc,
					loader,
					loader
				)
				self.verbose_results.add(str(self.file_details), end='\n\n')

				# set the pc to the pc address
				self.registers.pc(self.file_details.pc)
				self.pcb.pc = self.registers.pc()
				self.pcb.memory_u_limit = int(self.file_details.loader) + int(self.file_details.byte_size)
				self.pcb.memory_l_limit = int(self.file_details.loader)
				self.page_number = self.registers.pc() // self.op_sys.get_page_size()
				# double memory size if there is not a memory location for the program
				while self.pcb.memory_u_limit + 6 >= len(self.memory.main_memory) * 6:
					self.memory.double_size()
				# start loading at the loader address
				loc = self.pcb.memory_l_limit
				if not self.memory.is_free(self.pcb.memory_l_limit, self.pcb.memory_u_limit):
					self.errors.append(ErrorMessage('LoadError', f'Cannot load {self.file_name} at location {loc} where not enough memory is free.'))
					self.clear_file_details()

				while loc < int(self.file_details.loader) + int(self.file_details.byte_size):
					byte = f.read(1) # get opcode
					six_bytes: bytes = byte + f.read(5)
					if not byte:
						break
					op_name = ''
					error = False
					if int.from_bytes(byte) in self.op_names:
						op_name = self.op_names[int.from_bytes(byte)]
					# items loaded before the pc are not considered operations
					if loc >= self.file_details.pc - 6:
						match op_name:
							case 'adr':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg="{hex(six_bytes[1])}", addr=\"{" ".join([str(hex(b)) for b in six_bytes[2:]])}\")')
							case 'mov':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'str':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'strb':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'ldr':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'ldrb':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'bx':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg="{hex(six_bytes[1])}")')
								# 4 bytes unused
							case 'b':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(label=\"{" ".join([str(hex(b)) for b in six_bytes[1:5]])}\")')
								# 1 byte unused
							case 'bne':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(label=\"{" ".join([str(hex(b)) for b in six_bytes[1:5]])}\")')
								# 1 byte unused
							case 'bgt':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(label=\"{" ".join([str(hex(b)) for b in six_bytes[1:5]])}\")')
								# 1 byte unused
							case 'blt':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(label=\"{" ".join([str(hex(b)) for b in six_bytes[1:5]])}\")')
								# 1 byte unused
							case 'beq':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(label=\"{" ".join([str(hex(b)) for b in six_bytes[1:5]])}\")')
								# 1 byte unused
							case 'cmp':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'and':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'orr':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'eor':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\")')
								# 3 bytes unused
							case 'add':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\", reg3=\"{hex(six_bytes[3])}\")')
								# 2 bytes unused
							case 'sub':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\", reg3=\"{hex(six_bytes[3])}\")')
								# 2 bytes unused
							case 'mul':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\", reg3=\"{hex(six_bytes[3])}\")')
								# 2 bytes unused
							case 'div':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg1="{hex(six_bytes[1])}", reg2=\"{hex(six_bytes[2])}\", reg3=\"{hex(six_bytes[3])}\")')
								# 2 bytes unused
							case 'swi':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(imm=\"{" ".join([str(hex(b)) for b in six_bytes[1:5]])}\")')
								# 1 byte unused
							case 'bl':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(label=\"{" ".join([str(hex(b)) for b in six_bytes[1:5]])}\")')
								# 1 byte unused
							case 'mvi':
								self.verbose_results.add(f'Loading instruction {int.from_bytes(byte)} ({op_name})')
								self.verbose_results.add(f'{op_name}(reg="{hex(six_bytes[1])}", imm=\"{" ".join([str(hex(b)) for b in six_bytes[2:]])}\")')
							case _:
								self.errors.append(ErrorMessage('LoadError', f'Unknown operation {byte}'))
								error = True
					self.memory.load_6bytes(six_bytes, loc)
					loc += 6
		except FileNotFoundError as e:
			self.errors.append(ErrorMessage('LoadError', f'File not found {self.file_name}.'))
			return
		except:
			self.errors.append(ErrorMessage('LoadError', 'An error has occurred.'))
			return
		if self.verbose:
			print(Fore.WHITE, end='')
			print(self.verbose_results)
		if self.file_details.byte_size != 0:
			print(Fore.GREEN, end='')
			print(f'Finished loading {self.file_name} at location {self.file_details.starting_loader // self.op_sys.page_size} and time {self.clock.get_value()}.')
		# update pcb
		self.pcb.state = 1

	def execute(self, arrival_time: int=None):
		self.load()
		self.run(False if self.op_sys.scheduling_method is self.op_sys.mlq else True)

	def run(self, is_not_mlq=True, is_execute=True) -> None:
		if not is_execute and not self.is_running:
			self.load()
		self.verbose_results.clear()
		self.verbose_results.add('')
		self.is_running = True
		self.hit_swi = False
		self.op_sys.running_item = self
		# set the pc to the pc address
		self.registers.pc(self.pcb.pc)
		# start loading at the loader address
		loc = self.pcb.memory_l_limit
		if self.file_details.byte_size == 0:
			self.errors.append(ErrorMessage('FetchError', f'No file loaded {self.file_name}.'))
		self.memory.process = self
		try:
			while self.registers.pc() < self.pcb.memory_u_limit:
				six_bytes = self.memory.fetch_6bytes(self.registers.pc())
				if type(six_bytes[0]) == int:
					six_bytes = [int.to_bytes(n) for n in six_bytes]
				byte = six_bytes[0] # get opcode
				if not byte:
					break
				op_name = ''
				error = False
				if int.from_bytes(byte) in self.op_names:
					op_name = self.op_names[int.from_bytes(byte)]
				reg1: bytes = six_bytes[1]
				reg2: bytes = six_bytes[2]
				reg3: bytes = six_bytes[3]
				match op_name:
					case 'adr':
						self.verbose_results.add(f'reg {reg1} <- address {six_bytes[2]+six_bytes[3]+six_bytes[4]+six_bytes[5]}')
						self.op_methods.adr(reg1, six_bytes[2]+six_bytes[3]+six_bytes[4]+six_bytes[5])
					case 'mov':
						self.verbose_results.add(f'reg {reg1} <- reg {reg2}')
						self.op_methods.mov(reg1, reg2)
						# 3 bytes unused
					case 'str':
						self.verbose_results.add(f'memory[reg {reg2}] <- reg {reg1}')
						self.op_methods.str(reg1, reg2)
						# 3 bytes unused
					case 'strb':
						self.verbose_results.add(f'memory[reg {reg2}] <- byte(memory[reg {reg1}])')
						self.op_methods.strb(reg1, reg2)
						# 3 bytes unused
					case 'ldr':
						self.verbose_results.add(f'reg {reg1} <- memory[reg {reg2}]')
						self.op_methods.ldr(reg1, reg2)
						# 3 bytes unused
					case 'ldrb':
						self.verbose_results.add(f'reg {reg1} <- byte(memory[reg {reg2}])')
						self.op_methods.ldrb(reg1, reg2)
						# 3 bytes unused
					case 'bx':
						self.verbose_results.add(f'PC <- reg {reg1}')
						self.op_methods.bx(reg1)
						# 4 bytes unused
					case 'b':
						self.verbose_results.add(f'PC <- address(label {six_bytes[1]+six_bytes[2]+six_bytes[3]+six_bytes[4]})')
						self.op_methods.b(six_bytes[1])
						# 1 byte unused
					case 'bne':
						self.verbose_results.add(f'PC <- address(label {six_bytes[1]+six_bytes[2]+six_bytes[3]+six_bytes[4]}) if Z != 0')
						self.op_methods.bne(six_bytes[1])
						# 1 byte unused
					case 'bgt':
						self.verbose_results.add(f'PC <- address(label {six_bytes[1]+six_bytes[2]+six_bytes[3]+six_bytes[4]}) if Z > 0')
						self.op_methods.bgt(six_bytes[1])
						# 1 byte unused
					case 'blt':
						self.verbose_results.add(f'PC <- address(label {six_bytes[1]+six_bytes[2]+six_bytes[3]+six_bytes[4]}) if Z < 0')
						self.op_methods.blt(six_bytes[1])
						# 1 byte unused
					case 'beq':
						self.verbose_results.add(f'PC <- address(label {six_bytes[1]+six_bytes[2]+six_bytes[3]+six_bytes[4]}) if Z == 0')
						self.op_methods.beq(six_bytes[1])
						# 1 byte unused
					case 'cmp':
						self.verbose_results.add(f'Z <- reg {reg1} - reg {reg2}')
						self.op_methods.cmp(reg1, reg2)
						# 3 bytes unused
					case 'and':
						self.verbose_results.add(f'Z <- reg {reg1} & reg {reg2}')
						self.op_methods.and_op(reg1, reg2)
						# 3 bytes unused
					case 'orr':
						self.verbose_results.add(f'Z <- reg {reg1} | reg {reg2}')
						self.op_methods.orr(reg1, reg2)
						# 3 bytes unused
					case 'eor':
						self.verbose_results.add(f'Z <- reg {reg1} ^ reg {reg2}')
						self.op_methods.eor(reg1, reg2)
						# 3 bytes unused
					case 'add':
						self.verbose_results.add(f'reg {reg1} <- reg {reg2} + reg {reg3}')
						self.op_methods.add(reg1, reg2, reg3)
						# 2 bytes unused
					case 'sub':
						self.verbose_results.add(f'reg {reg1} <- reg {reg2} - reg {reg3}')
						self.op_methods.sub(reg1, reg2, reg3)
						# 2 bytes unused
					case 'mul':
						self.verbose_results.add(f'reg {reg1} <- reg {reg2} * reg {reg3}')
						self.op_methods.mul(reg1, reg2, reg3)
						# 2 bytes unused
					case 'div':
						self.verbose_results.add(f'reg {reg1} <- reg {reg2} / reg {reg3}')
						self.op_methods.div(reg1, reg2, reg3)
						# 2 bytes unused
					case 'swi':
						self.verbose_results.add(f'run interrupt imm {six_bytes[1]+six_bytes[2]+six_bytes[3]+six_bytes[4]}')
						self.op_methods.swi(six_bytes[1])
						# 1 byte unused
					case 'bl':
						self.verbose_results.add(f'PC <- address(label {six_bytes[1]+six_bytes[2]+six_bytes[3]+six_bytes[4]})')
						self.op_methods.bl(six_bytes[1])
						# 1 byte unused
					case 'mvi':
						self.verbose_results.add(f'reg {reg1} <- imm {six_bytes[2]+six_bytes[3]+six_bytes[4]+six_bytes[5]}')
						self.op_methods.mvi(reg1, six_bytes[2])
						# self.op_methods.mvi(reg1, six_bytes[2]+six_bytes[3]+six_bytes[4]+six_bytes[5])
					case _:
						# skip unknown operation
						self.errors.append(ErrorMessage('FetchError', f'Unknown operation {byte}'))
						error = True
				self.registers.pc( self.registers.pc() + 6 )
				self.clock_tick()
				self.page_number = self.registers.pc() // self.op_sys.get_page_size()
				if self.page_number > 0:
					self.offset = self.registers.pc() % self.op_sys.get_page_size()
				else:
					self.offset = self.pcb.pc
				for p in self.shell.processes:
					p.update_stats()
				if is_execute and self.op_sys.scheduling_method is self.op_sys.rr:
					self.op_sys.rr.track_gantt()
				# check how long process has been running
				if is_execute and (self.shell.clock.get_value() >= self.resume_time + self.quantum or self.hit_swi): #TODO: change to >?
					self.to_ready(is_not_mlq)
					return
		except:
			self.errors.append(ErrorMessage('FetchError', 'An error has occurred.'))
			return
		if self.verbose:
			print(Fore.WHITE, end='')
			print(self.verbose_results)
		if (self.file_details.byte_size != 0 and self not in self.op_sys.terminated_items) or not is_execute:
			print(Fore.GREEN, end='')
			print(f'Finished running {self.file_name} at time {self.clock.get_value()}.')
			self.is_running = False # must reload to run again
			self.finish_time = self.clock.get_value()
			self.turnaround_time = self.finish_time - self.arrival_time
			self.to_terminated(is_not_mlq)
			print(Fore.WHITE, end='')

	def to_new(self) -> None:
		pass
	
	def to_ready(self, is_not_mlq=True) -> None:
		# update pcb
		self.pcb.state = 1
		self.pcb.pc = self.registers.pc()
		self.pcb.registers = self.registers.registers.copy()
		# move to ready queue
		if self is self.op_sys.running_item:
			self.op_sys.running_item = None
		self.op_sys.ready_queue.append(self)
		if is_not_mlq:
			# run next process
			self.op_sys.run_next_process()
		else:
			# track swi-hit:runs ratio
			if self.hit_swi:
				self.mlq_swi_hits += 1
			self.hit_swi = False
			self.mlq_bursts += 1
			# decide to promote or demote
			swi_hit_ratio = self.mlq_swi_hits / self.mlq_bursts
			if self.mlq_bursts >= 5:
				# reset ratio tracking every 5
				self.mlq_swi_hits = 0
				self.mlq_bursts = 0
				if self in self.op_sys.mlq.queues.p0.members:
					if swi_hit_ratio < 1: # not all 5 runs hit swi
						self.op_sys.mlq.queues.demote(self, 0)
					else:
						self.op_sys.mlq.queues.no_change(self, 0)
				elif self in self.op_sys.mlq.queues.p1.members:
					if swi_hit_ratio > 0.8: # all 5 runs hit swi
						self.op_sys.mlq.queues.promote(self, 1)
					elif swi_hit_ratio < 0.8: # less than 4/5 runs hit swi
						self.op_sys.mlq.queues.demote(self, 1)
					else: # exactly 4/5 runs hit swi
						self.op_sys.mlq.queues.no_change(self, 1)
				elif self in self.op_sys.mlq.queues.p2.members:
					if swi_hit_ratio >= 0.8: # 4/5 or more runs hit swi
						self.op_sys.mlq.queues.promote(self, 2)
					else:
						self.op_sys.mlq.queues.no_change(self, 2)
				else:
					raise ValueError('not in MLQ')
			else:
				if self in self.op_sys.mlq.queues.p0.members:
					self.op_sys.mlq.queues.no_change(self, 0)
				elif self in self.op_sys.mlq.queues.p1.members:
					self.op_sys.mlq.queues.no_change(self, 1)
				elif self in self.op_sys.mlq.queues.p2.members:
					self.op_sys.mlq.queues.no_change(self, 2)
				else:
					raise ValueError('not in MLQ')
			self.op_sys.run_next_process()


	def to_running(self):
		pass

	def to_waiting(self):
		pass

	def to_terminated(self, is_not_mlq=True):
		self.garbage_cleanup()
		# remove from running and ready
		self.op_sys.running_item = None
		if self in self.op_sys.ready_queue:
			self.op_sys.ready_queue.remove(self)
		# move to terminated list
		self.op_sys.terminated_items.append(self)
		self.op_sys.run_next_process()
	
	def core_dump(self) -> None:
		self.memory.dump(self.verbose)

	def clock_tick(self) -> int:
		return self.clock.tick()

	def error_dump(self) -> None:
		if self.errors:
			print(Fore.RED, end='')
			print(f'{len(self.errors)} errors found')
			for e in self.errors:
				print(e)
		else:
			print(Fore.GREEN, end='')
			print('No errors found')
		self.errors.clear()

	def get_int_from_str(self, s: str):
		return int( ''.join(x for x in s if x.isdigit()) )

	# def main(self):
	# 	self.load()
	# 	self.run()
	# 	self.core_dump()
	# 	self.error_dump()

# if __name__ == '__main__':
# 	driver = Process(True, 'int.osx')
# 	driver.main()