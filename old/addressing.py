from enum import IntEnum

class AddressingMode(IntEnum):
    # Each addressing mode gets its own 2-bit value
    REGISTER = 0b00      # Register direct: r0, r1, etc.
    IMMEDIATE = 0b01     # Immediate value: #42
    ABSOLUTE = 0b10      # Absolute memory address: $1000
    RELATIVE = 0b11      # Relative address (for branching): label or +2, -3

def encode_addressing_mode(mode, high_bits, low_byte):
    """
    Encode a value with its addressing mode using a 2-byte format.
    Byte 1: Top 2 bits = addressing mode, bottom 6 bits = high bits of value
    Byte 2: Full byte for low bits of value
    
    Args:
        mode: The addressing mode (2 bits)
        high_bits: The high 6 bits of the value
        low_byte: The low 8 bits of the value
        
    Returns:
        A tuple of two bytes (mode_and_high_byte, low_byte)
    """
    mode_and_high_byte = ((mode & 0x03) << 6) | (high_bits & 0x3F)
    return (mode_and_high_byte, low_byte & 0xFF)

def decode_addressing_mode(high_byte, low_byte=None):
    """
    Decode the addressing mode and value from encoded bytes.
    
    Args:
        high_byte: Byte with mode in top 2 bits, high value bits in bottom 6 bits
        low_byte: Optional byte containing low 8 bits of value
        
    Returns:
        A tuple (addressing_mode, value)
    """
    mode = (high_byte >> 6) & 0x03
    
    if low_byte is not None:
        # 14-bit value format (6 bits from high byte, 8 bits from low byte)
        value = ((high_byte & 0x3F) << 8) | (low_byte & 0xFF)
    else:
        # 6-bit value format (for backward compatibility)
        value = high_byte & 0x3F
        
    return (mode, value)

def get_value_from_operand(proc, mem, mode, value):
    """
    Resolve the actual value based on the addressing mode and value.
    
    Args:
        proc: The current process context
        mem: The memory object
        mode: The addressing mode (AddressingMode enum value)
        value: The value associated with that addressing mode
        
    Returns:
        The resolved value
    """
    if mode == AddressingMode.REGISTER:
        # Register addressing: Get value from the register
        return getRegisterValue(proc, value)
    elif mode == AddressingMode.IMMEDIATE:
        # Immediate addressing: Return the value directly
        return value
    elif mode == AddressingMode.ABSOLUTE:
        # Absolute addressing: Read from memory at the specified address
        return mem[value]
    elif mode == AddressingMode.RELATIVE:
        # Relative addressing: Calculate address relative to PC
        return proc.pc + value
    
    # Default case (shouldn't happen)
    return value

def getRegisterValue(proc, regNum):
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
