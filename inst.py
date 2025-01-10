from enum import Enum

class Inst(Enum):
    # General instructions
    NOP = 0
    SYSCALL = 1

    # Register operations
    LDA = 2
    LDX = 3
    LDY = 4
    STA = 5
    STX = 6
    STY = 7
    TAX = 8
    TAY = 9
    TSX = 10
    TXA = 11
    TXS = 12
    TYA = 13

    # Arithmetic
    INC = 14
    INX = 15
    INY = 16
    DEC = 17
    DEX = 18
    DEY = 19
    ADD = 20
    SUB = 21
    MUL = 22
    DIV = 23
    MOD = 24

    # Bitwise
    AND = 25
    ORA = 26
    XOR = 27

    # Shift & rotate
    SHL = 28
    LSR = 29
    ROL = 30
    ROR = 31
    BIT = 32

    # Jump operations
    JMP = 33
    JSR = 34
    RTS = 35

    # Branch if -operations
    BCC = 36
    BCS = 37
    BEQ = 38
    BMI = 39
    BNE = 40
    BPL = 41
    BVC = 42
    BVS = 43

    # Flags
    SEC = 44
    SED = 45
    CLC = 46
    CLD = 47
    CLV = 48

    # Stack
    PHA = 49
    PHP = 50
    PLA = 51
    PLP = 52

    # Compare
    CMP = 53
    CPX = 54
    CPY = 55

    # Data Movement
    MOV = 56

    # Privileged instructions
    INT = 57
    RTI = 58
    CLP = 59
    SWT = 60
    HLT = 61

    # External device operations
    IN = 62
    OUT = 63