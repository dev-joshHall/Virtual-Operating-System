; This is an I/O bound program, it will loop forever doing an SWI instruction
MVI Z 50  ; Start Z at 50
MVI R1 1
LOOP  SUB Z Z R1  ; Subtract 1 from Z
      SWI 1
      BGT LOOP ; Loop if Z > 0