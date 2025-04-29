from inst import Inst
from addressing import AddressingMode
import shlex
import sys
import os

def read_file(filename):
    with open(filename) as f:
        return f.read()

def write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def find_dependency(filename, dir='.', debug_include=False):
    result = ''
    if debug_include:
        print(f'[INCLUDE] {"    " * dir.count("/")}{dir.split("/")[-1]}')
    try:
        for item in os.listdir(dir):
            if item == filename:
                result = os.path.join(dir, item)
            elif os.path.isdir(os.path.join(dir, item)):
                result = find_dependency(filename, os.path.join(dir, item), debug_include)
            elif debug_include:
                print(f'[INCLUDE]     {"    " * dir.count("/")}{item}')
    except Exception:
        pass
    return result

def get_indent(line):
    return len(line) - len(line.lstrip(' '))

def process_asm_to_int(p, include_path='include', debug_include=False):
    out = []
    data_section = []
    text_section = []
    labels = {}
    pos = 0
    in_data_section = False
    in_text_section = False
    lines = p.split('\n')
    i = -1

    while i + 1 < len(lines):
        i += 1
        line = lines[i].split(';;')[0]
        if not line:
            continue

        step = 0
        indent = get_indent(line)

        if line.startswith('.'):
            print(f'section {line}')
            section = line
            continue

        line = line.strip()

        if section == '.data':
            print(f'Line: {line}')
            if line.endswith(':'):
                label = line.removesuffix(':')
                labels[label] = pos

            elif line.startswith('.ascii'):
                string_literal = line.split('.ascii')[1].strip().removeprefix('"').split('"')[0]
                print(string_literal)
                for char in string_literal:
                    data_section.append(f'db {ord(char)}')
                    pos += 1
                data_section.append('db 0')  # Null terminator
                pos += 1
        elif section == '.text':
            if line.endswith(':'):
                label = line[:-1]
                # Store the absolute position in the text section
                # We'll use this for calculating jump targets later
                labels[label] = pos
                print(f"{label}: {pos} (in text section)")

            elif line.startswith('#'):
                parts = line.split()
                if parts[0] == '#define':
                    labels[parts[1]] = ' '.join(parts[2:])
                elif parts[0] == '#include':
                    name = parts[1].strip('"\'<>')
                    path = find_dependency(name, include_path, debug_include)
                    if not path:
                        raise FileNotFoundError(f'Dependency "{name}" could not be found.')
                    p += '\n' + read_file(path) + '\n'
            else:
                # Strip comments from the line before parsing
                if '#' in line:
                    line = line.split('#')[0].strip()
                opcode, *args = shlex.split(line.replace(',', ' '))
                step += 1
                final_args = []
                for arg in args:
                    arg = arg.strip()
                    # Determine addressing mode based on prefix or format
                    if arg.startswith('#'):
                        # Immediate mode: #42
                        value = arg[1:]
                        if value.startswith('0b'):
                            value = str(int(value[2:], 2))
                        elif value.startswith('0x'):
                            value = str(int(value[2:], 16))
                        # Store mode and value (will be encoded during binary generation)
                        final_args.append(f"{int(AddressingMode.IMMEDIATE)}")
                        final_args.append(value)
                        step += 1  # Extra step for the added value
                    elif arg.startswith('$'):
                        # Absolute memory addressing: $1000
                        value = arg[1:]
                        if value.startswith('0b'):
                            value = str(int(value[2:], 2))
                        elif value.startswith('0x'):
                            value = str(int(value[2:], 16))
                        final_args.append(f"{int(AddressingMode.ABSOLUTE)}")
                        final_args.append(value)
                        step += 1
                    elif arg.startswith('r') and arg[1:].isdigit():
                        # Register addressing: r0, r1, etc.
                        reg_num = arg[1:]
                        # With 14-bit values, we can have up to 16384 registers
                        if int(reg_num) > 16383:  # 2^14 - 1
                            print(f"Warning: Register number {reg_num} exceeds 14-bit limit (0-16383). Truncating to {int(reg_num) & 0x3FFF}")
                            reg_num = str(int(reg_num) & 0x3FFF)
                        final_args.append(f"{int(AddressingMode.REGISTER)}")
                        final_args.append(reg_num)
                        step += 1
                    elif arg in labels:
                        # Label reference (could be absolute or relative)
                        # For now, treat as absolute
                        final_args.append(f"{int(AddressingMode.ABSOLUTE)}")
                        final_args.append(str(labels[arg]))
                        step += 1
                    elif arg.startswith('0b'):
                        # Binary literals without prefix - treat as immediate
                        value = int(arg[2:], 2) & 0x3FFF  # Ensure 14-bit value
                        final_args.append(f"{int(AddressingMode.IMMEDIATE)}")
                        final_args.append(str(value))
                        step += 1
                    elif arg.startswith('0x'):
                        # Hex literals without prefix - treat as immediate
                        value = int(arg[2:], 16) & 0x3FFF  # Ensure 14-bit value
                        final_args.append(f"{int(AddressingMode.IMMEDIATE)}")
                        final_args.append(str(value))
                        step += 1
                    elif not arg.isnumeric():
                        # String or symbol - encode as absolute address for now
                        final_args.append(f"{int(AddressingMode.ABSOLUTE)}")
                        final_args.append(f'"{arg}"')
                        step += 1
                    else:
                        # Numeric literals - treat as immediate
                        value = int(arg) & 0x3FFF  # Ensure 14-bit value
                        final_args.append(f"{int(AddressingMode.IMMEDIATE)}")
                        final_args.append(str(value))
                        step += 1

                if opcode == 'syscall':
                    opcode = 'lda 0b0'
                    step += 1
                elif opcode in ['beq', 'bne', 'bnz']:
                    if 'ret' in p:
                        # Use proper addressing modes (register mode = 0) instead of binary literals
                        text_section.append(f'lda {int(AddressingMode.REGISTER)} 7')  # Register 7
                        text_section.append(f'psh {int(AddressingMode.REGISTER)} 0')  # Push from register 0
                        text_section.append(f'lda {int(AddressingMode.REGISTER)} 6')  # Load to register 6
                        text_section.append(f'lda {int(AddressingMode.ABSOLUTE)} {final_args[0]}')  # Load target address as absolute
                        # Use register addressing mode (0) for operand - only use register 6
                        text_section.append(f'{opcode} {int(AddressingMode.REGISTER)} 6')
                        text_section.append(f'pop {int(AddressingMode.REGISTER)} 0')
                        opcode = None  # Skip adding another instruction at the end
                        step += 12
                    else:
                        # Use proper addressing modes (register mode = 0) for simpler case
                        text_section.append(f'lda {int(AddressingMode.REGISTER)} 6')  # Load to register 6
                        text_section.append(f'lda {int(AddressingMode.ABSOLUTE)} {final_args[0]}')  # Load target address as absolute
                        # Use register addressing mode (0) for operand - only use register 6
                        text_section.append(f'{opcode} {int(AddressingMode.REGISTER)} 6')
                        opcode = None  # Skip adding another instruction at the end
                        step += 3

                elif opcode == 'cmp':
                    # Special case for CMP instruction to ensure both arguments are preserved
                    # Always make sure we have two arguments for CMP
                    if len(final_args) < 2:
                        print(f"Warning: CMP instruction with insufficient arguments. Adding 0 as second argument.")
                        final_args.append('0')
                    
                    # Make sure the instruction with both arguments is explicitly added to text_section
                    # This ensures the intermediate file contains both arguments for CMP
                    text_section.append(f'{opcode} {" ".join(final_args)}'.strip())
                    opcode = None  # Set opcode to None to skip adding another instruction at the end
                elif opcode == 'jmp':
                    # For jump instructions targeting a label (like "jmp print_loop")
                    # With our addressing mode system, the final_args should already contain
                    # the addressing mode and the target address/label
                    if len(final_args) == 2:
                        # This is the expected format - addressing mode and value
                        target_label = None
                        for label_name, label_pos in labels.items():
                            # If this jump target matches a known label position
                            if str(label_pos) == final_args[1]:
                                target_label = label_name
                                break

                        if target_label:
                            print(f"Debug: JMP to label '{target_label}' at position {final_args[1]}")
                        else:
                            print(f"Debug: JMP to address {final_args[1]}")
                    else:
                        # This shouldn't happen with the new addressing mode system,
                        # but we'll handle it just in case
                        print(f"Warning: jmp with unexpected arg count: {final_args}")
                        # Try to fix it - assuming the first arg is the target
                        if len(final_args) > 0:
                            # Use absolute addressing mode for jumps
                            fixed_args = [f"{int(AddressingMode.ABSOLUTE)}", final_args[0]]
                            final_args.clear()
                            final_args.extend(fixed_args)

                elif opcode == 'ret':
                    final_args.append(1)
                    for _ in range(int(final_args[0])):
                        text_section.append('pop 0 0b111')
                    opcode = 'jmp 0b111'
                    final_args = []
                    step += 4

                pos += step + len(final_args)
                if opcode:
                    text_section.append(f'{opcode} {" ".join(final_args)}'.strip())

    for i, line in enumerate(text_section):
        for label in sorted(labels, key=lambda x: len(x), reverse=True):
            dest = labels[label]
            if label in line:
                line = line.replace(f'"{label}"', str(dest))
                line = line.replace(label, str(dest))
                text_section[i] = line

    out.extend(data_section)
    out.extend(text_section)

    return '\n'.join(out)

def process_int_to_bin(intfile):
    data_section = []
    code_section = []
    current_section = data_section  # Default to data section

    with open(intfile) as f:
        for line in f.read().split('\n'):
            if line.startswith(';;') or not line.strip():
                continue
            inst, *args = shlex.split(line)
            if not inst.strip() or inst.startswith('#') or inst.startswith('//'):
                continue            # Special case for db (define byte) directive
            if inst.lower() == 'db':
                # For db, we directly add the byte value without an opcode
                for arg in args:
                    if arg.startswith('0b'):
                        data_section.append(int(arg[2:], 2))
                    elif arg.startswith('0x'):
                        data_section.append(int(arg[2:], 16))
                    elif not arg.isnumeric():
                        data_section.append(ord(arg))
                    else:
                        data_section.append(int(arg))
                continue

            # All non-db instructions go to code section
            # Format: [operand_count, opcode, arg1, arg2, ...]
            try:
                opcode = Inst[inst.upper()].value

                # Special case for CMP to ensure it always has 2 arguments
                if inst.upper() == 'CMP' and len(args) == 1:
                    print(f"Warning: CMP instruction at line '{line}' has only one argument. Adding 0 as second argument.")
                    args.append('0')            # With our addressing mode system, each operand consists of one byte
                # with the addressing mode in the top 2 bits and value in lower 6 bits
                code_section.append(len(args) // 2)  # Number of operands (each is a mode-value pair)
                # Then append the opcode
                code_section.append(opcode)
            except KeyError:
                print('SIGILL: ', line)
                exit(1)

            # Process pairs of arguments (addressing_mode, value)
            i = 0
            while i < len(args):
                # First element should be the addressing mode
                if not args[i]:
                    print(f"Warning: Empty addressing mode found in line: {line}")
                    code_section.append(0)  # Default addressing mode
                    i += 1
                    continue
                
                # Parse addressing mode
                try:
                    mode = int(args[i])
                except ValueError:
                    print(f"Warning: Invalid addressing mode '{args[i]}' in line: {line}")
                    mode = 0  # Default to register mode
                
                # Next element is the value
                i += 1
                if i >= len(args):
                    print(f"Warning: Missing value after addressing mode in line: {line}")
                    value = 0
                else:
                    arg = args[i]
                    if not arg:  # Check for empty string
                        print(f"Warning: Empty value found in line: {line}")
                        value = 0  # Default to 0 for empty args
                    elif arg.startswith('0b'):
                        value = int(arg[2:], 2) & 0x3F  # Ensure 6-bit value
                    elif arg.startswith('0x'):
                        value = int(arg[2:], 16) & 0x3F  # Ensure 6-bit value
                    elif not arg.isnumeric() and arg.startswith('"') and arg.endswith('"'):
                        # Handle string values - use first character's ASCII value
                        str_value = arg.strip('"')
                        if str_value:
                            value = ord(str_value[0]) & 0x3F  # Ensure 6-bit value
                        else:
                            print(f"Warning: Empty string in line: {line}")
                            value = 0
                    elif not arg.isnumeric():
                        # For any other non-numeric value, try to interpret as a character
                        if len(arg) > 0:
                            value = ord(arg[0]) & 0x3F  # Ensure 6-bit value
                        else:
                            print(f"Warning: Empty value in line: {line}")
                            value = 0
                    else:
                        # Numeric values
                        value = int(arg) & 0x3F  # Ensure 6-bit value
                  # Encode the addressing mode and value into two bytes
                # First byte: mode (2 bits) + high 6 bits of value
                # Second byte: low 8 bits of value
                from addressing import encode_addressing_mode
                high_bits = (value >> 8) & 0x3F
                low_byte = value & 0xFF
                byte1, byte2 = encode_addressing_mode(mode, high_bits, low_byte)
                code_section.append(byte1)
                code_section.append(byte2)
                
                i += 1

    output = []

    # Add header (data section pointer)
    if data_section:
        output.append((len(data_section) + 2) >> 8)
        output.append((len(data_section) + 2) & 0xFF)
    else:
        output.extend((0,0))

    # Add code section
    output.extend(code_section)

    # Add data section
    output.extend(data_section)

    return bytes(output)

def main():
    infile = sys.argv[1]
    outfile = sys.argv[2] if len(sys.argv) > 1 else infile.removesuffix('.asm') + '.bin'
    intfile = infile.removesuffix('.asm') + '.int'
    debug = True

    p = read_file(infile)
    int_content = process_asm_to_int(p, debug_include=debug)
    write_file(intfile, int_content)

    binary_content = process_int_to_bin(intfile)
    with open(outfile, 'wb') as f:
        f.write(binary_content)

if __name__ == "__main__":
    main()
