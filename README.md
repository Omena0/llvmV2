
# Instructions V2

```md
# INCREMENT / DECREMENT
INCA - A++
INCX - X++
INCY - Y++

DECA - A--
DECX - X--
DECY - Y--

# ADD / SUBSTRACT
ADDX - A += X
ADDY - A += Y

SUBX - A -= X
SUBY - A -= Y

# SUM / DIFFERENCE
SUM - A = X + Y
DIF - A = X - Y

# MEMORY
LDA - A = mem[A]
LDX - X = mem[A]
LDY - Y = mem[A]

STA - mem[A] = A
STX - mem[A] = X
STY - mem[A] = Y

MOV - mem[Y] = mem[X]



# BIT SHIFT
ROL - A = A << 1
ROR - A = A >> 1

# BITWISE LOGIC
AND - A = X & Y
ORA - A = X | Y
XOR - A = X ^ Y

# STACK
PSH - push(A), sp++
POP - A = pop(), sp--

# COMPARE & JUMP
CMP - A = X \<op1\> Y
JMP - jump(A)
JNZ - if not A: jump(X)

# INTERRUPT
INT - interrupt(A,X,Y)

```
