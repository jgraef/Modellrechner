; springe zum start des programms
jum start

; variablen
a: sb 0

; programm
start:
	; lade erste zahl nach a
	in 0
	stad a
	; lade zweite zahl in den akkumulator
	in 0
	; addiere beide zahlen (akku := akku+a)
	addd a
	; gebe summe aus
	out 0
	; beende programm
	stop
