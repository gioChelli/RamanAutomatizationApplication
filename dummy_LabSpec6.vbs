Option Explicit
Dim serverName, PORT
Dim startY, endY
Dim ErrorConnection
ErrorConnection = False
serverName = "127.0.0.1"
PORT = "5500"

main

Sub main
    Do
        RamanConnection
        If ErrorConnection = True Then
            Exit Sub
        End If
        WScript.Sleep 10000
    Loop
    
End Sub

Sub AcquisitionProcess
    StartAcquisition
    WScript.Echo "Inizio invio colonne" & ErrorConnection
    If ErrorConnection = True Then
        Exit Sub
    End If
    startY = CDbl(SendColumn("start"))
    If ErrorConnection = True Then
        Exit Sub
    End If
    endY = CDbl(SendColumn("end"))
    startY = 19689 'le sovrascrivo perche non ho le acquisizioni di colonna, comunque il metodo precedente funziona
    endY = 38549
    WScript.Echo "Fine invio colonne " & ErrorConnection
    If ErrorConnection = True Then
        Exit Sub
    End If
    SendImages
    If ErrorConnection = True Then
        Exit Sub
    End If
    EndAcquisition
    If ErrorConnection = True Then
        Exit Sub
    End If
End Sub

Function SendColumn(order)
    Dim fso, folder, files, file
    Dim arrFiles()
    Dim path : path = "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\colonne\acquisizione1\"        '"D:\Giorgio\unipi\Tirocinio\VBScript\colonne\acquisizione1\"
    Dim url : url = "http://127.0.0.1:5500/edgeImage"
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set folder = fso.GetFolder(path)
    Set files = folder.Files

    Dim count : count = 0
    For Each file In files
        count = count + 1
    Next

    ReDim arrFiles(count - 1)

    Dim i : i = 0
    Dim kv
    For Each file In files
        kv = Split(file.Name, ".")
        arrFiles(i) = kv(0)
        i = i + 1
    Next

    Dim j, temp
    For i = 0 To count - 2
        For j = i + 1 To count - 1
            If order = "start" And CDbl(arrFiles(i)) > CDbl(arrFiles(j)) Then
                temp = arrFiles(i)
                arrFiles(i) = arrFiles(j)
                arrFiles(j) = temp
            ElseIf order = "end" And CDbl(arrFiles(i)) < CDbl(arrFiles(j)) Then
                    temp = arrFiles(i)
                    arrFiles(i) = arrFiles(j)
                    arrFiles(j) = temp
            End If
        Next
    Next

    Dim result, resultCode
    For i = 0 to count-2
        arrFiles(i) = arrFiles(i) & ".jpg"
        sendImage path, url, arrFiles(i), resultCode, result
        
        Dim find, row, col
        If  resultCode <> "201" Then 
            ErrorConnection = True
            Exit For
        ElseIf resultCode = "201" Then
            Serialization result, find, row, col
        End If

        If find = "GLASS" Then
            SendColumn = row
            Exit For
        End If
    Next
End Function

Sub SendImages 
    Dim fso, folder, files, file
    Dim arrFiles()
    Dim path : path = "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\melanomaColorato\"     '"D:\Giorgio\unipi\Tirocinio\melanomaColorato\"
    
    Dim url : url = "http://127.0.0.1:5500/patternImage"
    
    Set fso = CreateObject("Scripting.FileSystemObject")
    Set folder = fso.GetFolder(path)
    Set files = folder.Files
    WScript.Echo "Inizio invio immagini"
    Dim count : count = 0
    For Each file In files
        count = count + 1
    Next
    WScript.Echo "immagini" & count

    ReDim arrFiles(count - 1)
    Dim result, resultCode, i
    For Each file In files

        sendImage path, url, file.Name, resultCode, result
        
        If  resultCode <> "201" Then 
            ErrorConnection = True
            Exit For
        End If
    Next
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
        WScript.Echo o.ResponseText
        result = Replace(result, "{", "")
        result = Replace(result, "}", "")
        result = Replace(result, """", "") 
        WScript.Echo result
        Dim coppie, kv, chiave, valore
        Dim x, y, scope, operation, i

        coppie = Split(result, ",")

        For i = 0 To UBound(coppie)

            kv = Split(coppie(i), ":")
    
            If UBound(kv) >= 1 Then
                chiave = Trim(kv(0))
                valore = Trim(kv(1))
                WScript.Echo "  Chiave: " & chiave
                WScript.Echo "  Valore: " & valore

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
                WScript.Echo "Errore nel parsing della coppia: " & coppie(i)
            End If
        Next

        If operation = "acquisition" Then
            AcquisitionProcess
        ElseIf operation = "ramanAcquisition" Then
            RamanAcquisition x, y 
        Else
            PatternAcquisition x, y, scope 
        End If
    End If
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
    WScript.Sleep 10000
    Dim filepath : filepath = "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\ramanAcquisition.txt"
    Dim newName : newName = "raman_" & x & "_" & y & ".txt"

    Dim stream, bytes
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1 
    stream.Open
    stream.LoadFromFile filepath
    bytes = stream.Read
    stream.Close

    Dim encoded
    encoded = EncodeBase64(bytes)

    Dim jsonBody
    jsonBody = "{""filename"":""" & newName & """,""content"":""" & encoded & """}"

    Dim http
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "PATCH", "http://" & serverName & ":" & PORT & "/endRamanAcquisition", False
    http.setRequestHeader "Content-Type", "application/json"
    http.send jsonBody

    main
End Sub

Sub StartAcquisition
    Dim o
    Set o = CreateObject("WinHttp.WinHttpRequest.5.1")
    o.Open "PATCH", "http://" & serverName & ":" & PORT & "/startAcquisition", False
    o.Send
    If o.Status <> "200" Then 
        ErrorConnection = True
    End If
End Sub

Sub EndAcquisition
    Dim url : url = "http://"& serverName & ":" & PORT &"/endAcquisition"
    Dim o
    Set o = CreateObject("WinHttp.WinHttpRequest.5.1")
    o.Open "PATCH", url,False
    o.Send
    If o.Status <> "200" Then 
        ErrorConnection = True
    End If

    Set o = Nothing
End Sub

Sub sendImage(ByVal path, ByVal url, ByVal filename, ByRef resultCode, ByRef result)
    
    Dim http, stream, boundary, body
    'MsgBox path & filename
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