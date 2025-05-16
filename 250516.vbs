Option Explicit
'PROVO ACQUISIZIONE CON AUTOFOCUS
'per colorato solo luce sotto 3\4 tacche
'X 15000  Y 21000
'per non colorato
'X 15500  Y 24500

Dim videoID
Dim video
Dim StatusX
Dim StatusY
Dim positionName
Dim column : column = 0
Dim row : row = 0
Dim scope
Dim lastX, lastY

Const MOTOR_VALUE = 0
Const MOTOR_ORIGIN = 5
Const MOTOR_NO_MESSAGE = 100
Const ACQ_IMAGE = 1
Const ACQ_AUTO_SHOW = 10
Const START_VIDEO = 0
Const STOP_VIDEO = 1
Const GET_VIDEO_ID = 2
Const MB_OK = 0
Const START_AUTOFOCUS = 0
Const VIDEO_AUTOFOCUS = 12
Const GET_AUTOFOCUS_STATUS = 1
Const GET_AUTOFOCUS_STATE = 4
Const AUTOFOCUS_ENABLE = 5
Const STOP_AUTOFOCUS = 2
Const MOTOR_STEP = 1
Const PARAM_DEFAULT = 0
Const PARAM_OVERWRITE = 1
Const SHOW_ALWAYS = 1

'mi posiziono in alto a sinistra di default
Call moveToStart

'inserisco i parametri X e Y per configurazione
LabSpec.SetSingleScriptParam "Asse X", "um", row, PARAM_OVERWRITE
LabSpec.SetSingleScriptParam "Asse Y", "um", column, PARAM_OVERWRITE

LabSpec.SetScriptParamOptions "Configurazione posizione di partenza", SHOW_ALWAYS

LabSpec.SetSingleScriptParam "Asse X", "um", row, PARAM_DEFAULT
LabSpec.SetSingleScriptParam "Asse Y", "um", column, PARAM_DEFAULT

LabSpec.MoveMotor "X", row, positionName, MOTOR_VALUE
LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
lastX = row
lastY = column

'inizio acquisizione
Call acquisition

Sub moveToStart 'il punto 0,0 e' a altezza centro a sinistra

    Dim motorX : motorX = 0
    Dim motorY : motorY = 0
    
    LabSpec.MoveMotor "X", row, positionName, MOTOR_VALUE
    LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
    Do
        lastX = motorX
        row = row - 900
        
        LabSpec.MoveMotor "X", row, positionName, MOTOR_VALUE
        motorX = LabSpec.GetMotorPosition("X", MOTOR_VALUE)

    Loop Until motorX = lastX
   
    Do
        lastY = motorY
        column = column - 820
        
        LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)

    Loop Until motorY = lastY

    LabSpec.MoveMotor "X", lastX, positionName, MOTOR_ORIGIN
    LabSpec.MoveMotor "Y", lastY, positionName, MOTOR_ORIGIN
    column = lastY
    row = lastX 
End Sub

Sub acquisition
    Dim x : x = 0
    Dim y : y = 0
   'Dim focusState, focusEnabled
    video = LabSpec.Video(START_VIDEO)
    Do
        x = 0
        row = lastX
        Do
            LabSpec.MoveMotor "X", row, positionName, 0
            Do
                LabSpec.GetMotorStatus "X", StatusX
            Loop Until StatusX = 0
            
            Do 
                videoID = LabSpec.Video(GET_VIDEO_ID)
                LabSpec.Pause 1000
        
            Loop Until videoID>0
            
           'focusEnabled = LabSpec.AutoFocus(GET_AUTOFOCUS_STATE)
           'If(focusEnabled = 0) Then
          '     LabSpec.AutoFocus AUTOFOCUS_ENABLE
           ' End If
            
           ' LabSpec.AutoFocus VIDEO_AUTOFOCUS
            
            'LabSpec.AutoFocus START_AUTOFOCUS

          ' Do
           '     focusState = LabSpec.AutoFocus(GET_AUTOFOCUS_STATUS)
          ' Loop until focusState = 0

            LabSpec.AddID videoID
            LabSpec.Save 0, "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\acqBianco\" & row & "_" & column & ".jpg", "jpg"

           'LabSpec.AutoFocus STOP_AUTOFOCUS
            
            row = row + 900 'per scope x5 ci muoviamo di 900 pixel,
            x = x + 1
        Loop Until x > 10
        
        column = column + 820 'per scope x5 ci muoviamo di 820 pixel,
        LabSpec.MoveMotor "Y", column, positionName, 0
        Do
            LabSpec.GetMotorStatus "Y", StatusY
        Loop Until StatusY = 0
        y = y + 1
    Loop Until y > 10
    video = LabSpec.Video(STOP_VIDEO)
    
End Sub
