from errorMessage import ErrorMessage
from colorama import Fore

class Operations:

    def __init__(self, process) -> None:
        self.process = process

    def adr(self, reg, addr):
        """
        Get address of label
        reg <- addr(<label>)
        reg: 1 byte
        addr: 4 bytes
        """
        pass

    def mov(self, reg1, reg2):
        """
        Load data from register
        reg1 <- reg2
        reg1: 1 byte
        reg2: 1 byte
        """
        reg2_val = self.process.registers.get_reg(reg2)
        self.process.registers.set_reg(reg1, reg2_val)

    def str(self, reg1, reg2):
        """
        Store word (int) using register indirect addressing
        memory[reg2] <- reg1
        reg1: 1 byte
        reg2: 1 byte
        """
        pass

    def strb(self, reg1, reg2):
        """
        Store byte using register indirect addressing
        memory[reg2] <- byte(memory[reg1])
        reg1: 1 byte
        reg2: 1 byte
        """
        pass

    def ldr(self, reg1, reg2):
        """
        Load word (int) using register indirect addressing
        reg1 <- memory[reg2]
        reg1: 1 byte
        reg2: 1 byte
        """
        pass

    def ldrb(self, reg1, reg2):
        """
        Load byte using register indirect addressing
        reg1 <- byte(memory[reg2])
        reg1: 1 byte
        reg2: 1 byte
        """
        pass

    def bx(self, reg):
        """
        Jump to address in register
        PC <- reg
        reg: 1 byte
        """
        new_pc: int = int.from_bytes(self.process.registers.get_reg(reg))-6
        self.process.registers.pc(new_pc)
        if self.process.verbose:
            self.process.verbose_results.add(f'PC <- reg{int.from_bytes(reg)} ({new_pc})')

    def b(self, lbl):
        """
        Jump to label
        PC <- address(label)
        lbl: 4 bytes
        """
        new_pc: int = int.from_bytes(lbl)-6
        self.process.registers.pc(new_pc)
        if self.process.verbose:
            self.process.verbose_results.add(f'PC <- address ({new_pc})')

    def bne(self, lbl):
        """
        Jump to label if Z register is not zero
        PC <- address(label) if Z != 0
        lbl: 4 bytes
        """
        z: int = int.from_bytes(self.process.registers.z())
        if z != 0:
            addr = int.from_bytes(lbl) - 6
            self.process.registers.pc(addr)
            if self.process.verbose:
                self.process.verbose_results.add(f'PC <- address ({addr})')
            return
        if self.process.verbose:
            self.process.verbose_results.add(f'Z == 0')

    def bgt(self, lbl):
        """
        Jump to label if Z register is greater than zero
        PC <- address(label) if Z > 0
        lbl: 4 bytes
        """
        z: int = int.from_bytes(self.process.registers.z())
        if z > 0:
            addr = (int.from_bytes(lbl) - 6) + self.process.pcb.memory_l_limit
            self.process.registers.pc(addr)
            if self.process.verbose:
                self.process.verbose_results.add(f'PC <- address ({addr})')
            return
        if self.process.verbose:
            self.process.verbose_results.add(f'Z not greater than 0, Z == {z}')

    def blt(self, lbl):
        """
        Jump to label if Z register is less than zero
        PC <- address(label) if Z < 0
        lbl: 4 bytes
        """
        z: int = int.from_bytes(self.process.registers.z())
        if z < 0:
            addr = int.from_bytes(lbl) - 6
            self.process.registers.pc(addr)
            if self.process.verbose:
                self.process.verbose_results.add(f'PC <- address ({addr})')
            return
        if self.process.verbose:
            self.process.verbose_results.add(f'Z not less than 0, Z == {z}')

    def beq(self, lbl):
        """
        Jump to label if Z register is equals zero
        PC <- address(label) if Z == 0
        lbl: 4 bytes
        """
        z: int = int.from_bytes(self.process.registers.z())
        if z == 0:
            addr = int.from_bytes(lbl) - 6
            self.process.registers.pc(addr)
            if self.process.verbose:
                self.process.verbose_results.add(f'PC <- address ({addr})')
            return
        if self.process.verbose:
            self.process.verbose_results.add(f'Z != 0, Z == {z}')

    def cmp(self, reg1, reg2):
        """
        Compare <reg1> and <reg2> place result in Z register
        Z <- reg1 - reg2
        reg1: 1 byte
        reg2: 1 byte
        """
        sum: int = int.from_bytes(self.process.registers.get_reg(reg1)) - int.from_bytes(self.process.registers.get_reg(reg2))
        if self.process.verbose:
            self.process.verbose_results.add(f'Z <- result ({sum})')
        self.process.registers.z(int.to_bytes(sum))

    def and_op(self, reg1, reg2):
        """
        Perform an AND operation on <reg1> and <reg2> result in Z register
        Z <- reg1 & reg2
        reg1: 1 byte
        reg2: 1 byte
        """
        pass

    def orr(self, reg1, reg2):
        """
        Perform an OR operation on <reg1> and <reg2> result in Z register
        Z <- reg1 | reg2
        reg1: 1 byte
        reg2: 1 byte
        """
        pass

    def eor(self, reg1, reg2):
        """
        Exclusive OR operation on <reg1> and <reg2> result in Z register
        Z <- reg1 ^ reg2
        reg1: 1 byte
        reg2: 1 byte
        """
        pass

    def add(self, reg1: bytes, reg2: bytes, reg3: bytes) -> None:
        """
        reg1 <- reg2 + reg3
        reg1: 1 byte
        reg2: 1 byte
        reg3: 1 byte
        """
        sum: int = int.from_bytes(self.process.registers.get_reg(reg2)) + int.from_bytes(self.process.registers.get_reg(reg3))
        if self.process.verbose:
            self.process.verbose_results.add(f'reg {reg1} <- result ({sum})')
        self.process.registers.set_reg(reg1, int.to_bytes(sum))

    def sub(self, reg1, reg2, reg3):
        """
        reg1 <- reg2 - reg3
        reg1: 1 byte
        reg2: 1 byte
        reg3: 1 byte
        """
        sum: int = int.from_bytes(self.process.registers.get_reg(reg2)) - int.from_bytes(self.process.registers.get_reg(reg3))
        if self.process.verbose:
            self.process.verbose_results.add(f'reg {reg1} <- result ({sum})')
        self.process.registers.set_reg(reg1, int.to_bytes(sum))

    def mul(self, reg1, reg2, reg3):
        """
        reg1 <- reg2 * reg3
        reg1: 1 byte
        reg2: 1 byte
        reg3: 1 byte
        """
        result: int = int.from_bytes(self.process.registers.get_reg(reg2)) * int.from_bytes(self.process.registers.get_reg(reg3))
        if self.process.verbose:
            self.process.verbose_results.add(f'reg {reg1} <- result ({result})')
        self.process.registers.set_reg(reg1, int.to_bytes(result))

    def div(self, reg1, reg2, reg3):
        """
        reg1 <- reg2 / reg3
        reg1: 1 byte
        reg2: 1 byte
        reg3: 1 byte
        """
        result: int = int.from_bytes(self.process.registers.get_reg(reg2)) / int.from_bytes(self.process.registers.get_reg(reg3))
        if self.process.verbose:
            self.process.verbose_results.add(f'reg {reg1} <- result ({result})')
        self.process.registers.set_reg(reg1, int.to_bytes(result))

    def swi(self, imm: bytes):
        """
        Software Interrupt
        run interrupt imm
        imm: 4 bytes
        """
        imm_int: int = int.from_bytes(imm)
        if self.process.verbose:
            self.process.verbose_results.add(f'Software Interrupt {imm_int}')
        match imm_int:
            case 0:
                self.process.shell.user_mode()
                self.process.pcb.waiting()
                input('Enter input: ')
                self.process.pcb.ready()
                self.process.shell.kernal_mode()
            case 1:
                self.process.shell.user_mode()
                self.process.pcb.waiting()
                z: int = int.from_bytes(self.process.registers.z())
                print(Fore.BLUE, end='')
                print(f'Z: {z}')
                self.process.pcb.ready()
                self.process.shell.kernal_mode()
            case 3:
                self.process.errors.append(ErrorMessage('SwiError', 'SWI code {imm_int}'))
            case 4: # wait system call
                print(Fore.BLUE, end='')
                print('Waiting...')
        self.process.hit_swi = True # added this

    def bl(self, lbl):
        """
        Jump to label and link (place the PC of the next instruction into a register)
        PC <- address(lbl)
        R5 <- PC+6
        lbl: 4 bytes
        """
        new_pc: int = int.from_bytes(lbl) - 6
        self.process.registers.pc(new_pc)
        self.process.registers.r5(new_pc + 6)
        if self.process.verbose:
            self.process.verbose_results.add(f'PC <- address ({new_pc})')
            self.process.verbose_results.add(f'R5 <- {new_pc} + 6')

    def mvi(self, reg: bytes, imm: bytes):
        """
        Load register with immediate value
        reg1 <- imm
        reg1: 1 byte
        imm: 4 bytes
        """
        imm_int: int = int.from_bytes(imm)
        self.process.registers.set_reg(reg, int.to_bytes(imm_int))
        if self.process.verbose:
            self.process.verbose_results.add(f'reg{int.from_bytes(reg)} <- {imm_int}')
        