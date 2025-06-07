Option Explicit

Const STARTROWGLASS = 5060 
Const AXISYx5 = 820 'dimensione standard della colonna con scope x5
Const AXISXx5 = 900 'dimensione standard della riga con scope x5

Dim positionName 'parametro usato per lo spostamento non inizializzato
Dim y : y = 0
Dim x : x = 0
Dim startY, endY
Dim lastX, lastY
Dim ErrorConnection : ErrorConnection = False

Const MOTOR_VALUE = 0
Const MOTOR_ORIGIN = 5
Const START_VIDEO = 0
Const STOP_VIDEO = 1
Const GET_VIDEO_ID = 2
Const MB_OK = 0

Dim longValue : longValue = 50000
Call main

Sub main
    'mi posiziono in alto a sinistra e lo setto come default
    move("-")

    LabSpec.MoveMotor "X", lastX, positionName, MOTOR_ORIGIN
    LabSpec.MoveMotor "Y", lastY, positionName, MOTOR_ORIGIN
    x = 0
    y = 0    
    StartAcquisition
    'inizio acquisizione per trovare inizio vetrino
    If ErrorConnection = True Then
        Exit Sub
    End If
    startY = EdgesAcquisition("+")
    If ErrorConnection = True Then
        Exit Sub
    End If
    'LabSpec.Message startY, 0
    'mi posiziono in fondo a sinistra
    move("+")
    'inizio acquisizione per trovare fine vetrino
    endY = EdgesAcquisition("-")
    If ErrorConnection = True Then
        Exit Sub
    End If
    'inizio acquisizione solo della zona del vetrino
    GlassAcquisition
    If ErrorConnection = True Then
        Exit Sub
    End If
End Sub

Sub StartAcquisition
    Dim o
    Set o = CreateObject("MSXML2.XMLHTTP")
    o.Open "GET", "http://127.0.0.1:5500/startAcquisition", False
    o.Send
    If o.Status <> "200" Then 
        LabSpec.Message "Connessione non riuscita", 0
        ErrorConnection = True
    End If
End Sub

Sub GlassAcquisition
    
    Dim path: path = "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\glassAcq\"
    Dim filename
    Dim url : url = "http://127.0.0.1:5500/patternImage"
    Dim resultCode
    Dim result
   
    Dim motorX : motorX = 0
    Dim motorY : motorY = 0    
    x = STARTROWGLASS
    y = startY
    Dim videoID 
    Dim video

    LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
    LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE
    
    video = LabSpec.Video(START_VIDEO)
    Do
        Do
            lastX = x
            LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
            motorX = LabSpec.GetMotorPosition("X", MOTOR_VALUE)
            
            Do 
                videoID = LabSpec.Video(GET_VIDEO_ID)
                LabSpec.Pause 1000
            Loop Until videoID>0

            LabSpec.AddID videoID
            filename = x & "_" & y & ".jpg"
            LabSpec.Save 0, path & filename, "jpg"

            sendImage path, url, filename, resultCode, result

            Dim find, row, col
            If  resultCode <> "201" Then 
                ErrorConnection = True
                Exit Do
            ElseIf resultCode = "201" Then
                Serialization result, find, row, col
            End If
        
            'LabSpec.Message findVetr, 0

            If find = "PATTERN" Then
                EdgesAcquisition = row
                Exit Do
            End If
            
            x = x + AXISXx5
            
        Loop Until lastX = motorX
        
        If ErrorConnection = True Then
            Exit Do
        End If
        y = y + AXISYx5
        LabSpec.MoveMotor "Y", column, positionName, MOTOR_VALUE
        motorX = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)
        
    Loop Until y >= endY
    video = LabSpec.Video(STOP_VIDEO)

End Sub

Sub move(ByVal operator)
    
    Dim lastX, lastY
    Dim xOffset : xOffset = AXISXx5 
    Dim yOffset : yOffset = AXISYx5 
    Dim motorX 
    Dim motorY 

    LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
    LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE
    Do
        lastX = motorX
      
        x = x - xOffset
        
        LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
        motorX = LabSpec.GetMotorPosition("X", MOTOR_VALUE)
        If motorX = lastX Then
            x = lastX
            xOffset = xOffset / 2
        End if

    Loop Until (motorX = lastX) and (xOffset < 1) 
   
    Do
        lastY = motorY
        Select Case operator
            Case "+"
                y = y + yOffset
            Case "-"
                y = y - yOffset
        End Select
        
        LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)

        If motorY = lastY Then
            y = lastY
            yOffset = yOffset / 2
        End if

    Loop Until (motorY = lastY) and (yOffset < 1)

End Sub
    
Function EdgesAcquisition(ByVal operator)
    
    Dim path: path = "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\colonne\acquisizione5\"
    Dim filename
    Dim url : url = "http://127.0.0.1:5500/edgeImage"
    Dim resultCode
    Dim result
    
    Dim videoID 
    Dim video
    Dim motorY : motorY = 0
    Dim lastY
       
    x = x + 8000
    video = LabSpec.Video(START_VIDEO)
    LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
    Do
        lastY = motorY
        Select Case operator
            Case "+"
                 y = y + AXISYx5
            Case "-"
                 y = y - AXISYx5
        End Select
       
        Do 
            videoID = LabSpec.Video(GET_VIDEO_ID)
            LabSpec.Pause 1000
        Loop Until videoID>0
        
        LabSpec.AddID videoID
        filename = y & ".jpg"
        LabSpec.Save 0, path & filename, "jpg"

        sendImage path, url, filename, resultCode, result
        
        Dim find, row, col
        If  resultCode <> "201" Then 
            ErrorConnection = True
            Exit Do
        ElseIf resultCode = "201" Then
            Serialization result, find, row, col
        End If
        
        'LabSpec.Message findVetr, 0

        If find = "GLASS" Then
            EdgesAcquisition = row
            Exit Do
        End If

        LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)

    Loop Until motorY = lastY
    video = LabSpec.Video(STOP_VIDEO)   
End Function

Sub sendImage(ByVal path, ByVal url, ByVal filename, ByRef resultCode, ByRef result)
    
    Dim http, stream, boundary, body
    
    boundary = "-----BOUNDARY123456"
    Dim fileStream
    Set fileStream = CreateObject("ADODB.Stream")
    fileStream.Type = 1 ' Binary
    fileStream.Open
    fileStream.LoadFromFile path & filename
    Dim imageByte: imageByte = fileStream.Read
    fileStream.Close

    Dim part1, part2
    part1 = "--" & boundary & vbCrLf & "Content-Disposition: form-data; name=""file""; filename=""" & filename & """" & vbCrLf & "Content-Type: image/jpeg" & vbCrLf & vbCrLf
    part2 = vbCrLf & "--" & boundary & "--" & vbCrLf

    Set body = CreateObject("ADODB.Stream")
    body.Type = 1
    body.Open
    body.Write TextToBinary(part1)
    body.Write imageByte
    body.Write TextToBinary(part2)
    body.Position = 0

    With CreateObject("MSXML2.ServerXMLHTTP")
        .SetTimeouts 0, 60000, 300000, 300000
        .Open "POST", url, False
        .SetRequestHeader "Content-Type", "multipart/form-data; boundary=" & boundary
        .Send body.Read
        If .Status = "201" Then 
            result = .ResponseText
        Else 
            result = .StatusText 
        End If
        resultCode = .Status
    End With
    
    'LabSpec.Message strResponse, 0
    'If InStr(strResponse, """result"":""EMPTY""") > 0 Then
        'LabSpec.Message "top", 0
    'End If
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

Sub Serialization(ByVal result, ByRef find, ByRef row, ByRef col)
    result = Replace(result, "{", "")
    result = Replace(result, "}", "")
    'Divide in coppie chiave:valore
    Dim coppie, i, kv, chiave, valore, vetrino
    coppie = Split(result, ",")
    
    For i = 0 To UBound(coppie)
        kv = Split(coppie(i), ":")
        chiave = Trim(Replace(Replace(kv(0), """", ""), Chr(34), ""))
        valore = Trim(Replace(kv(1), """", ""))
       'LabSpec.Message row, 0
        Select Case chiave
            Case "result"
                 find = valore
            Case "row"
                row = valore
            Case "column"
                 col = CInt(valore)
        End Select
    Next
End Sub
