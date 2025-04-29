<<<<<<<< Updated upstream:main.py
from inspect import signature
========
from old.inst import Inst
>>>>>>>> Stashed changes:old/main.py
import sys

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

KERNEL_MEMORY_AMOUNT = 0x0F00

class Memory:
    __slots__ = ['data', 'allocations']
    def __init__(self, size: int):
        self.data = [0] * size

        # List of tuples of (procId, start, end)
        self.allocations = []

    def __getitem__(self, address: int) -> int:
        self.check_access(address)
        return self.data[address]

    def __setitem__(self, address: int, value: int) -> None:
        self.check_access(address)
        self.data[address] = value

    def check_access(self, address: int) -> None:
        # For kernel mode, allow all access
        if state.privilegedMode:
            return

        # For user mode, check if the address is in the process's allocated memory
        current_process_id = next(pid for pid, p in state.processes.items() if p is state.proc)
        valid_access = False

        for proc_id, start, end in self.allocations:
            if proc_id == current_process_id and start <= address < end:
                valid_access = True
                break

        if not valid_access:
            # Auto-allocate memory for the process
            self.allocate(current_process_id, address, 1)
            return  # Allow access after allocation

    def allocate(self, process_id: int, address: int, size: int = 1) -> None:
        """Allocate memory for a process, handling merging with adjacent allocations"""
        end_address = address + size
        
        # Look for adjacent allocations to merge with
        left_allocation = None
        right_allocation = None

        for i, (proc_id, start, end) in enumerate(self.allocations):
            if proc_id == process_id:
                if end == address:  # Adjacent on left
                    left_allocation = i
                if start == end_address:  # Adjacent on right
                    right_allocation = i

        if left_allocation is not None and right_allocation is not None:
            # Merge both left and right allocations
            left_proc_id, left_start, left_end = self.allocations[left_allocation]
            right_proc_id, right_start, right_end = self.allocations[right_allocation]
            new_allocation = (process_id, left_start, right_end)
            # Remove in reverse order to avoid index issues
            self.allocations.pop(max(left_allocation, right_allocation))
            self.allocations.pop(min(left_allocation, right_allocation))
            self.allocations.append(new_allocation)
        elif left_allocation is not None:
            # Extend left allocation
            proc_id, start, end = self.allocations[left_allocation]
            self.allocations[left_allocation] = (proc_id, start, end_address)
        elif right_allocation is not None:
            # Extend right allocation
            proc_id, start, end = self.allocations[right_allocation]
            self.allocations[right_allocation] = (proc_id, address, end)
        else:
            # Create new allocation for this address range
            self.allocations.append((process_id, address, end_address))

    def unallocate(self, process_id: int) -> None:
        """Free all memory allocations for a specific process"""
        self.allocations = [alloc for alloc in self.allocations if alloc[0] != process_id]



# State
class State:
    def __init__(self):
        # Use a dict to have indexes remain the same even if processes die
        processes = {0: Process()}
        proc = processes[0]

        mem = Memory(0xFFFFF)

        privilegedMode = True

    def contextSwitch(self, procId:int) -> None:
        global mem, privilegedMode, proc

        if procId < 0 or procId >= len(self..processes):
            raiseInterrupt(3)

        self.proc = self.processes[procId]

        return True

    def raiseInterrupt(self, interrupt: int) -> True:
        """
            Raise an interrupt and hand control to the kernel.

            ## Interrupts:
            - 0: Syscall
            - 1: Sigill (Illegal instruction)
            - 2: Memory access violation
            - 3: Invalid process ID
            - 4: Invalid operand count
        """

        self.contextSwitch(0)
        self.privilegedMode = True
        self.proc.a = interrupt

        return True

state = State()

instructions = {}
def inst(name):
    def inner(func):
        instructions[name] = func
        return func
    return inner

def execInstr(inst, args):
    if inst not in instructions:
        raiseInterrupt(1) # Invalid instruction
    try:
        return instructions[inst](*args)
    except TypeError as e:
        raiseInterrupt(4) # Invalid operand count

def loadExecutable(path: str) -> int:
    with open(path, 'rb') as f:
        data = f.read()

    # Find a spot to load the executable into

def run():
    ...

