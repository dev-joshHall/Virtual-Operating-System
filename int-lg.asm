MVI Z 20  ; Start Z at 20
MVI R1 1
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
ADD R3 R3 R3 ; Do operation
LOOP1  SUB Z Z R1  ; Subtract 1 from Z
      ADD R3 R3 R3 ; Do operation
      SWI 1
      BGT LOOP1 ; Loop if Z > 0
MVI Z 100  ; Start Z at 100
LOOP2 SUB Z Z R1  ; Add 1 to Z
      ADD R3 R3 R3 ; Do operation
      BGT LOOP2 ; Loop if Z > 0