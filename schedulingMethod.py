from priorityQueue import PriorityQueues

class SchedulingMethod:
	def __init__(self, op_sys, quantum1=99999999999, quantum2=99999999999) -> None:
		self.op_sys = op_sys
		self.quantum1 = quantum1
		self.quantum2 = quantum2

	def run(self) -> bool:
		pass

class FCFS(SchedulingMethod):
	def __init__(self, op_sys) -> None:
		super().__init__(op_sys)

	def __str__(self) -> str:
		return 'FCFS'

	def run(self) -> bool:
		# consider only if p is at/past arrival time and there is space
		ready_processes: list = [p for p in self.op_sys.ready_queue if p.arrival_time <= self.op_sys.active_shell.clock.get_value()]
		# if no processes are arrived and ready, but there are more in the ready queue, tick the clock
		while not ready_processes and self.op_sys.ready_queue:
			self.op_sys.active_shell.clock.tick()
			ready_processes: list = [p for p in self.op_sys.ready_queue if p.arrival_time <= self.op_sys.active_shell.clock.get_value()]
		has_space = []
		for p in ready_processes:
			try:
				if self.op_sys.memory.is_free(p.pcb.memory_l_limit, p.pcb.memory_u_limit) or p.is_running:
					has_space.append(p)
			except IndexError: # memory for item has not been created (memory is free)
				has_space.append(p)
		# TODO: allow process to reoccupy its own position
		if has_space:
			next_process = self.op_sys.ready_queue.pop(self.op_sys.ready_queue.index(has_space[0]))
			next_process.pcb.state = 2
			next_process.resume_time = self.op_sys.active_shell.clock.get_value()
			self.op_sys.running_item = next_process
			self.op_sys.active_shell.process = next_process
			if self.op_sys.active_shell.process.verbose:
				self.op_sys.active_shell.process.verbose_results.add(f'Scheduling process "{next_process}"')
			if not next_process.is_running:
				next_process.load()
			next_process.quantum = self.quantum1
			next_process.run()
			return True
		return False

class RR(SchedulingMethod):
	def __init__(self, op_sys, quantum) -> None:
		super().__init__(op_sys, quantum)
		self.gantt_times: list[int] = []
		self.gantt_chart: list[int] = []

	def __str__(self) -> str:
		return 'RR'
	
	def track_gantt(self):
		self.gantt_times.append(str(self.op_sys.active_shell.clock.get_value()))
		if self.op_sys.running_item:
			self.gantt_chart.append(str(self.op_sys.running_item.p_id))
		else:
			self.gantt_chart.append('x')
	
	def get_gantt_chart(self) -> str:
		times = 'time:\t'
		for t in self.gantt_times:
			times += f'{t}\t'
		p0_row = 'p0:\t\t'
		for i in self.gantt_chart:
			p0_row += f'{i}\t'
		return 'RR Gantt Chart:' + '\n' + times + '\n' + p0_row + '\n'

	def clear_gantt(self) -> None:
		self.gantt_chart.clear()
		self.gantt_times.clear()

	def run(self) -> bool:
		# consider only if p is at/past arrival time and there is space
		ready_processes: list = [p for p in self.op_sys.ready_queue if p.arrival_time <= self.op_sys.active_shell.clock.get_value()]
		# if no processes are arrived and ready, but there are more in the ready queue, tick the clock
		while not ready_processes and self.op_sys.ready_queue:
			self.op_sys.active_shell.clock.tick()
			ready_processes: list = [p for p in self.op_sys.ready_queue if p.arrival_time <= self.op_sys.active_shell.clock.get_value()]
		has_space = []
		for p in ready_processes:
			try:
				if self.op_sys.memory.is_free(p.pcb.memory_l_limit, p.pcb.memory_u_limit) or p.is_running:
					has_space.append(p)
			except IndexError: # memory for item has not been created (memory is free)
				has_space.append(p)
		# TODO: allow process to reoccupy its own position
		if has_space:
			next_process = self.op_sys.ready_queue.pop(self.op_sys.ready_queue.index(has_space[0]))
			# Rerun process and update variables
			next_process.pcb.state = 2
			next_process.resume_time = self.op_sys.active_shell.clock.get_value()
			self.op_sys.running_item = next_process
			self.op_sys.active_shell.process = next_process
			if self.op_sys.active_shell.process.verbose:
				self.op_sys.active_shell.process.verbose_results.add(f'Scheduling process "{next_process}"')
			if not next_process.is_running:
				next_process.load()
			next_process.quantum = self.quantum1
			next_process.run()
			return True
		return False

class MLQ(SchedulingMethod):
	def __init__(self, op_sys, quantum1=99999999999, quantum2=99999999999) -> None:
		super().__init__(op_sys, quantum1, quantum2)
		self.queues: PriorityQueues = PriorityQueues(op_sys, self.quantum1, self.quantum2)
		self.first_run = True

	def __str__(self) -> str:
		return 'MLQ'

	def run(self) -> bool:
		if self.first_run:
			self.first_run = False
			self.queues.select_queue(0)
		else:
			self.queues.select_queue()