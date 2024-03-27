class Registers:
	def __init__(self, r0=b'\x00', r1=b'\x00', r2=b'\x00', r3=b'\x00', r4=b'\x00', r5=b'\x00', sp=b'\x00', fp=b'\x00', sl=b'\x00', z=b'\x00', sb=b'\x00', pc=0) -> None:
		self.registers = {
			0: r0,
			1: r1,
			2: r2,
			3: r3,
			4: r4,
			5: r5,
			6: sp,
			7: fp,
			8: sl,
			9: z,
			10: sb,
			11: pc,
		}

	def set_reg(self, r: bytes, value: bytes) -> None:
		self.registers[int.from_bytes(r)] = value

	def get_reg(self, r: bytes) -> bytes:
		return self.registers[int.from_bytes(r)]

	def r0(self, value=None) -> bytes | None:
		"""General purpose"""
		if value is not None:
			self.registers[0] = value
			return
		return self.registers[0]
	
	def r1(self, value=None):
		"""General purpose"""
		if value is not None:
			self.registers[1] = value
			return
		return self.registers[1]
	
	def r2(self, value=None):
		"""General purpose"""
		if value is not None:
			self.registers[2] = value
			return
		return self.registers[2]
	
	def r3(self, value=None):
		"""General purpose"""
		if value is not None:
			self.registers[3] = value
			return
		return self.registers[3]
	
	def r4(self, value=None):
		"""General purpose"""
		if value is not None:
			self.registers[4] = value
			return
		return self.registers[4]
	
	def r5(self, value=None):
		"""General purpose"""
		if value is not None:
			self.registers[5] = value
			return
		return self.registers[5]
	
	def sp(self, value=None):
		"""
		Space Pointer
		Point at top of run-time stack.
		Used with SL register to test for Stack-Overflow and Out-Of-Memory
		"""
		if value is not None:
			self.registers[6] = value
			return
		return self.registers[6]
	
	def fp(self, value=None):
		"""
		Frame Pointer
		Point at current frame on run-time stack
		"""
		if value is not None:
			self.registers[7] = value
			return
		return self.registers[7]
	
	def sl(self, value=None):
		"""
		Stack Limit
		Limit the size of the run-time stack.
		Set this register in your VM to the byteSize value stored as the first value in the osX byte file.
		Can be used to test for Stack-Overflow and Out-Of-Memory
		"""
		if value is not None:
			self.registers[8] = value
			return
		return self.registers[8]
	
	def z(self, value=None):
		"""
		Flag
		Set when CMP instruction is run.
		Used by conditional branch instructions
		"""
		if value is not None:
			self.registers[9] = value
			return
		return self.registers[9]

	def sb(self, value=None):
		"""
		Stack Base
		Limit the size of memory in your VM
		Set this register in your VM to the maximum size of memory.
		Can be used to test for Stack-Underflow
		"""
		if value is not None:
			self.registers[10] = value
			return
		return self.registers[10]
	
	def pc(self, value: bytes=None):
		"""
		Program Counter
		Point to next instruction to run.
		Never directly set this register using assembly code. 
		"""
		if value is not None:
			if type(value) == bytes:
				self.registers[11] = int.from_bytes(value)
			else:
				self.registers[11] = value
			return
		return self.registers[11]
	
	def __str__(self) -> str:
		return f"""registers = (
		r0: {self.get_reg(int.to_bytes(0))},
		r1: {self.get_reg(int.to_bytes(1))},
		r2: {self.get_reg(int.to_bytes(2))},
		r3: {self.get_reg(int.to_bytes(3))},
		r4: {self.get_reg(int.to_bytes(4))},
		r5: {self.get_reg(int.to_bytes(5))},
		sp: {self.get_reg(int.to_bytes(6))},
		fp: {self.get_reg(int.to_bytes(7))},
		sl: {self.get_reg(int.to_bytes(8))},
		z: {self.get_reg(int.to_bytes(9))},
		sb: {self.get_reg(int.to_bytes(10))},
		pc: {self.get_reg(int.to_bytes(11))}\n)"""