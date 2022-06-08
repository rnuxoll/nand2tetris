// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

@sum
M=0 //sum=0

@i
M=1 //i=1

(LOOP)
@i
D=M // D register = i
@R0 // symbol for register 0

D=D-M // D=i-R0
@END
D;JGT // if D=(i-R0) > 0 goto END

@R1
D=M //D=R1
@sum
M=D+M // sum = sum + R1

@i
M=M+1 // i+=1
@LOOP
0;JMP // go to loop

(END)
@sum
D=M // sets D register to value of the register where we stored the sum
    // i.e., sets D register to the sum
@R2
M=D
