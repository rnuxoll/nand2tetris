// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


// label symbol corresponding to where the start of the loop is
// this loop listens for keyboard input
(LOOP)
    // if a key is pressed, jump to blacken
    @KBD
    // a code of 0 at RAM[KBD] indicates that no key has been pressed
    // a 16 bit character code at RAM[KBD] indicates that a key has been pressed
    D=M // set the value of RAM[KBD] to D

    @BLACKEN // set the A register to BLACKEN, so any jump will be to BLACKEN
    D; JNE // jump if M=RAM[KBD] > 0

    @CLEAR // set the A register to CLEAR so any jump will be to CLEAR
    D; JEQ // jump if M=RAM[KBD] = 0

    // unconditional jump back to beginning of LOOP
    // note that this statement should never be reached unless RAM[KBD] < 0
    // which is an extenuating case of invalid input
    @LOOP
    0;JMP

// label symbol corresponding to commands that blacken the screen
(BLACKEN)
    
    @increment // defined variable that stores how 
    // many registers we are past the address
    // of the initial pixel
    D=M // store value of RAM[increment] in 
    // as shown in from location 1978 of the textbook, setting it to -1 is a shortcut
    // to blacken
    @SCREEN
    A=D+A // add increment to address of the first screen pixel
    M=-1

    // keep incrementing A register and blackening
    // until we reach the end of the data registers that control the screen
    // which is 8192 registers after @SCREEN
    @increment
    MD=M+1 // increment the increment and store in D as well as M

    // check if the increment is greater than 192
    @8192
    D=D-A
    
    @LOOP
    D;JNE // jump back to the beginning of the loop if D != 0
    // i.e. jump back to the beginning of the loop if increment < 8192
    
    // now that screen has been blackened, reset increment and unconditional jump back
    // to listening for keyboard input
    @increment
    M=0
    @LOOP
    0;JMP


// label symbol corresponding to commands that clear the screen
(CLEAR)
    @SCREEN
    M=0

    // now that screen has been blackened, unconditional jump back
    // to listening for keyboard input
    @LOOP
    0;JMP
