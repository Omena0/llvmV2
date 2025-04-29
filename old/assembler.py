from old.inst import Inst
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
        line = lines[i].split(';;')[0].strip()
        if not line:
            continue

        step = 0
        indent = get_indent(line)
        line = line.strip()

        if line.startswith('.'):
            print(f'section {line}')
            section = line
            continue

        if section == '.data':
            if line.endswith(':'):
                label = line[:-1]
                labels[label] = pos
                print(f"{label}: {pos}")
            elif line.startswith('.ascii'):
                string_literal = line.split('.ascii')[1].strip().strip('"')
                for char in string_literal:
                    data_section.append(f'db {ord(char)}')
                    pos += 1
                data_section.append('db 0')  # Null terminator
                pos += 1

        elif section == '.text':
            if line.endswith(':'):
                label = line[:-1]
                labels[label] = pos
                print(f"{label}: {pos}")
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
                opcode, *args = shlex.split(line.replace(',', ' '))
                step += 1
                final_args = []

                for arg in args:
                    arg = arg.strip()
                    if arg.startswith('0b'):
                        final_args.append(str(int(arg[2:], 2)))
                    elif arg.startswith('0x'):
                        final_args.append(str(int(arg[2:], 16)))
                    elif arg.startswith('!'):
                        text_section.append(f'lda 0b1111 {arg[1:]}')
                        final_args.append('0b1111')
                        step += 3
                    elif arg in labels:
                        final_args.append(str(labels[arg]))
                    elif not arg.isnumeric():
                        final_args.append(f'"{arg}"')
                    else:
                        final_args.append(arg)

                if opcode == 'syscall':
                    opcode = 'lda 0b0'
                    step += 1
                elif opcode in ['beq', 'bne', 'bnz', 'jmp']:
                    if 'ret' in p:
                        text_section.append(f'lda 0b111 {pos + 9}')
                        text_section.append('psh 0 0b111')
                        text_section.append(f'lda 0b110 {final_args[0]}')
                        final_args[0] = '0b110'
                        text_section.append(f'{opcode} {" ".join(final_args)}'.strip())
                        text_section.append('pop 0 0b111')
                        opcode = None
                        step += 12
                    else:
                        text_section.append(f'lda 0b110 {final_args[0]}')
                        final_args[0] = '0b110'
                        step += 3
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
    output = []
    with open(intfile) as f:
        for line in f.read().split('\n'):
            if line.startswith(';;') or not line.strip():
                continue
            inst, *args = shlex.split(line)
            if not inst.strip() or inst.startswith('#') or inst.startswith('//'):
                continue

            try:
                output.append(Inst[inst.upper()].value)
            except KeyError:
                print('SIGILL: ', line)
                exit(1)

            for arg in args:
                if arg.startswith('0b'):
                    output.append(int(arg[2:], 2))
                elif arg.startswith('0x'):
                    output.append(int(arg[2:], 16))
                elif not arg.isnumeric():
                    output.append(ord(arg))
                else:
                    output.append(int(arg))

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


