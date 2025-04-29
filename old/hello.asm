.data
HELLO_STR:
    .ascii "Hello, World!"  # Assembler will add the null terminator automatically

.text
# Start of the program
start:
    # Load the address of the string into a register
    ldx HELLO_STR

    # Print each character until we reach the null terminator
print_loop:
    # Load the character from memory
    lda x
    cmp a, #0
    beq end

    # Print the character
    out 0b0001

    # Increment the address
    inx

    # Jump back to the start of the loop
    jmp print_loop

end:
    # Halt the program
    hlt