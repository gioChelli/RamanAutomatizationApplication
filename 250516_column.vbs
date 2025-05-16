Option Explicit 
'permette di scansionare una colonna da analizzare per decidere da Dove fare foto

Dim videoID
Dim video
Dim StatusX
Dim StatusY
Dim positionName
Dim column : column = 0
Dim row : row = 0
Dim scope

Const MOTOR_VALUE = 0
Const MOTOR_ORIGIN = 5
Const START_VIDEO = 0
Const STOP_VIDEO = 1
Const GET_VIDEO_ID = 2

'mi posiziono in alto a sinistra di default
Call moveToStart

'inizio acquisizione
Call acquisition

Sub moveToStart 'il punto 0,0 e' a altezza centro a sinistra

    Dim motorX : motorX = 0
    Dim motorY : motorY = 0
    Dim lastY

    LabSpec.MoveMotor "X", row, positionName, MOTOR_VALUE
    LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
    motorX = LabSpec.GetMotorPosition("X", MOTOR_VALUE)
    Do
        If(motorX < 5000) Then
            row = row + 900
        Else
            row = row - 900
        End If
        LabSpec.MoveMotor "X", row, positionName, MOTOR_VALUE
        motorX = LabSpec.GetMotorPosition("X", MOTOR_VALUE)

    Loop Until motorX > 5000
   
    Do
        lastY = motorY
        column = column - 820
        
        LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)

    Loop Until motorY = lastY

    LabSpec.MoveMotor "X", motorX, positionName, MOTOR_ORIGIN
    LabSpec.MoveMotor "Y", lastY, positionName, MOTOR_ORIGIN
    column = lastY
    row = motorX 
End Sub
    
Sub acquisition
    Dim lastY, motorY
    motorY = 0
    video = LabSpec.Video(START_VIDEO)
    Do
        lastY = motorY
        column = column + 820
        Do 
            videoID = LabSpec.Video(GET_VIDEO_ID)
            LabSpec.Pause 1000
        Loop Until videoID>0
        
        LabSpec.AddID videoID
        LabSpec.Save 0, "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\debugCol\" & column & ".jpg", "jpg"
        LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)

    Loop Until motorY = lastY
    video = LabSpec.Video(STOP_VIDEO)   
End Sub
