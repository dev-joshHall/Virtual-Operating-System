MVI Z 100  ; Start Z at 100
MVI R1 1
LOOP  SUB Z Z R1  ; Subtract 1 from Z
      ADD R3 R3 R3 ; Do operation
      BGT LOOP ; Loop if Z > 0