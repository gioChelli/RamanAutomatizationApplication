'PROVA A SPOSTARE IL MOTORE A INIZIO VETRINO
Option Explicit

Dim resX
Dim resY
Dim StatusX
Dim StatusY
Dim row
Dim column
Dim videoID
Dim imageID
Dim video
Dim StopVideo
row = 0
column = 0
Dim positionName

Dim mosaicID

Dim MOTOR_VALUE
Dim MOTOR_NO_MESSAGE
Dim ACQ_IMAGE
Dim ACQ_AUTO_SHOW
Dim START_VIDEO 
Dim STOP_VIDEO
Dim GET_VIDEO_ID
Dim MB_OK
Dim NO_SPECIFIED_COLOR
Dim START_EXTENDED_VIDEO

MOTOR_VALUE = 0
MOTOR_NO_MESSAGE = 100
ACQ_IMAGE = 1
ACQ_AUTO_SHOW = 10 
START_VIDEO = 0
START_EXTENDED_VIDEO = 3
STOP_VIDEO = 1
GET_VIDEO_ID = 2
MB_OK = 0
NO_SPECIFIED_COLOR = -1

moveToStart
acquisition
'createImage

Sub moveToStart 'il punto 0,0 e' a altezza centro a sinistra

   'Dim position
   'position = LabSpec.GetMotorPosition("X", MOTOR_VALUE)
   'LabSpec.Message "Sono in posizione" & position, MB_OK
    LabSpec.MoveMotor "X", column, positionName, 0
    LabSpec.MoveMotor "Y", row, positionName, 0
    Do
       LabSpec.GetMotorStatus "X", StatusX
       LabSpec.GetMotorStatus "Y", StatusY
    Loop Until StatusX=0 And StatusY = 0
    
End Sub

Sub acquisition
   Dim x : x = 0
   Dim y : y = 0
  'mosaicID = LabSpec.CreateDataObject("FloatImage", 1024, 1024, NO_SPECIFIED_COLOR)

   Do
        x = 0
        Do
            LabSpec.MoveMotor "X", column, positionName, 0
            Do
                LabSpec.GetMotorStatus "X", StatusX
            Loop Until StatusX = 0
            
            video = LabSpec.Video(START_VIDEO)
   
            Do 
                videoID = LabSpec.Video(GET_VIDEO_ID)
                LabSpec.Pause 1000
            Loop Until videoID>0 
   
            LabSpec.AddID videoID
            LabSpec.Save 0, "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\firstAcq\" & row & "_" & column & ".jpg", "jpg"
  
            video = LabSpec.Video(STOP_VIDEO)   
            
            column = column + 900
            x = x + 1
        Loop Until x > 19
        
        row = row + 820
        LabSpec.MoveMotor "Y", row, positionName, 0
        Do
            LabSpec.GetMotorStatus "Y", StatusY
        Loop Until StatusY = 0
        y = y + 1
    Loop Until y > 19
    
End Sub

Sub createImage

    
    Dim i
    Dim value
    
   'Do
        mosaicID = LabSpec.Load("C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\0_0.jpg")
        LabSpec.Message mosaicID, MB_OK
   'Loop until mosaicID > 0
   'LabSpec.Paint 0, mosaicID, value, 0.2, 0.2, 0.6, 0.6, "immagine"
    LabSpec.Message mosaicID, MB_OK
   'For i=0 To UBound(mosaicID)
     '  LabSpec.Message mosaicID(i), MB_OK
   'Next
    
End Sub
