from enum import Enum, auto

class Inst(Enum):
    # General instructions
    NOP = auto()
    SYSCALL = auto()

    # Register operations
    LDA = auto()
    LDX = auto()
    LDY = auto()
    STA = auto()
    STX = auto()
    STY = auto()
    TAX = auto()
    TAY = auto()
    TSX = auto()
    TXA = auto()
    TXS = auto()
    TYA = auto()

    # Arithmetic
    INC = auto()
    INA = auto()
    INX = auto()
    INY = auto()
    DEC = auto()
    DEX = auto()
    DEY = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()

    # Bitwise
    AND = auto()
    ORA = auto()
    XOR = auto()

    # Shift & rotate
    SHL = auto()
    LSR = auto()
    ROL = auto()
    ROR = auto()
    BIT = auto()

    # Jump operations
    JMP = auto()
    JSR = auto()
    RTS = auto()

    # Branch if -operations
    BCC = auto()
    BCS = auto()
    BEQ = auto()
    BMI = auto()
    BNE = auto()
    BPL = auto()
    BVC = auto()
    BVS = auto()

    # Flags
    SEC = auto()
    SED = auto()
    CLC = auto()
    CLD = auto()
    CLV = auto()

    # Stack
    PHA = auto()
    PHP = auto()
    PLA = auto()
    PLP = auto()

    # Compare
    CMP = auto()
    CPX = auto()
    CPY = auto()

    # Data Movement
    MOV = auto()

    # Privileged instructions
    INT = auto()
    RTI = auto()
    CLP = auto()
    SWT = auto()
    HLT = auto()

    # External device operations
    IN = auto()
    OUT = auto()
