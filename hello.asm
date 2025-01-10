.data
HELLO_STR:
    .ascii "Hello, World!\0"

.text
# Start of the program
start:
    # Load the address of the string into a register
    lda 0b0000, HELLO_STR

    # Print each character until we reach the null terminator
print_loop:
    # Load the character from memory
    lda 0b0001, 0b0000

    # Check if the character is the null terminator
    beq 0b0001, 0b0000, end

    # Print the character
    out 0b0001

    # Increment the address
    inc 0b0000

    # Jump back to the start of the loop
    jmp print_loop

end:
    # Halt the program
    hlt