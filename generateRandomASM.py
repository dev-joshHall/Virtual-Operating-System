import random

with open('randomSWI1.asm', 'w') as f1:
	probs = []
	for _ in range(20):
		prob = random.randint(1, 20) / 100
		probs.append(prob)
	for _ in range(15):
		for p in probs:
			r = random.random()
			if r > p:
				f1.write('ADD R3 R3 R3 ; Do operation\n')
			else:
				f1.write('SWI 1\n')

with open('randomSWI2.asm', 'w') as f2:
	probs = []
	for _ in range(10):
		prob = random.randint(1, 20) / 100
		probs.append(prob)
	for _ in range(30):
		for p in probs:
			r = random.random()
			if r > p:
				f2.write('ADD R3 R3 R3 ; Do operation\n')
			else:
				f2.write('SWI 1\n')