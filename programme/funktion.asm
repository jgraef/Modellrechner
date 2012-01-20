; springe zum start
jum start

max:
	; Dies ist eine Funktion
	; Funktionen bekommen ihre Parameter in umgekehrter Reihenfolge auf den
	; Stapel gelegt.

	; Wenn eine Funktion einen Rückgabewert hat (ansonsten wäre sie eine
	; Prozedur, was aber keinen großen Unterschied macht) wird dieser im
	; Akkumulator abgelegt.

	; Um später einfachen Zugriff auf die Parameter zu haben erzeugen wir
	; die Stapelbasis für die Funktion.
	newb

	; Um an die Parameter zu gelangen, benutzen wir am besten LDL
	; Stapelzeiger -->
	; Stapelbasis  --> alte Stapelbasis  (LDL 0)
	;                  Rücksprungadresse (LDL 1)
	;                  2. Parameter      (LDL 2)
	;                  1. Parameter      (LDL 3)


	ldl 2 ; 2. Parameter (b) in Akkumulator laden
	sbl 3 ; Akkumulator - 1. Parameter (a), Ergenis wieder in Akkumulator
	      ; speichern
	      ; Die Subtraktion entspricht einen Vergleich (außer dass das
	      ; Ergebnis im Akkumulator liegt)
	cmpu 0 ; Verschiebe Ergebnis vom Akkumulator in das Ergebnisregister
	; springe zu '.b_größer_a' wenn b>a, ansonsten fahre fort
	jp .b_größer_a

	; wird aufgerufen wenn a>b
	ldl 3
	jum .fertig

	.b_größer_a: ; wird aufgerufen wenn b>a
		ldl 2

	.fertig:
		oldb ; alte Stapelbasis wiederherstellen
		ret ; Funktionsaufruf beenden. Ergebnis liegt im Akkumulator

start:
	; 1. Parameter
	in 0; Eingabe einlesen
	push ; Eingabe als Parameter für die Funktion max auf den Stapel legen

	; 2. Parameter
	in 0; Eingabe einlesen
	push ; Eingabe als Parameter für die Funktion max auf den Stapel legen

	; Funktion aufrufen. Ergebnis wird im Akkumulator abgelegt.
	cal max

	; beide Parameter wieder von Stapel holen
	red 2 ; genauso gut kann man zweimal 'pop' benutzen

	; Ausgabe anzeigen
	out 0

	; Programm beenden (stop entspricht einer endlosschleife)
	stop
