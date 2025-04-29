print("===== SCRIPT EXECUTION STARTED =====")

from inst import Inst
from addressing import AddressingMode, decode_addressing_mode
import sys

# Debug toggle - set to True to enable debug print statements, False to disable them
DEBUG = True

class Process:
    __slots__ = ['pc','a','b','c','d','e','f','x','y','z','sp','flags','data_section']
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
        self.data_section = 0  # Pointer to the data section for this process

    def __hash__(self):
        return hash(f'{self.a}{self.b}{self.c}{self.d}{self.e}{self.f}{self.x}{self.y}{self.z}{self.sp}{self.flags}{mem.data}')

all_registers = [
    'a', 'b', 'c', 'd', 'e', 'f', 'x', 'y', 'z', 'sp'
]

KERNEL_MEMORY_AMOUNT = 0x0F00

class Memory:
    __slots__ = ['data']
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

def getRegisterValue(regNum):
    """Get the value from a register based on its number."""
    if regNum == 0:
        return proc.a
    elif regNum == 1:
        return proc.b
    elif regNum == 2:
        return proc.c
    elif regNum == 3:
        return proc.d
    elif regNum == 4:
        return proc.e
    elif regNum == 5:
        return proc.f
    elif regNum == 6:
        return proc.x
    elif regNum == 7:
        return proc.y
    elif regNum == 8:
        return proc.z
    elif regNum == 9:
        return proc.sp
    else:
        return 0  # Default case

def setRegisterValue(regNum, value):
    """Set the value of a register based on its number."""
    if regNum == 0:
        proc.a = value
    elif regNum == 1:
        proc.b = value
    elif regNum == 2:
        proc.c = value
    elif regNum == 3:
        proc.d = value
    elif regNum == 4:
        proc.e = value
    elif regNum == 5:
        proc.f = value
    elif regNum == 6:
        proc.x = value
    elif regNum == 7:
        proc.y = value
    elif regNum == 8:
        proc.z = value
    elif regNum == 9:
        proc.sp = value

def getOperandValue(high_byte, low_byte, is_jump=False):
    """
    Decode an operand pair and get the actual value based on addressing mode.
    
    Args:
        high_byte: Byte with addressing mode in top 2 bits, high value bits in bottom 6
        low_byte: Byte containing low 8 bits of value
        is_jump: Boolean indicating if this is for a jump/branch instruction
        
    Returns:
        The resolved value based on addressing mode
    """
    mode, value = decode_addressing_mode(high_byte, low_byte)
    
    # Print for debugging
    if DEBUG:
        print(f"Decoded mode: {mode}, value: {value} from bytes: {high_byte}, {low_byte}")
    
    if mode == AddressingMode.REGISTER:
        # Register addressing: Get value from the register
        return getRegisterValue(value)
    elif mode == AddressingMode.IMMEDIATE:
        # Immediate addressing: Return the value directly
        return value
    elif mode == AddressingMode.ABSOLUTE:
        # Absolute addressing: For JMP instructions, return the address directly
        # For other instructions, read from memory at the address
        if is_jump:
            return value  # Return the address value directly for jumps and branches
        else:
            return mem[value]  # For non-jump instructions, read from memory
    elif mode == AddressingMode.RELATIVE:
        # Relative addressing: Calculate address relative to PC
        return proc.pc + value
    
    # Default case (shouldn't happen)
    return value

def getTargetAddress(high_byte, low_byte):
    """
    For store operations, get the target address based on addressing mode.
    
    Args:
        high_byte: Byte with mode in top 2 bits, high value bits in bottom 6
        low_byte: Byte containing low 8 bits of value
        
    Returns:
        The target memory address or register number
    """
    mode, value = decode_addressing_mode(high_byte, low_byte)
    
    if mode == AddressingMode.REGISTER:
        # Return register number for setting
        return ("register", value)
    elif mode == AddressingMode.ABSOLUTE:
        # Return memory address for absolute mode
        return ("memory", value)
    elif mode == AddressingMode.RELATIVE:
        # Calculate relative address
        return ("memory", proc.pc + value)
    else:
        # Immediate mode doesn't make sense for targets
        if DEBUG:
            print(f"Warning: Invalid addressing mode for target: {mode}")
        return ("memory", 0)  # Default to memory address 0

def raiseInterrupt(interrupt: int) -> True:
    global mem, privilegedMode, proc

    privilegedMode = True
    proc = processes[0]
    proc.a = interrupt

    return True

def processInst(inst: int, operands: list) -> bool:
    global mem, privilegedMode

    if inst in [Inst.RTI, Inst.CLP, Inst.SWT]:
        return raiseInterrupt(1)

    match Inst(inst):
        case Inst.NOP:
            pass  # No operation
            
        case Inst.LDA:
            # Handle operands as pairs of bytes (high byte, low byte)
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.a = getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")
                proc.a = 0

        case Inst.LDX:
            # Handle operands as pairs of bytes (high byte, low byte)
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.x = getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")
                proc.x = 0

        case Inst.LDY:
            # Handle operands as pairs of bytes (high byte, low byte)
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.y = getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")
                proc.y = 0

        case Inst.STA:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                target_type, target = getTargetAddress(high_byte, low_byte)
                if target_type == "memory":
                    mem[target] = proc.a
                elif target_type == "register":
                    setRegisterValue(target, proc.a)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.STX:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                target_type, target = getTargetAddress(high_byte, low_byte)
                if target_type == "memory":
                    mem[target] = proc.x
                elif target_type == "register":
                    setRegisterValue(target, proc.x)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.STY:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                target_type, target = getTargetAddress(high_byte, low_byte)
                if target_type == "memory":
                    mem[target] = proc.y
                elif target_type == "register":
                    setRegisterValue(target, proc.y)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

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
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                target_type, target = getTargetAddress(high_byte, low_byte)
                if target_type == "memory":
                    mem[target] += 1
                elif target_type == "register":
                    value = getRegisterValue(target) + 1
                    setRegisterValue(target, value)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.INA:
            proc.a += 1

        case Inst.INX:
            proc.x += 1

        case Inst.INY:
            proc.y += 1

        case Inst.DEC:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                target_type, target = getTargetAddress(high_byte, low_byte)
                if target_type == "memory":
                    mem[target] -= 1
                elif target_type == "register":
                    value = getRegisterValue(target) - 1
                    setRegisterValue(target, value)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.DEX:
            proc.x -= 1

        case Inst.DEY:
            proc.y -= 1

        case Inst.ADD:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.a += getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.SUB:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.a -= getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.MUL:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.a *= getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.DIV:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                divisor = getOperandValue(high_byte, low_byte)
                if divisor == 0:
                    if DEBUG:
                        print("Warning: Division by zero")
                    return raiseInterrupt(3)  # Assuming interrupt 3 is for division by zero
                proc.a //= divisor
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.MOD:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                divisor = getOperandValue(high_byte, low_byte)
                if divisor == 0:
                    if DEBUG:
                        print("Warning: Modulo by zero")
                    return raiseInterrupt(3)  # Assuming interrupt 3 is for division by zero
                proc.a %= divisor
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.AND:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.a &= getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.ORA:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.a |= getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.XOR:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.a ^= getOperandValue(high_byte, low_byte)
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.SHL:
            proc.a <<= 1

        case Inst.LSR:
            proc.a >>= 1

        case Inst.ROL:
            proc.a = (proc.a << 1) | (proc.a >> 7)

        case Inst.ROR:
            proc.a = (proc.a >> 1) | (proc.a << 7)

        case Inst.BIT:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                proc.flags = (proc.a & getOperandValue(high_byte, low_byte)) != 0
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.JMP:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                target = getOperandValue(high_byte, low_byte, is_jump=True)
                if DEBUG:
                    print(f"jumped to {target}")
                proc.pc = target
                return True
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")
                return False

        case Inst.JSR:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                mem[proc.sp] = proc.pc
                proc.sp -= 1
                proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                return True
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")
                return False

        case Inst.RTS:
            proc.sp += 1
            proc.pc = mem[proc.sp]
            return True

        case Inst.BCC:
            if not (proc.flags & 0x01):
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.BCS:
            if proc.flags & 0x01:
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.BMI:
            if proc.flags & 0x80:
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.BNE:
            if not (proc.flags & 0x02):  # If Zero flag is clear
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.BEQ:
            if proc.flags & 0x02:  # If Zero flag is set
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.BPL:
            if not (proc.flags & 0x80):
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.BVC:
            if not (proc.flags & 0x40):
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.BVS:
            if proc.flags & 0x40:
                if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                    high_byte, low_byte = operands[0]
                    proc.pc = getOperandValue(high_byte, low_byte, is_jump=True)
                    return True
                else:
                    if DEBUG:
                        print(f"Warning: Expected operand pair but got {operands[0]}")
            return False

        case Inst.SEC:
            proc.flags |= 0x01  # Set Carry flag

        case Inst.SED:
            proc.flags |= 0x08  # Set Decimal flag

        case Inst.CLC:
            proc.flags &= ~0x01  # Clear Carry flag

        case Inst.CLD:
            proc.flags &= ~0x08  # Clear Decimal flag

        case Inst.CLV:
            proc.flags &= ~0x40  # Clear Overflow flag

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
            # Get value from first operand
            value1 = proc.a  # In most processors, CMP compares accumulator with operand
            
            # Get value from operand using the new 2-byte format
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                value2 = getOperandValue(high_byte, low_byte)
                
                # Calculate comparison result
                result = value1 - value2
                
                # Set flags based on comparison result
                # Clear all flags first
                proc.flags = 0
                
                # Zero flag (0x02): Set if values are equal
                if result == 0:
                    proc.flags |= 0x02
                
                # Carry flag (0x01): Set if value1 >= value2
                if value1 >= value2:
                    proc.flags |= 0x01
                
                # Negative flag (0x80): Set if result is negative
                if result < 0:
                    proc.flags |= 0x80
                
                if DEBUG:
                    print(f"CMP comparing {value1} with {value2}, result: {result}, flags: {bin(proc.flags)}")
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.CPX:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                value1 = proc.x
                value2 = getOperandValue(high_byte, low_byte)
                result = value1 - value2
                
                # Set flags
                proc.flags = 0
                if result == 0:
                    proc.flags |= 0x02  # Zero flag
                if value1 >= value2:
                    proc.flags |= 0x01  # Carry flag
                if result < 0:
                    proc.flags |= 0x80  # Negative flag
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.CPY:
            if isinstance(operands[0], tuple) and len(operands[0]) == 2:
                high_byte, low_byte = operands[0]
                value1 = proc.y
                value2 = getOperandValue(high_byte, low_byte)
                result = value1 - value2
                
                # Set flags
                proc.flags = 0
                if result == 0:
                    proc.flags |= 0x02  # Zero flag
                if value1 >= value2:
                    proc.flags |= 0x01  # Carry flag
                if result < 0:
                    proc.flags |= 0x80  # Negative flag
            else:
                if DEBUG:
                    print(f"Warning: Expected operand pair but got {operands[0]}")

        case Inst.INT:
            return raiseInterrupt(proc.a)

        case Inst.RTI:
            proc.sp += 1
            proc.pc = mem[proc.sp]
            return True

        case Inst.CLP:
            privilegedMode = False

        case Inst.SWT:
            privilegedMode = True

        case Inst.HLT:
            exit(proc.a)

        case Inst.IN:
            proc.a = ord(sys.stdin.read(1))

        case Inst.OUT:
            print(chr(proc.a), proc.a)
            # sys.stdout.write(chr(proc.a))

        case _:
            return raiseInterrupt(0)
    
    return False

def loadFile(filename:str) -> bytes:
    with open(filename,'rb') as f:
        return list(f.read())

def loadExecutable(executable:list[int], offset:int):
    # Load the executable into memory
    mem[offset:offset+len(executable)] = executable

    # Let's read the header properly
    # First 2 bytes are the data section pointer in big-endian format
    data_section_offset = (mem[offset] << 8) | mem[offset+1]
    print(f"Data section pointer from header: {data_section_offset}")

    # Store the absolute address of the data section
    proc.data_section = offset + data_section_offset

    # Now, code section should start right after the 2-byte header
    code_start = offset + 2

    # Memory dump for debugging
    print("Memory dump for analysis:")
    print("Header bytes:")
    print(f"mem[{offset}] = {mem[offset]} (high byte)")
    print(f"mem[{offset+1}] = {mem[offset+1]} (low byte)")
    print("First few code bytes:")
    for i in range(code_start, code_start + 10):
        print(f"mem[{i}] = {mem[i]}")

    # Start execution at the beginning of code section
    proc.pc = code_start
    print(f"Starting execution at offset: {proc.pc}, data section at: {proc.data_section}")

    return len(executable)

import time as t

def run() -> None:
    print("Starting execution loop...")
    print("Format: PC | OpCount | Instruction | [Args]")

    previous_states = set()

    while True:
        try:
            # For each instruction, we have:
            # [num_args, opcode, arg1, arg2, ...]
            num_args = mem[proc.pc]

            # Safety check - if the operand count is invalid, skip this instruction
            if num_args < 0 or num_args > 10:  # Reasonable limit on operand count
                if DEBUG:
                    print(f"Warning: Invalid operand count {num_args} at address {proc.pc}")
                proc.pc += 1  # Skip this byte and try again
                continue

            # Make sure we have enough bytes for the opcode
            if proc.pc + 1 >= 65536:
                if DEBUG:
                    print(f"Error: Reached end of memory at {proc.pc}")
                break

            opcode = mem[proc.pc + 1]

            # Ensure the opcode is valid
            try:
                inst_name = str(Inst(opcode)).replace("Inst.","")
            except ValueError:
                if DEBUG:
                    print(f"Warning: Invalid opcode {opcode} at address {proc.pc+1}")
                proc.pc += 2  # Skip this instruction and try again
                continue
            
            # Get the operands, ensuring we don't read past the end of memory
            # Each operand is now 2 bytes (mode+high bits, low bits)
            raw_args = mem[proc.pc + 2:min(proc.pc + 2 + num_args*2, 65536)]
            
            # Group bytes into pairs for each operand
            args = []
            for i in range(0, len(raw_args), 2):
                if i+1 < len(raw_args):
                    args.append((raw_args[i], raw_args[i+1]))
                else:
                    # Handle the odd case if we somehow have an odd number of bytes
                    args.append((raw_args[i], 0))
            
            # Debug output with raw bytes and decoded values
            if DEBUG:
                print(f'{proc.pc} | {num_args} | {inst_name} | {raw_args} | Decoded pairs: {args}')
            else:
                print(f'{proc.pc} | {num_args} | {inst_name} | {raw_args}')

            jumped = processInst(opcode, args)

            if not jumped:
                # Move to the next instruction: skip opcount + opcode + args*2 (each operand is 2 bytes)
                proc.pc += 2 + num_args*2
            else:
                if DEBUG:
                    print(f'jumped to {proc.pc}')

                if hash(proc) in previous_states:
                    print('Infinite loop detected! We are in an identical state to a previous one.')
                    if DEBUG:
                        print(hash(proc))
                        print(previous_states)
                    return

                previous_states.add(hash(proc))

            # Slow down execution for debugging
            try: t.sleep(0.05)
            except KeyboardInterrupt:
                return

        except Exception as e:
            print(f"Error during execution: {e}")
            print(f"At position: {proc.pc}, value: {mem[proc.pc]}")
            # Dump surrounding memory for analysis
            print("Memory dump around error point:")
            start = max(0, proc.pc - 5)
            end = min(proc.pc + 10, 65536)
            print(f'Memory from {start} to {end}')
            for i in range(start, end):
                print(mem[i],end=', ')
            print()
            break

print("Starting program...")
try:
    print("Loading kernel.bin...")
    kernel = loadFile("kernel.bin")
    print(f"Kernel loaded, size: {len(kernel)} bytes")
    loadExecutable(kernel, 0)
    print("Running virtual machine...")
    run()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
