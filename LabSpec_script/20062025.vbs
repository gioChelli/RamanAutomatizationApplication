Option Explicit

Const STARTCOLUMNGLASS = 1650
Const ENDCOLUMNGLASS = 52000
Const STARTROWGLASS = 5060 
Const AXISYx5 = 810 'dimensione standard della colonna con scope x5
Const AXISXx5 = 960 'dimensione standard della riga con scope x5
Const AXISYx10 = 405 'dimensione standard della colonna con scope x10
Const AXISXx10 = 480 'dimensione standard della riga con scope x10
Const AXISYx50 = 81
Const AXISXx50 = 96

Dim positionName 'parametro usato per lo spostamento non inizializzato
Dim y : y = 0
Dim x : x = 0
Dim startY, endY
Dim lastX, lastY
Dim ErrorConnection : ErrorConnection = False
Dim configFile : configFile="C:Users\RAMAN\Desktop\GiorgioChelliScripts\configFile.txt"
Dim path, pathCol, ramanPath, serverName, PORT
Dim SpectrumID
Dim ret
Dim param

Const MOTOR_VALUE = 0
Const MOTOR_ORIGIN = 5
Const START_VIDEO = 0
Const STOP_VIDEO = 1
Const GET_VIDEO_ID = 2
Const MB_OK = 0
Const ACQ_SPECTRUM = 0
Const ACQ_AUTO_SHOW = 10
Const START_AUTOFOCUS = 0
Const GET_AUTOFOCUS_STATE = 1
Const STOP_AUTOFOCUS = 2
Const SHOW_DATA = 0

Call main

Sub main
    
    Dim fso, OggFile, OggTextStream
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    If not fso.FileExists (configFile)Then
        LabSpec.Message "File di configurazione non trovato", MB_OK
        Exit Sub
    End If
    Set OggFile = fso.GetFile (configFile)

    Set OggTextStream = OggFile.OpenAsTextStream(1)
    Dim i : i = 0
    Dim stringa, config
    Do While Not OggTextStream.AtEndOfStream
        stringa = Trim(OggTextStream.ReadLine)
        Dim find
   
        If stringa <> "" And Left(stringa, 1) <> "#" Then
            config = Split(stringa, "=")
            If UBound(config) >= 1 Then 
                Select Case Trim(config(0))
                    Case "columnPath"
                        pathCol = Trim(config(1))
                        find = "col"
                    Case "glassPath"
                        path = Trim(config(1))
                        find = "glass"
                    Case "ramanPath"
                        ramanPath = Trim(config(1))
                        find = "raman"
                    Case "serverName"
                        serverName = Trim(config(1))
                        find = "server"
                    Case "PORT"
                        PORT = Trim(config(1))
                End Select
            Elseif UBound(config) = 0 Then 
                Select Case find
                    Case "col"
                        pathCol = pathCol & Trim(config(0))
                    Case "glass"
                        path = path & Trim(config(0))
                    Case "raman"
                        ramanPath = ramanPath & Trim(config(0))
                    Case "server"
                        serverName = serverName & Trim(config(0))
                End Select
            End If
        End If
    Loop
    OggTextStream.Close
    'LabSpec.Message ramanPath, 0
    Do
        RamanConnection
        If ErrorConnection = True Then
            Exit Sub 'Do
        End If
        LabSpec.Pause 10000
        'Exit Sub
    Loop 
End Sub

Sub AcquisitionProcess
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
    startY = CDbl(EdgesAcquisition("+"))
    If ErrorConnection = True Then
        Exit Sub
    End If
    'LabSpec.Message startY, 0
    'mi posiziono in fondo a sinistra
    move("+")
    'inizio acquisizione per trovare fine vetrino
    endY = CDbl(EdgesAcquisition("-"))
    If ErrorConnection = True Then
        Exit Sub
    End If
    'inizio acquisizione solo della zona del vetrino
    GlassAcquisition
    If ErrorConnection = True Then
        Exit Sub
    End If
    'terminata acquisizione vetrino
    EndAcquisition "endAcquisition"

    RamanConnection
End Sub

Sub RamanConnection
    On Error Resume Next
    Dim o, result
    Set o = CreateObject("WinHttp.WinHttpRequest.5.1")
    o.Open "PATCH", "http://" & serverName & ":" & PORT & "/ramanConnection", False
    o.SetTimeouts 10000, 10000, 10000, 300000                     'rimane in attesa per 5 minuti
    o.Send

    If Err.Number <> 0 Then 'se non ho ricevuto richieste in questi 5 minuti esco e col loop nel main partira poi una nuova connessione
        Err.Clear
        Exit Sub
    End If

    If o.Status <> 200 Then 
        ErrorConnection = True
    Else
        result = o.ResponseText
        
        result = Replace(result, "{", "")
        result = Replace(result, "}", "")
        result = Replace(result, """", "") 
        
        Dim coppie, kv, chiave, valore
        Dim x, y, scope, operation, i

        coppie = Split(result, ",")

        For i = 0 To UBound(coppie)

            kv = Split(coppie(i), ":")
    
            If UBound(kv) >= 1 Then
                chiave = Trim(kv(0))
                valore = Trim(kv(1))

                Select Case chiave
                    Case "status"
                        operation = valore
                    Case "x"
                        x = CDbl(valore)
                    Case "y"
                        y = CDbl(valore)
                    Case "scope"
                        scope = CDbl(valore)
                End Select
            Else
                ErrorConnection = True
            End If
        Next
        
        If operation = "acquisition" Then
            AcquisitionProcess
        ElseIf operation = "ramanAcquisition" Then
            RamanAcquisition x, y 
        ElseIf operation = "patternAcquisition" Then
            PatternAcquisition x, y, scope 
        End If
    End If
End Sub

Sub PatternAcquisition(ByVal x, ByVal Y, ByVal scope)

    Dim url : url = "http://"& serverName & ":" & PORT &"/highResolutionImage"
    Dim stepX, stepY, limitX, limitY, startX, startY, motorX, motorY
    Dim video, videoID, filename
    If scope = 10 Then
        stepX = AXISXx10
        stepY = AXISYx10
        limitX = x + AXISXx5
        limitY = y + AXISYx5
        startX = x
        startY = y
    ElseIf scope = 50 Then
        stepX = AXISXx50
        stepY = AXISYx50
        limitX = x + AXISXx10
        limitY = y + AXISYx10
        startX = x
        startY = y
    End If

    LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
    LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE

    video = LabSpec.Video(START_VIDEO)
    Do
        startX = x
        Do
            LabSpec.MoveMotor "X", startX, positionName, MOTOR_VALUE
            motorX = LabSpec.GetMotorPosition("X", MOTOR_VALUE)
            
            Do 
                videoID = LabSpec.Video(GET_VIDEO_ID)
                LabSpec.Pause 1000
            Loop Until videoID>0

            LabSpec.AddID videoID
            filename = startX & "_" & startY & "_x" & scope & ".jpg"
            LabSpec.Save 0, path & filename, "jpg"
            
            startX = startX + stepX
            Dim result, resultCode

            sendImage path, url, filename, resultCode, result

            If  resultCode <> "201" Then 
                ErrorConnection = True
                Exit Do
            End If
        Loop Until startX >= limitX

        If ErrorConnection = True Then
            Exit Do
        End If
        startY = startY + stepY
        LabSpec.MoveMotor "Y", startY, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)
    Loop Until startY >= limitY
    EndAcquisition "endPatternAcquisition"

    RamanConnection
End Sub

Function EncodeBase64(bytes)
    Dim xml, node
    Set xml = CreateObject("MSXML2.DOMDocument")
    Set node = xml.CreateElement("b64")
    node.DataType = "bin.base64"
    node.nodeTypedValue = bytes
    EncodeBase64 = Replace(node.Text, vbLf, "")
End Function

Sub RamanAcquisition(ByVal x, ByVal y)
    Dim SpectrumID
    Dim url : url = "http://"& serverName & ":" & PORT &"/endRamanAcquisition"
    
    LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
    LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE
    
    LabSpec.Acq ACQ_SPECTRUM + ACQ_AUTO_SHOW, 1, 1, 0, 0 
    
    Do 
        SpectrumID = LabSpec.GetAcqID() 
    Loop Until SpectrumID > 0

    Dim ramanTxt : ramanTxt = ramanPath & x & "_" & y & ".txt"

    LabSpec.AddID(SpectrumID)
    LabSpec.Save 0, ramanTxt, "txt"  
    
    Dim stream, bytes
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1 
    stream.Open
    stream.LoadFromFile ramanTxt
    bytes = stream.Read
    stream.Close

    Dim encoded
    encoded = EncodeBase64(bytes)

    ramanTxt = Replace(ramanPath & x & "_" & y & ".txt", "\", "\\")
    Dim jsonBody
    jsonBody = "{""filename"":""" & ramanTxt & """,""content"":""" & encoded & """}"

    Dim http
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "PATCH", "http://" & serverName & ":" & PORT & "/endRamanAcquisition", False
    http.setRequestHeader "Content-Type", "application/json"
    http.send jsonBody
    
    RamanConnection
End Sub

Sub StartAcquisition
    Dim o
    Set o = CreateObject("WinHttp.WinHttpRequest.5.1")
    o.Open "PATCH", "http://" & serverName & ":" & PORT & "/startAcquisition", False
    o.Send
    If o.Status <> "200" Then 
        LabSpec.Message "Connessione non riuscita", 0
        ErrorConnection = True
    End If
End Sub

Sub EndAcquisition(ByVal method)
    Dim url : url = "http://"& serverName & ":" & PORT &"/" & method
    Dim o
    Set o = CreateObject("WinHttp.WinHttpRequest.5.1")
    o.Open "PATCH", url,False
    o.Send
    If o.Status <> "200" Then 
        LabSpec.Message "Connessione non riuscita", 0
        ErrorConnection = True
    End If

    Set o = Nothing
End Sub

Sub GlassAcquisition
    
    Dim filename
    Dim url : url = "http://"& serverName & ":" & PORT &"/patternImage"
    Dim resultCode
    Dim result
   
    Dim motorX : motorX = 0
    Dim motorY : motorY = 0    
    
    y = startY
    Dim videoID 
    Dim video

    LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
    LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE

    'LabSpec.Message endY, 0
    
    video = LabSpec.Video(START_VIDEO)
    Do
        x = STARTROWGLASS
        Do
            LabSpec.MoveMotor "X", x, positionName, MOTOR_VALUE
            motorX = LabSpec.GetMotorPosition("X", MOTOR_VALUE)
            
            Do 
                videoID = LabSpec.Video(GET_VIDEO_ID)
                LabSpec.Pause 1000
            Loop Until videoID>0

            LabSpec.AddID videoID
            filename = x & "_" & y & ".jpg"
            LabSpec.Save 0, path & filename, "jpg"
            
            x = x + AXISXx5

            sendImage path, url, filename, resultCode, result

            If  resultCode <> "201" Then 
                ErrorConnection = True
                Exit Do
            End If
            
            'Dim find, row, column
            'Serialization result, find, row, col
            'If find = "ERROR" Then
            '    ErrorConnection = True
            '    Exit Do
            'End If

        Loop Until motorX > ENDCOLUMNGLASS

        If ErrorConnection = True Then
            Exit Do
        End If
        y = y + AXISYx5
        LabSpec.MoveMotor "Y", y, positionName, MOTOR_VALUE
        motorY = LabSpec.GetMotorPosition("Y", MOTOR_VALUE)
        
    Loop Until motorY >= endY
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
 
    Dim filename
    Dim url : url = "http://"& serverName & ":" & PORT &"/edgeImage"
    Dim resultCode
    Dim result
    
    Dim videoID 
    Dim video
    Dim motorY : motorY = 0
    Dim lastY
       
    If operator = "+" Then
        y = STARTCOLUMNGLASS 
    End If
    x = 20000
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
        LabSpec.Save 0, pathCol & filename, "jpg"

        sendImage pathCol, url, filename, resultCode, result
        
        Dim find, row, col
        If  resultCode <> "201" Then 
            ErrorConnection = True
            Exit Do
        ElseIf resultCode = "201" Then
            Serialization result, find, row, col
        End If
        
        'LabSpec.Message find, 0

        If find = "GLASS" Then
            EdgesAcquisition = row
            Exit Do
        Elseif find = "ERROR" Then
            ErrorConnection = True
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
            Case "col"
                col = valore
        End Select
    Next
End Sub
