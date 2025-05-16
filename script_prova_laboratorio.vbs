'PROVA A SPOSTARE IL MOTORE A INIZIO VETRINO
Option Explicit

Dim resX
Dim resY
Dim StatusX
Dim StatusY

Sub moveToStart
	Dim i : i = 0
	do
		resY = MoveY(0)
		resX = MoveX(0)
		If(resX = -1 Or resY = -1)
			LabSpec.Message "Errore nello spostamento", 50
		EndIf
	
		Do
			LabSpec.GetMotorStatus("X", StatusX)
			LabSpec.GetMotorStatus("Y", StatusY)
		Loop Until StatusX=0 And StatusY = 0
	i = i + 1
	if(i = 5)
		Exit Do
	EndIf
	
	loop while resX = -1 or resY = -1 
End Sub