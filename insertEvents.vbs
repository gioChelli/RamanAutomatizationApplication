Sub selectEventsPalaiaDB
	
	Set dbConnection = CreateObject("ADODB.Connection")
	Set recordSet = CreateObject("ADODB.Recordset")
	dbConnection.Open "Driver={MySQL ODBC 8.0 ANSI Driver};Server=localhost;Database=comunePalaia;User=root;Password=Giocondo2021$;Option=3;" 
	recordSet.open "SELECT * FROM Events", dbConnection, 1, 3
	
	Do while Not .EOF
		WScript.echo recordSet("Titolo") 'per ogni costumer si scrive il nome
		.MoveNext 'ci muoviamo al prossimo record
	Loop
	
End Sub

'Call selectEventsPalaiaDB

Dim http
Set http = CreateObject("MSXML2.ServerXMLHTTP") 
'esempio di get
http.Open "GET", "https://comunepalaia-production.up.railway.app/news", False 'false specifica che
'la richiesta deve essere sincrona, con true era asincrona
http.Send
If http.Status = 200 Then
    WScript.Echo http.responseText
Else
    WScript.Echo "Errore HTTP: " & http.Status
End If
