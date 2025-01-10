from inst import Inst
import sys

class Process:
    def __init__(self):
        self.pc = 0

        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.sp = 0
        self.flags = 0

KERNEL_MEMORY_AMOUNT = 0x0F00

class Memory:
    def __init__(self, size: int):
        self.data = [0] * size

    def __getitem__(self, address: int) -> int:
        self.check_access(address)
        return self.data[address]

    def __setitem__(self, address: int, value: int) -> None:
        self.check_access(address)
        self.data[address] = value

    def check_access(self, address: int) -> None:
        if not privilegedMode and address <= KERNEL_MEMORY_AMOUNT:
            raiseInterrupt(2)

mem = Memory(65536)
privilegedMode = True

processes = [Process()]

proc = processes[0]

def raiseInterrupt(interrupt: int) -> True:
    global mem, privilegedMode, proc

    privilegedMode = True
    proc = processes[0]
    proc.a = interrupt

    return True

def processInst(inst: int, operands: list) -> None:
    global mem, privilegedMode

    if inst in [Inst.RTI, Inst.CLP, Inst.SWT]:
        return raiseInterrupt(1)

    match Inst(inst):
        case Inst.NOP:
            pass  # No operation

        case Inst.LDA:
            proc.a = mem[operands[0]]

        case Inst.LDX:
            proc.x = mem[operands[0]]

        case Inst.LDY:
            proc.y = mem[operands[0]]

        case Inst.STA:
            mem[operands[0]] = proc.a

        case Inst.STX:
            mem[operands[0]] = proc.x

        case Inst.STY:
            mem[operands[0]] = proc.y

        case Inst.TAX:
            proc.x = proc.a

        case Inst.TAY:
            proc.y = proc.a

        case Inst.TSX:
            proc.x = proc.sp

        case Inst.TXA:
            proc.a = proc.x

        case Inst.TXS:
            proc.sp = proc.x

        case Inst.TYA:
            proc.a = proc.y

        case Inst.INC:
            proc.a += 1

        case Inst.INX:
            x += 1

        case Inst.INY:
            proc.y += 1

        case Inst.DEC:
            proc.a -= 1

        case Inst.DEX:
            proc.x -= 1

        case Inst.DEY:
            proc.y -= 1

        case Inst.ADD:
            proc.a += mem[operands[0]]

        case Inst.SUB:
            proc.a -= mem[operands[0]]

        case Inst.MUL:
            proc.a *= mem[operands[0]]

        case Inst.DIV:
            proc.a //= mem[operands[0]]

        case Inst.MOD:
            proc.a %= mem[operands[0]]

        case Inst.AND:
            proc.a &= mem[operands[0]]

        case Inst.ORA:
            proc.a |= mem[operands[0]]

        case Inst.XOR:
            proc.a ^= mem[operands[0]]

        case Inst.SHL:
            proc.a <<= 1

        case Inst.LSR:
            proc.a >>= 1

        case Inst.ROL:
            proc.a = (proc.a << 1) | (proc.a >> 7)

        case Inst.ROR:
            proc.a = (proc.a >> 1) | (proc.a << 7)

        case Inst.BIT:
            proc.flags = (proc.a & mem[operands[0]]) != 0

        case Inst.JMP:
            proc.pc = operands[0]

        case Inst.JSR:
            mem[proc.sp] = proc.pc
            proc.sp -= 1
            proc.pc = operands[0]

        case Inst.RTS:
            proc.sp += 1
            proc.pc = mem[proc.sp]

        case Inst.BCC:
            if not (proc.flags & 0x01):
                proc.pc = operands[0]

        case Inst.BCS:
            if proc.flags & 0x01:
                proc.pc = operands[0]

        case Inst.BEQ:
            if proc.flags & 0x02:
                proc.pc = operands[0]

        case Inst.BMI:
            if proc.flags & 0x80:
                proc.pc = operands[0]

        case Inst.BNE:
            if not (proc.flags & 0x02):
                proc.pc = operands[0]

        case Inst.BPL:
            if not (proc.flags & 0x80):
                proc.pc = operands[0]

        case Inst.BVC:
            if not (proc.flags & 0x40):
                proc.pc = operands[0]

        case Inst.BVS:
            if proc.flags & 0x40:
                proc.pc = operands[0]

        case Inst.SEC:
            proc.flags |= 0x01

        case Inst.SED:
            proc.flags |= 0x08

        case Inst.CLC:
            proc.flags &= ~0x01

        case Inst.CLD:
            proc.flags &= ~0x08

        case Inst.CLV:
            proc.flags &= ~0x40

        case Inst.PHA:
            mem[proc.sp] = proc.a
            proc.sp -= 1

        case Inst.PHP:
            mem[proc.sp] = proc.flags
            proc.sp -= 1

        case Inst.PLA:
            proc.sp += 1
            proc.a = mem[proc.sp]

        case Inst.PLP:
            proc.sp += 1
            proc.flags = mem[proc.sp]

        case Inst.CMP:
            proc.flags = (proc.a - mem[operands[0]]) == 0

        case Inst.CPX:
            proc.flags = (proc.x - mem[operands[0]]) == 0

        case Inst.CPY:
            proc.flags = (proc.y - mem[operands[0]]) == 0

        case Inst.INT:
            return raiseInterrupt(proc.a)

        case Inst.RTI:
            proc.sp += 1
            proc.pc = mem[proc.sp]

        case Inst.CLP:
            privilegedMode = False

        case Inst.SWT:
            privilegedMode = True

        case Inst.HLT:
            exit(proc.a)

        case Inst.IN:
            proc.a = sys.stdin.read(1)

        case Inst.OUT:
            sys.stdout.write(chr(proc.a))

        case _:
            return raiseInterrupt(0)

def loadFile(filename:str) -> bytes:
    with open(filename,'rb') as f:
        return list(f.read())

def loadExecutable(executable:list[int],offset:int):
    mem[offset:offset+len(executable)] = executable
    return len(executable)

import time as t

def run() -> None:
    while True:
        operandCount = mem[proc.pc]
        print(f'{operandCount} {str(Inst(mem[proc.pc+1])).replace('Inst.','')}')
        processInst(mem[proc.pc+1],mem[proc.pc+2:proc.pc+2+operandCount])

        proc.pc += 1 + operandCount

        t.sleep(0.05)

kernel = loadFile("kernel.bin")
loadExecutable(kernel,0)
run()

