# hackembler

`hackembler` is an assembler of 16-bit Hack Assembly Language.

Hack Assembly Language is a language described in a textbook titled "The Elements of Computing Systems: Building a Modern Computer from First Principles" by Noam Nisan and Shimon Schocken.

The assembler handles all the specified instructions, variable labels, goto labels, comment and whitespace.

## Example

As an example, take a look at the following Hack Assembly program.
It multiples (using repeated addition) `RAM[0]` and `RAM[1]` and stores the result in `RAM[2]`.

```
// counter = R0
@R0
D=M
@counter
M=D

// R2 = 0
@R2
M=0

(LOOP)
  // if (counter == 0) goto END
  @counter
  D=M
  @END
  D;JEQ

  // counter--
  @counter
  M=M-1

  // R2 += R1
  @R1
  D=M
  @R2
  M=M+D

  // goto LOOP
  @LOOP
  0;JMP

(END)
  // an infinite loop
  @END
  0;JMP
```

The above program is translated to the following 20 16-bit instructions:

```
0000000000000000
1111110000010000
0000000000010000
1110001100001000
0000000000000010
1110101010001000
0000000000010000
1111110000010000
0000000000010010
1110001100000010
0000000000010000
1111110010001000
0000000000000001
1111110000010000
0000000000000010
1111000010001000
0000000000000110
1110101010000111
0000000000010010
1110101010000111
```

