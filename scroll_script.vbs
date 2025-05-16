'script per acquisire tutto lo il vetrino
'mi baso sulle informazioni trovate online che in LabSpec di Horiba un pixel corrisponde a 2.56 * 2.56 micron
Option Explicit

Dim LabSpec
Set LabSpec = CreateObject("LabSpec") 

Dim row, column
row = 0
column = 0

Dim positionName
Dim MOTOR_VALUE, ACQ_IMAGE, ACQ_AUTO_SHOW, MOTOR_NO_MESSAGE

MOTOR_VALUE = 0
ACQ_IMAGE = 1
ACQ_AUTO_SHOW = 10
MOTOR_NO_MESSAGE = 100

Dim resX, resY 'per verificare se lo spostamento è possibile
Dim StatusX, StatusY 'servano per attendere la fine dello spostamento

Call main

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

Function MoveY(ByVal row)
	MoveY = LabSpec.MoveMotor "Y", row, positionName, MOTOR_VALUE + MOTOR_NO_MESSAGE 
End Function

Function MoveX(ByVal column)
	MoveX = LabSpec.MoveMotor "X", column, positionName, MOTOR_VALUE + MOTOR_NO_MESSAGE
End Function

Sub AcquireImages
	
	LabSpec.SetDetectorZone 0, 256, 2, 0, 256, 2
	Do	
		Do
			Dim imageID
		
			resX = MoveX(column)
			If(resX = -1)
				LabSpec.Message "Acquisizione riga terminata o errore nello spostamento", 50
				Exit Do
			EndIf
			Do
				LabSpec.GetMotorStatus("X", StatusX)
			Loop Until StatusX = 0
			column = column + 256 / 2 * 2.56
		
			LabSpec.Acq ACQ_IMAGE + ACQ_AUTO_SHOW, 1, 1, 0, 0
			do 
				imageID = LabSpec.GetAcqID() 
			Loop Until imageID > 0
			'salvataggio
			Dim save
			save = LabSpec.AddID imageID 'questo salva su Labspec
			if(save = -1)
				LabSpec.Message "Immagine non salvata (acquisizioni > 1000)", 50
			EndIf

			LabSpec.Save imageID, "C:\immagini\image" & row & "_" & column & ".tfs", "tfs" 'questo salva su disco
			
		loop
	
		column = 0
		row = row + 256 / 2 * 2.56
		resY = MoveY(row)
		If(resY = -1)
			LabSpec.Message "Acquisizione terminata o errore nello spostamento", 50
			Exit Do
		EndIf
		Do
			LabSpec.GetMotorStatus("Y", StatusY)
		Loop Until StatusY = 0
		
	Loop
End Sub

   

Sub main
	Call moveToStart
	if(resX = -1 or resY = -1)
		LabSpec.Message "Errore acquisizione", 50
		Exit Sub
	Endif
	LabSpec.Message "Inizio acquisizione", 10
	Call AcquireImages
	LabSpec.Message "Acquisizione terminata", 10
End Sub

