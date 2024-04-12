from process import Process
from memory import Memory
import os
import sys
from test import Test
from clock import Clock
import subprocess
from errorMessage import ErrorMessage
from schedulingMethod import SchedulingMethod, FCFS, RR, MLQ
from colorama import Fore
from semaphore import Semaphore

class Shell:
	def __init__(self, op_sys, name: str) -> None:
		self.op_sys: OpSys = op_sys
		self.clock = Clock(0)
		self.processes: list[Process] = [Process(self.op_sys, self, 0, False, '')]
		# set active process
		self.process = self.processes[0]
		self.name: str = name
		self.mode: int = 0
		print(Fore.WHITE, end='')
		print(f'Josh OS Shell {name}')

		self.mode_names: dict[int, str] = {
			0: 'kernel',
			1: 'user'
		}

	def user_mode(self) -> None:
		self.mode = 1

	def kernal_mode(self) -> None:
		self.mode = 0

	def is_user_mode(self) -> bool:
		return self.mode == 1
	
	def is_kernel_mode(self) -> bool:
		return self.mode == 0
	
	def get_mode(self) -> int:
		return self.mode
	
	def set_fcfs(self) -> None:
		pass

	def set_rr(self) -> None:
		pass

	def set_mlq(self) -> None:
		pass

	def clean_input(self, text: str) -> str:
		return text.strip().lower()
	
	def run_shell(self) -> None:
		while True:
			c = self.get_user_input()
			if c == 0:
				break

	def get_user_input(self) -> int:
		print(Fore.WHITE, end='')
		u_input: str = input('> ')
		u_input = self.clean_input(u_input)
		if u_input == 'help':
			print(Fore.BLUE, end='')
			print('Commands:')
			print('\tosx <fileName>.asm <loadAddress>')
			print('\tload <fileName>.osx (-v)')
			print('\trun <fileName>.osx (-v)')
			print('\texecute <file1>.osx <arrivalTime1> <file2>.osx <arrivalTime2>...')
			print('\terrordump (-v)')
			print('\tcoredump (-v)')
			print('\tgantt')
			print('\tsetrr <int> (<int>)')
			print('\tsetsched <rr or fcfs or mlq>')
			print('\thelp')
			print('\tclear')
			print('\tquit')
			print('\tshell change <shellName>')
			print('Files must be loaded in free areas of memory')
			print('Files must be loaded before they are run')
			print('Optional -v can be used to activate verbose mode for additional result details.\n')
			print('Errors are cleared after each errordump')
			print('ctrl + C to exit an input prompt')
			return
		try:
			parts = u_input.split()
			verbose = False
			if '-v' in parts:
				verbose = True
				parts.remove('-v')
			if not parts:
				return 1
			command = parts[0]
			f_name = parts[-1]
			self.process.verbose = verbose
			#TODO: add compile option using osx
			if command in ('osx', 'osx.exe'):
				f_name = parts[1]
				load_addr = parts[2]
				try:
					dir_path = os.path.abspath(os.path.dirname(__file__))
					osx_path = os.path.join(dir_path, 'osx.exe')
					f_path = os.path.join(dir_path, f_name)
					p = subprocess.run([osx_path, f_path, load_addr], capture_output=True)
					if b'Error 1' in p.stdout:
						self.process.errors.append(ErrorMessage('OsxError', f'Invalid osx command "{u_input}".'))
				except:
					self.process.errors.append(ErrorMessage('OsxError', f'failed to run osx command "{u_input}".'))
			elif command == 'load':
				self.process.file_name = f_name
				self.process.load()
			elif command == 'run':
				self.process.file_name = f_name
				self.process.run()
			elif command == 'execute':
				# TODO: haddle additional files and arrival times
				# create processes
				self.processes = []
				self.op_sys.mlq.queues.clear_gantt()
				self.op_sys.rr.clear_gantt()
				p_id = 1
				self.op_sys.running_item = None
				self.op_sys.ready_queue.clear()
				self.op_sys.terminated_items.clear()
				for n in range((len(parts) - 1) // 2):
					p = Process(self.op_sys, self, p_id, verbose, parts[n*2+1], int(parts[n*2+2]))
					p_id += 1
					self.processes.append(p)
					self.op_sys.ready_queue.append(p)
					if verbose:
						self.process.verbose_results.add('Creating Process ' + str(p))
				self.processes.sort(key=lambda x: x.arrival_time)
				self.process = self.processes[0]
				self.op_sys.ready_queue.remove(self.process) # remove running process from ready
				self.clock.reset()
				if self.op_sys.scheduling_method is self.op_sys.mlq:
					self.op_sys.mlq.queues.p0.add_member(self.process)
				self.process.quantum = self.op_sys.scheduling_method.quantum1
				self.process.execute()
				return
			elif command == 'gantt':
				with open('gantt-results.txt', 'w') as f:
					if self.op_sys.scheduling_method is self.op_sys.mlq:
						f.write(self.op_sys.mlq.queues.get_gantt_chart())
					elif self.op_sys.scheduling_method is self.op_sys.rr:
						f.write(self.op_sys.rr.get_gantt_chart())
					else:
						return
					print(Fore.GREEN, end='')
					print('Gantt chart results writen to "gantt-results.txt"')
			elif command == 'setrr':
				q1 = int(parts[1])
				q2 = 99999999999 # default q2
				if len(parts) > 2:
					q2 = int(parts[2])
				if q1 < 4 or q2 < 4:
					print(Fore.RED, end='')
					print('Cannot set quantums lower than 4 due to stack requirments')
					return
				for m in (self.op_sys.fcfs, self.op_sys.rr, self.op_sys.mlq):
					m.quantum1 = q1
					m.quantum2 = q2
			elif command == 'setsched':
				if parts[1] in ('rr', 'rr1', 'round robin', 'roundrobin'):
					self.op_sys.scheduling_method = self.op_sys.rr
				elif parts[1] == 'fcfs':
					self.op_sys.scheduling_method = self.op_sys.fcfs
				elif parts[1] == 'mlq':
					self.op_sys.scheduling_method = self.op_sys.mlq
				else:
					raise ValueError('Invalid scheduling algrithm')
				print(Fore.GREEN, end='')
				print('Setting scheduling algorithm to ' + str(self.op_sys.scheduling_method))
			elif command == 'coredump':
				self.process.core_dump()
			elif command == 'errordump':
				self.process.error_dump()
			elif command in ('cls', 'clear'):
				os.system('cls')
			elif 'shell' in command:
				name = parts[-1]
				shell = self.op_sys.get_shell(name)
				if shell:
					self.swap_shell(shell)
				else:
					self.new_shell(name)
				return 0
			elif command in ('exit', 'quit'):
				print(Fore.GREEN, end='')
				print('Exiting with code 0')
				print(Fore.WHITE, end='')
				return 0
			else:
				print(Fore.RED, end='')
				print(f'Unknown command "{command}"')
				return 1
		except:
			print(Fore.RED, end='')
			print('Invalid command or arguments')
		
	def swap_shell(self, shell) -> None:
		self.op_sys.swap_shell(shell)

	def new_shell(self, name: str) -> None:
		self.op_sys.new_shell(name)

class OpSys:
	def __init__(self) -> None:
		sys.setrecursionlimit(10**6)
		self.shells: list[Shell] = []
		#self.new_queue: list = []
		self.ready_queue: list = []
		self.running_item = None
		# self.waiting_queue: list = []
		self.terminated_items: list = []
		self.message_queue = []
		self.message_queue_semaphore: Semaphore = Semaphore()
		self.fcfs: SchedulingMethod = FCFS(self)
		self.rr: SchedulingMethod = RR(self, quantum=10)
		self.mlq: SchedulingMethod = MLQ(self, quantum1=10, quantum2=20)
		self.scheduling_method: SchedulingMethod = self.rr
		self.page_size: int = 36
		self.memory = None
		self.page_table = {}
		self.active_shell: Shell = Shell(self, 'shell1')
		self.shells.append(self.active_shell)
		self.memory = Memory(self.active_shell.process)
		self.active_shell.process.memory = self.memory
		self.message_queue_semaphore = Test()
		self.active_shell.run_shell()

	def signal_message(self, message: bytes, process=None):
		self.message_queue_semaphore.wait()
		self.message_queue.append(message)
		self.message_queue_semaphore.signal()

	def receive_message(self) -> bytes:
		self.message_queue_semaphore.wait()
		try:
			result = self.message_queue.pop()
		except:
			pass
		self.message_queue_semaphore.signal()
		return result

	def run_next_process(self) -> bool:
		return self.scheduling_method.run()

	def get_shell(self, name: str) -> Shell | None:
		shells_found = [x for x in self.shells if x.name.strip().lower() == name.strip().lower()]
		if not len(shells_found):
			return None
		return shells_found[0]
	
	def swap_shell(self, shell) -> None:
		self.active_shell.mode = 1
		self.active_shell = shell
		self.active_shell.mode = 1
		self.memory.process = self.active_shell.process
		self.active_shell.process.memory = self.memory
		os.system('cls')
		print(Fore.BLUE, end='')
		print(f'Switched to shell {self.active_shell.name}')
		self.active_shell.run_shell()

	def new_shell(self, name: str) -> None:
		new_shell = Shell(self, name)
		os.system('cls')
		print(Fore.BLUE, end='')
		print(f'New shell {name} created')
		self.active_shell = new_shell
		self.memory.process = self.active_shell.process
		self.active_shell.process.memory = self.memory
		self.active_shell.run_shell()


if __name__ == '__main__':
	op_sys = OpSys()
