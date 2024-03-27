N1 .WORD 1
N2 .WORD 2
N3 .WORD 3
MVI R2 1
MVI R3 2
ADD Z R2 R3		; store sum in Z register
SWI 1			; print result