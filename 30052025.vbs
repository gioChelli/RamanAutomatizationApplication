Option Explicit
Dim video
Dim videoID

Const START_VIDEO = 0
Const STOP_VIDEO = 1
Const GET_VIDEO_ID = 2
Const INTERPRETED = 0
Const RAW = 1
Const HTTP_POST = 1
Const HTTP = 2

Call acquisition

Sub acquisition
    
    Dim path: path = "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\0.jpg"
    Dim url : url = "http://127.0.0.1:5500/laserImage"
    Dim http, stream, boundary, body
    Dim row : row = 0
    boundary = "-----BOUNDARY123456"
    video = LabSpec.Video(START_VIDEO)       
    
    Do   
        videoID = LabSpec.Video(GET_VIDEO_ID)
        LabSpec.Pause 1000
        
    Loop Until videoID>0
            
    LabSpec.AddID videoID
    LabSpec.Save 0, "C:\Users\RAMAN\Desktop\GiorgioChelliScripts\acquisition\0.jpg", "jpg"
    'send = LabSpec.Send("HTTP", "http://0.0.0.0:5500/edgeImage", "files=videoID", Mode, Status)
    'LabSpec.Message Status, 0
    
    video = LabSpec.Video(STOP_VIDEO)
    
    Dim fileStream
    Set fileStream = CreateObject("ADODB.Stream")
    fileStream.Type = 1 ' Binary
    fileStream.Open
    fileStream.LoadFromFile path
    Dim imageByte: imageByte = fileStream.Read
    fileStream.Close

    Dim part1, part2
    part1 = "--" & boundary & vbCrLf & "Content-Disposition: form-data; name=""file""; filename=""" & row & """" & vbCrLf & "Content-Type: image/jpeg" & vbCrLf & vbCrLf
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
    End With
    LabSpec.Message strResponse, 0

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
