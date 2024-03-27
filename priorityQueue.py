class PriorityQueue:
	def __init__(self, queues, queue_number: int, quantum: int) -> None:
		self.queues = queues
		self.queue_number: int = queue_number
		self.quantum = quantum
		self.gantt_chart = []
		self.gantt_times = []
		self.members: list = []

	def track_gantt(self):
		self.gantt_times.append(str(self.queues.op_sys.active_shell.clock.get_value()))
		if not self.is_empty():
			self.gantt_chart.append(str(self.members[0].p_id))
		else:
			self.gantt_chart.append('x')

	def clear_gantt(self) -> None:
		self.gantt_chart.clear()
		self.gantt_times.clear()

	def is_empty(self) -> bool:
		return len(self.members) == 0

	def add_member(self, member):
		self.members.append(member)

	def remove_member(self, member):
		self.members.remove(member)

	def clear(self):
		self.members.clear()

	def select_process(self) -> bool:
		self.queues.selection_item = (self.queues.selection_item + 1) % 4
		# run the process from members
		chosen = None
		if not self.is_empty():
			chosen = self.members[0]
		else:
			self.queues.was_empty(self.queue_number)
		# remove running item from ready queue while running
		if chosen in self.queues.op_sys.ready_queue:
			self.queues.op_sys.ready_queue.remove(chosen)
		chosen.pcb.state = 2
		chosen.resume_time = self.queues.op_sys.active_shell.clock.get_value()
		self.queues.op_sys.running_item = chosen
		self.queues.op_sys.active_shell.process = chosen
		if self.queues.op_sys.active_shell.process.verbose:
			self.queues.op_sys.active_shell.process.verbose_results.add(f'Scheduling process "{chosen}"')
		if not chosen.is_running:
			chosen.load()
		chosen.quantum = self.quantum
		chosen.run(False)
		return True

class PriorityQueues:
	def __init__(self, op_sys, quantum1: int=10, quantum2: int=20) -> None:
		self.op_sys = op_sys
		self.quantum1 = quantum1
		self.quantum2 = quantum2
		self.p0: PriorityQueue = PriorityQueue(self, 0, quantum1)
		self.p1: PriorityQueue = PriorityQueue(self, 1, quantum2)
		self.p2: PriorityQueue = PriorityQueue(self, 2, 99999999999)
		self.selection_order: list[PriorityQueue] = [self.p0, self.p0, self.p1, self.p2]
		self.selection_item: int = 0

	def clear_gantt(self):
		for q in (self.p0, self.p1, self.p2):
			q.clear_gantt()

	def remove_process(self, process) -> None:
		for q in (self.p0, self.p1, self.p2):
			if process in q.members:
				q.remove_member(process)
	
	def clean_queues(self) -> None:
		to_remove: list = []
		for q in (self.p0, self.p1, self.p2):
			for p in q.members:
				if p in self.op_sys.terminated_items:
					to_remove.append(p)
		for p in to_remove:
			self.remove_process(p)

	def clear_queues(self) -> None:
		self.p0.clear()
		self.p1.clear()
		self.p2.clear()
		self.selection_item = 0

	def queues_are_empty(self) -> bool:
		return self.p0.is_empty() and self.p1.is_empty() and self.p2.is_empty()

	def get_gantt_chart(self) -> str:
		times = 'time:\t'
		for t in self.p0.gantt_times:
			times += f'{t}\t'
		p0_row = 'p0:\t\t'
		for i in self.p0.gantt_chart:
			p0_row += f'{i}\t'
		p1_row = 'p1:\t\t'
		for i in self.p1.gantt_chart:
			p1_row += f'{i}\t'
		p2_row = 'p2:\t\t'
		for i in self.p2.gantt_chart:
			p2_row += f'{i}\t'
		return 'MLQ Gantt Chart:' + '\n' + times + '\n' + p0_row + '\n' + p1_row + '\n' + p2_row + '\n'

	def select_queue(self, queue: int | None= None):
		if queue == 0:
			self.clear_queues()
		# self.op_sys.ready_queue will be used as long as processes live
		ready_processes: list = [p for p in self.op_sys.ready_queue if p.arrival_time <= self.op_sys.active_shell.clock.get_value()]
		# if all queues are empty and there are still more processes not arrived, tick clock
		while not ready_processes and self.op_sys.ready_queue and self.queues_are_empty():
			self.op_sys.active_shell.clock.tick()
			ready_processes: list = [p for p in self.op_sys.ready_queue if p.arrival_time <= self.op_sys.active_shell.clock.get_value()]
		new_arrivals_with_space = []
		for p in ready_processes:
			try:
				if (p not in self.p0.members + self.p1.members + self.p2.members) and (self.op_sys.memory.is_free(p.pcb.memory_l_limit, p.pcb.memory_u_limit) or p.is_running):
					new_arrivals_with_space.append(p)
			except IndexError: # memory for item has not been created (memory is free)
				new_arrivals_with_space.append(p)
		# move ready processes into MLQs
		for p in new_arrivals_with_space:
			self.p0.add_member(p) # add new arrivals with space to 0 priority queue

		self.clean_queues() # remove terminated programs from queues
		
		for q in (self.p0, self.p1, self.p2):
			q.track_gantt()

		empty_queues = 0
		while empty_queues < 3:
			if not self.selection_order[self.selection_item].is_empty():
				# select next process
				self.selection_order[self.selection_item].select_process()
				# advance selection to next queue
				# self.selection_order = (self.selection_order + 1) % 4
				break
			else: # if next selected queue is empty, advance to next queue
				self.selection_item = (self.selection_item + 1) % 4
				empty_queues += 1

	def promote(self, process, old_queue: int):
		if old_queue == 0:
			self.p0.remove_member(process)
			self.p0.add_member(process)
		elif old_queue == 1:
			self.p1.remove_member(process)
			self.p0.add_member(process)
		elif old_queue == 2:
			self.p2.remove_member(process)
			self.p1.add_member(process)
		
	def demote(self, process, old_queue: int):
		if old_queue == 0:
			self.p0.remove_member(process)
			self.p1.add_member(process)
		elif old_queue == 1:
			self.p1.remove_member(process)
			self.p2.add_member(process)
		elif old_queue == 2:
			self.p2.remove_member(process)
			self.p2.add_member(process)

	def no_change(self, process, queue: int):
		# move process to end of its queue
		if queue == 0:
			self.p0.remove_member(process)
			self.p0.add_member(process)
		elif queue == 1:
			self.p1.remove_member(process)
			self.p1.add_member(process)
		elif queue == 2:
			self.p2.remove_member(process)
			self.p2.add_member(process)
	
	def was_empty(self, queue: int):
		raise Exception(f'MLG error: {queue} queue was run while empty')
