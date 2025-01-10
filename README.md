
# computer

## Interrupts

```md
0: SIGILL
1: Privilege violation
2: Memory violation
```

## Instructions

```md
Instructions by Name

# General instructions
NOP: no operation
SYSCALL: system call

# Register operations
LDA: load accumulator
LDX: load x
LDY: load y
STA: store accumulator
STX: store x
STY: store y
TAX: transfer accumulator -> x
TAY: transfer accumulator -> y
TSX: transfer stack pointer -> x
TXA: transfer x -> accumulator
TXS: transfer x -> stack pointer
TYA: transfer y -> accumulator

# Arithmetic
INC: increment
INX: increment x
INY: increment y
DEC: decrement
DEX: decrement x
DEY: decrement y
ADD: add
SUB: subtract
MUL: multiply
DIV: divide
MOD: modulo

# Bitwise
AND: and
ORA: or accumulator
XOR: xor with accumulator

# Shift & rotate
SHL: shift left
LSR: shift right
ROL: rotate left
ROR: rotate right
BIT: bit test

# Jump operations
JMP: jump
JSR: jump subroutine
RTS: return from subroutine

# Branch if -operations
BCC: branch if carry clear
BCS: branch if carry set
BEQ: branch if equal
BMI: branch if minus
BNE: branch if not equal
BPL: branch if on plus
BVC: branch if overflow set
BVS: branch if overflow clear

# Flags
SEC: set carry
SED: set decimal
CLC: clear carry
CLD: clear decimal
CLV: clear overflow

# Stack
PHA: push accumulator
PHP: push processor status (sr)
PLA: pull accumulator
PLP: pull processor status (sr)

# Compare
CMP: compare with accumulator
CPX: compare with x
CPY: compare with y

# Data Movement
MOV: move data from source to destination

## Privileged instructions
INT: interrupt
RTI: return from interrupt
CLP: clear privileged mode
SWT: switch context from accumulator

IN: get input from external device (plugin)
OUT: return from external device (plugin)
```
