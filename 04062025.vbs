Option Explicit

Dim positionName

Const MOTOR_VALUE = 0
Const MOTOR_ORIGIN = 5
Const START_VIDEO = 0
Const STOP_VIDEO = 1
Const GET_VIDEO_ID = 2
Const MB_OK = 0

'mi posiziono in alto a sinistra di default
Call moveToStart

'inizio acquisizione
Call acquisition

Sub moveToStart 'il punto 0,0 e' a altezza centro a sinistra
    
    Dim column : column = 0
    Dim row : row = 0
    Dim lastX, lastY
    
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
    
End Sub
    
Sub acquisition
    
    Dim videoID 
    Dim video
    Dim column : column = 0
    Dim row : row = 0
    Dim motorY : motorY = 0
    Dim lastY
    row = row + 8000
    video = LabSpec.Video(START_VIDEO)
    LabSpec.MoveMotor "X", row, positionName, MOTOR_VALUE
    Do
        lastY = motorY
        column = column + 832
        Do 
            videoID = LabSpec.Video(GET_VIDEO_ID)
            LabSpec.Pause 1000
        Loop Until videoID>0
        
        LabSpec.AddID videoID
        LabSpec.Save 0, "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\colonne\acquisizione5\" & column & ".jpg", "jpg"
        
        Dim resultCode
        sendImage column, resultCode 
        
        If  resultCode <> "201" Then Exit Do
        LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)

    Loop Until motorY = lastY
    video = LabSpec.Video(STOP_VIDEO)   
End Sub

Sub sendImage(ByVal column, ByRef resultCode)
    Dim path: path = "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\colonne\acquisizione5\" & column & ".jpg"
    Dim url : url = "http://127.0.0.1:5500/laserImage"
    Dim http, stream, boundary, body
    
    boundary = "-----BOUNDARY123456"
    Dim fileStream
    Set fileStream = CreateObject("ADODB.Stream")
    fileStream.Type = 1 ' Binary
    fileStream.Open
    fileStream.LoadFromFile path
    Dim imageByte: imageByte = fileStream.Read
    fileStream.Close

    Dim part1, part2
    part1 = "--" & boundary & vbCrLf & "Content-Disposition: form-data; name=""file""; filename=""" & column & """" & vbCrLf & "Content-Type: image/jpeg" & vbCrLf & vbCrLf
    part2 = vbCrLf & "--" & boundary & "--" & vbCrLf

    Set body = CreateObject("ADODB.Stream")
    body.Type = 1
    body.Open
    body.Write TextToBinary(part1)
    body.Write imageByte
    body.Write TextToBinary(part2)
    body.Position = 0

    Dim strResponse
    With CreateObject("MSXML2.ServerXMLHTTP")
        .SetTimeouts 0, 60000, 300000, 300000
        .Open "POST", url, False
        .SetRequestHeader "Content-Type", "multipart/form-data; boundary=" & boundary
        .Send body.Read
        If .Status = "201" Then 
            strResponse = .ResponseText
        Else 
            strResponse = .StatusText 
        End If
        resultCode = .Status
    End With
    LabSpec.Message strResponse, 0
    If InStr(strResponse, """result"":""EMPTY""") > 0 Then
        LabSpec.Message "top", 0
    End If
    body.Close

End Sub

Function TextToBinary(txt)
    Dim stream
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 2
    stream.Charset = "ascii"
    stream.Open 
    stream.WriteText txt
    stream.Position = 0
    stream.Type = 1
    TextToBinary = stream.Read
    stream.Close
End Function
