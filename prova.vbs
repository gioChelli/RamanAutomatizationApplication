Option Explicit

dim age : age = 43 'le variabili devono iniziare con una lettera, sono case insensitive, devono 
'aver meno di 256 caratteri
dim gino, data, ora
gino = "gatto"
data = #01/01/2020#	'assegno una data
ora = #12:30:44 PM# 'assegno un ora

wscript.echo "chicken"
'le variabili dichiarate con dim a livello di procedura sono visibili solo 
'all'interno della procedura, quelle dichiarate con dim a livello di script
'sono disponibili per tutte le procedure all'interno dello stesso script.
'le variabili dichiarate con Public sono visibili per tutte le procedure e
'gli script associati.
'Le variabili dichiarate come "Private" hanno validità solo all'interno dello
'script in cui sono dichiarate
Public gino : Private arturo

const HTTP = 80 'costante può avere private o public associato

'comment
REM comment

'integer division \, normal division /
wscript.echo 49\6
' 7 mod 4 per ottenere il resto, 2 ^ 3 per le potenze e le radici 2 ^ (1/2)
' il + lo usiamo anche per la concatenazione, ma per i numeri fa cast implicito e li somma,
' quindi per concatenare possiamo usare &. Per andare a capo possiamo usare la costante
' vblf, mentre vbtab permette di introdurre un tab

dim a, b
a = 23
b = 12

msgbox a = b 'per diverso <>

'per creare una procedura Sub, possiamo passare argomenti e chiamare usando lo statemente
'Call oppure no, non hanno un valore di ritorno
Sub Person_birthday()

End Sub

'modi di chiamare una Sub procedure
Call Person_birthday
Person_birthday 'e qui la lista dei parametri se ci sono

'creazione di una classe
Class Person
	Private m_name
	Private m_age
	Private m_vehicle
	
	Private Sub Class_Initialize()	'questo è il costruttore
		m_name = "unknown"
		m_age = 0
		msgbox "new person created"
	End Sub
	
	Public Property Get Name()
		Name = m_name
	End Property
	
	Public Property Get Age()
		Age = m_age
	End Property
	
	Public Property Let Name(newName)
		m_name = newName
	End Property
	
	Public Property Let Age(newAge) 'let permette di assegnare valori semplici
		If(newAge > 0 And newAge < 150) Then
			m_age = newAge
		Else 
			Msgbox "Invalid age"
		End If
	End Property
	
	Public Sub Birthday()
		m_age = m_age + 1
	End Sub
	
	' è una procedura alternativa a Sub che può prendere o no un argoemnto e può restituire un valore
	Public Function IsAdult()
		IsAdult = m_age >= 18 'un valore di ritorno viene restituito quando il nome della funzione
		'è uguale a qualcosa
	End Function
	
	Public Property Get Vehicle()
		Vehicle = m_vehicle
	End Property
	
	Public Property Set Vehicle(newVehicle) 'set permette di assegnare oggetti
		Set m_vehicle = newVehicle 'questo perche veicolo è un oggetto
	End Property
	
	Private Sub Class_Terminate()  'messaggio che compare quando posso rilasciare il puntatore alla classe
		msgbox "car no longer use"
	End Sub
End Class

'una funzione può restituire più valori separati da virgola come un array 
'assegnato al nome della funzione stessa. le sub sono sottoprocedure che 
'non possono restituire un valore e possono essere chiamate senza la parola
'chiave Call
'possiamo specificare se passare i parametri per valore o per riferimento:
Function fnadd(Byval num1, Byval num2) 'per valore
    num1 = 4
    num2 = 5
End Function

Function fnadd(ByRef num1, ByRef num2) 'per riferimento
    num1 = 4
    num2 = 5
End Function

Dim person1
Set person1 = New Person
person1.Name = "Gino"
person1.Birthday()

'è un linguaggio interpretato, non viene compilato
dim firstNumber
firstNumber = InputBox("Please enter a number", "First Number", 0) 
' il secondo parametro è il titolo della box, il terzo il valore di default
firstNumber = CInt(firstNumber) 'trasforma in un intero

Dim name
name = Trim(InputBox("Please enter your name", "name")) 'trim rimuove tutti gli spazi
'LTrim invece rimuove solo gli spazi prima del nome, RTrim rimuove solo quelli dopo
If Len(firstNumber) > 5 Then Msgbox "The name is" & UCase(name) 
'UCase(name) permette di scrivere in caratteri maiuscoli, LCase invece converte in minuscolo

Dim strTime
strTime = Time 'Time è una funzione di VBScript che ritorna il tempo attuale
If lnStr(1,strTime,"AM") <> 0 Then 'InStr è una funzione VBScript che ha 3 argomenti:
'il primo è da dove deve iniziare a cercare, il 2 è in quale stringa deve cercare,
'il 3 è quale stringa deve cercare
	Msgbox "The current time is" & strTime & ".Have a good morning"
Else
	REM siamo in if, REM è un modo alternativo per introdurre un commento
	msgbox "The current time is" & strTime & ".Have a good day and good night"
End If
'posso anche usare ElseIf cond Then
Dim dayOfWeek : dayOfWeek = Weekday(Date)
'Weekday ci ritorna l'intero che rappresenta il giorno della settimana
'Date è la funzione VBScript che ritorna la data corrente

'Select invece permette di fare una sorta di switch

Call Main

Sub Main
	Dim stringA, stringB
	stringA = wscript.Arguments.Item(0) 'dopo il nome dello script VB l'utente deve specificare
	stringB = wscript.Arguments.Item(1) 'due argomenti passati a queste variabili
	Select Case StrComp(stringA, stringB, vbTextCompare) 'funzione di comparazione di stringhe
	'le due stringhe da comparare e la modalità di comparazione, con vbTextCompare caratteri 
	'maiuscoli e minuscoli sono riportati come lo stesso, se rimuoviamo questo parametro allora
	'maiuscolo e minuscolo sono carratteri differenti
		case 0
			msgbox "Both the string are the same.", vbInformation, "Success" 'vbInformation è una costante di icona
		case 1
			msgbox stringA & "is grater then" & stringB, vbQuestion, "Warning"
		case -1
			msgbox stringB & "is grater then" & stringA, vbQuestion, "Warning"
		case Else
			msgbox "There is an error in string comparison", vbCritical, "Error"
	End Select
End Sub

Dim i 
Call Loop1

Sub Loop1
	For i = 1 to 10 step 2 'possiamo anche fare un for decrescente mettendo step negativo
		Msgbox "The current value of i is" & i
		If i = 5 Then Exit For
	Next
End Sub

On Error Resume Next 'è una statement VBScript che permette di non fermare lo script se c'è
'un errore,in quel caso lo script lo ignora e va avanti.
Dim objFSO, folder, file
Set objFSO = CreateObject("Scripting.FileSystemObject") 'creiamo l'oggetto file system
Set folder = objFSO.GetFolder("E:\VBSCript\Files") 'diamo il path del folder che ci interessa
'nell'oggetto file system

For each file in Folder.Files
	msgbox file.name
Next

Dim objWMIService, objHardDisks, objDrive
Const ForReading = 1, ForWriting = 1, ForAppending = 8
Set objWMIService = GetObject("winmgmts:\\"&"com-PC"&"\root\cimv2")
'il primo argomento sta per windows management, com-PC sarebbe il nome del pc,
'questo comando da un riferimento al WMI service che sta per windows management instrumentation
'service e è utile per automatizzare task amministrativi sul computer o ottenere dati di sistema

Set objHardDisks = objWMIService.ExecQuery("Select * from Win32_LogicalDisk")
'esegue una query sul WMI service e la query richiede tutti i dischi logici definiti sul pc

Set objFSO = Nothing 'distrugge l'oggetto liberando la memoria
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.OpenTextFile("E\VBScript\Files\DiskSizes.txt", ForAppending)
'apre il file indicato come primo parametro per fare l'operazione indicata come secondo
'parametro, in questo caso appendere

'possiamo usare Round(integer) per ottenere un numero approssimato

objFile.WriteLine Now 'scrive nel file la data e ora attuali

Dim index : index = 5 
Loop2

Sub Loop2
While i <= 5
	i = i +1
Wend
End Sub

Do While i<=5
	i = i +1
Loop

Do
	i = i+1
Loop While i <= 5 'eseguo quando è vera fino a che non è falsa

Do
	codice
Loop Until (condizione) 'eseguo quando è falsa fino a che non è vera

'creare un report HTML usando VBScript
Dim objFSO, objFile
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.CreateTextFile("E:\VBScript\Files\"&Date&".html", True) 
'esegue la creazione del file sull'oggetto file system, il parametro True dice di sovrascrivere
'il file se esiste già

Sub WriteHead
	With objFile 'with permette di non dover ripetere il nome dell'oggetto in ogni linea
		.WriteLine("<html")
		.WriteLine("<head>")
		.
		.
		.
		.WriteLine("</head")
	End With
End Sub

'creare un file EXCEL usando VBScript

Dim strFile
strFile = "E:\VBScript\files\"& Date&".xlsx"
FileDelete
WriteExcelReport

Sub WriteExcelReport
	Dim objExcelApp, objRange
	Set objExcelApp = CreateObject("Excel.Application") 'starta excel nel pc se installato
	With objExcelApp
		.Application.Visible = True
		.Workbooks.add
		.Cells(1,1).Value = "Report generated on" & Date 
		.Cells(1,1).Font.ColorIndex = 30
		set objRange = .ActiveCell.EntireColumn 'prendiamo un riferimento a un intera colonna
		with objRange
			.Font.Size = 12 'cambiamo il font di tutta la colonna
			.AutoFit() 'permette di formattare correttamente
		End with
		.ActiveWorkbook.SaveAs strFile
		.ActiveWorkbook.Close
		.Application.Quit
	End with
End Sub	

'Set obj1 = obj.Workbooks.open(“C:\newexcelfile.xls”)    ‘Opening an Excel file
'Set obj2=obj1.Worksheets(“Sheet1”)    ‘Referring Sheet1 of excel file
'obj2.Rows(“4:4”).Delete

obj1.Worksheets(“Sheet1”).usedrange.copy  'Copying from an Excel File1
obj2.Worksheets(“Sheet1”).usedrange.pastespecial  'Pasting in Excel File2

Sub FileDelete
	Dim objFSO
	Set objFSO = CreateObject("Scripting.FileSystemObject")
	If objFSO.FileExists(strFile) Then objFSO.DeleteFile(strFile)
End Sub

Dim fixedArray(3) 'contiene 4 elementi da indice 0 a 3, si specifica la dimensione dell'array al
'momento della dichiarazione
fixedArray(0) = "Abe"
fixedArray(1) = "Ben"
fixedArray(2) = "Chris"
fixedArray(3) = "Dustin"

wscript.echo "fixedArray dimension is" & fixedArray.Len 'scrive su linea di comando invece che box

'negli array dinamici invece non sappiamo quale sarà la dimensione del nostro array
Dim strCustomersNew()	'inizialmente non diamo una dimensione
Redim strCustomersNew(3)	'prima di mettere dati dobbiamo però definire la dimensione
strCustomersNew(0) = "Abe"
strCustomersNew(1) = "Ben"
strCustomersNew(2) = "Chris"
strCustomersNew(3) = "Dustin"
Redim Preserve strCustomersNew(5) 'permette di cambiare il numero di elementi dell'array
'la keyword Preserve ci dice che qualunque dato già esistente nell'array deve venire preservato
strCustomersNew(2) = "Eddie"
strCustomersNew(3) = "Fred"
Dim i
For i to UBound(strCustomersNew) 'UBound è una funzione VBScript che se non conosciamo la
'dimensione dell'array ce la restituisce lei
	wscript.echo "The element " & i & "is " & strCustomersNew(i)
Next

'un array può contenere dati di diversi tipi come stringhe e interi contemporaneamente
'gli array non sono limitati a una singola dimensione ma ne possono avere un 
'massimo di 60
'Split("Red $ Blue $ Yellow","$"), ha anche un 3 parametro che specifica il
'numero di stringhe da considerare
'a = array("Red","Blue","Yellow") : b = join(a,"$") è l'opposto di Split
a = array("Red","Blue","Yellow")
b = Filter(a,"B")
c = Filter(a,"e")
d = Filter(a,"Y")

Erase array      ' Free memory used by array.

'connettersi e interagire con un db usando VBScript
Dim objConnection, objRecordSet
OpenADOObjects
ShowCustomers
AddTempCostumer
UpdateCostumer
DeleteTempCostumer
CloseADOObjects

Sub OpenADOObjects
	Set objConnection = CreateObject("ADODB.Connection") 'creiamo un oggetto per eseguire la connessione
	objConnection.Open ConnectionString() 'la connectionString() è una stringa che specifica il tipo di db,
	'obj.Open“Provider=SQLQLEDB;Server=.\SQLEXPRESS;UserId=test;Password=P@123;Database
	'e altri dettagli di connessione come password e username
	Set objRecordSet = CreateObject("ADODB.Recordset") '
	objRecordSet.Open "SELECT * FRPM Customers", objConnection, 1, 3, 'indichiamo la query da eseguire
	' su objConnection, il terzo argomento è il tipo di Recordset, 1 significa adOpenKeySet che permette
	'di fare molte operazioni, mentre l'ultimo argomentoindica adLockOptimistic il tipo di lock che vogliamo
	'da quando il Recordset è impostato contiene tutte le righe delkla customer table
End Sub

Set ShowCustomers
With objRecordSet 'inizialmente punta al primo costumer
	Do while Not .EOF
		WScript.echo objRecordSet("Name") 'per ogni costumer si scrive il nome
		.MoveNext 'ci muoviamo al prossimo record
	Loop
End with
End Sub

Sub AddTempCostumer 'aggiungiamo una riga alla tabella
	objRecordSet.AddNew
	objRecordSet("CostumerID")=4
	objRecordSet("Name") = "George"
	objRecordSet.Update
End Sub

Sub UpdateCostumer
	objConnection.Execute"UPDATE Costumers SET Name = 'Gino' WHERE Name = 'George'"
End Sub

Sub DeleteTempCostumer
	objConnection.Execute"DELETE Costumers WHERE CostumerID = 4"
End Sub

Sub CloseADOObjects
	'boh
End Sub

'per andare a capo in VBScript possiamo usare _
split(allcookies, ";")

CDbl 'funzione che converte un dato di un sottotipo in double
Cint 'converte sottotipo in Int
Clng 'same  but long
CSng 'Same but single
Hex	'same ma esadecimale

FormatNumber 'una funzione che ritorna un espressione formattata come numero
FormatPercent 'una funzione che ritorna un espressione formattata come percentuale

Rnd 'ritorna un numero random tra 0 e 1

'Metodi per stringhe
'InStr ritorna la prima occorrenza della sottostringa specificata, da sinistra verso destra
'InstrRev same ma da destra verso sinistra
'Lcase ritorna la stringa in lower case
'Ucase ritorna la stringa in Upper case
'Left(String, Length) ritorna il numero del 2 parametro di caratteri dal lato 
'sinistro della stringa
'Right(String, Length) uguale ma a destra
'LTrim ritorna una stringa rimuovendo gli spazi a sinistra
'RTrim ritorna una stringa rimuovendo gli spazi a destra
'Trim rimuove sia gli spazi a sinistra che a destra
'Len ritorna la lunghezza della stringa data
'StrComp ritorna un valore intero comparando due stringhe: se la 1 stringa
'è minore della seconda ritorna -1, se sono uguali ritorna 0, altrimenti 1

'Accesso al file system
Dim oFS, drive, space
Set oFS = CreateObject("Scripting.FileSystemObject")
Set drive = oFS.GetDrive(oFS.GetDriveName("C:\"))
'su un oggetto drive possiamo usare le chiamate AvailableSpace,
'Drive.DriveLetter, driveType, FileSystem, FreeSpace, isReady, Path,
'RootFolder, SerialNumber, SharedName, TotalSize, VolumeName
'Drive è un oggetto che fornisce l'accesso alle proprietà di una particolare 
'unità disco o condivisione di rete.

Set dc = oFS.Drives 'ritorna tutti i dischi collegati al sistema

Set f = fso.GetFile("C:\user.js") 'è un oggetto che contiene sia proprietà che
'metodi per creare, eliminare o muovere un file.
'i metodi sono copy, delete, move, openasTextStream
'le proprietà sono attributes, dataCreated, DataLastAccessed, DataLastModified
'Drive, Name, ParentFolder, Path, ShortName, SHortPath, Size, Type.

Set f = oFS.GetFolder("D:\PROJECT\") 'ritorna tutti i file in una cartella
Set fc = f.Files      
'Get Item
Set s = fc.Item("sendmail.vbs")

Set f = fso.GetFolder("D:\PROJECT\") 'ottiene una cartella con Metodi
'copy, delete, move, CreateTextFile e proprietà attributes, dataCreated,
'DataLastAccessed, DataLastModified, Drive, Files, IsRootFolder, Name,
'ParentFolder, Path, ShortName,SHortPath, size, subFolders, type

'TextStream object helps the developers to work with text files seamlessly. 
'Developers can read, write or append the contents to the text file using 
'the text stream object.

Set objTextFile = objFSO.CreateTextFile("D:\Testfile.txt")
objFSO.OpenTextFile("D:\Testfile.txt",ForAppending,True)
objTextFile.WriteLine "Welcome to VBScript Programming"
objTextFile.Close

'per rilevare un errore usiamo
Err.Raise 6 
Err.Description

'possiamo usare IsEmpty per verificare se un espressione è vuota e ritorna un 
'valore booleano, IsNull per verificare se un'espressione ha dati validi e
'IsObject per verificare se un'espressione ha un oggetto valido.

Dim http
Set http = CreateObject("MSXML2.ServerXMLHTTP") 'permette di eseguire chiamate http verso
'un server remoto, inviare e ricevere i dati.

'esempio di get
http.Open "GET", "https://comunepalaia-production.up.railway.app/news", False 'false specifica che
'la richiesta deve essere sincrona, con true era asincrona
http.Send
If http.Status = 200 Then
    WScript.Echo http.responseText
Else
    WScript.Echo "Errore HTTP: " & http.Status
End If

'esempio di post
Set http = CreateObject("MSXML2.ServerXMLHTTP")

http.Open "POST", "https://example.com/api", False
http.setRequestHeader "Content-Type", "application/json"
http.Send "{""nome"":""Mario"",""cognome"":""Rossi""}"

'la prevenzione degli errori è un aspetto d gestione degli errori che
'significa prendere misurazioni effettive in uno script per evitare errori
'per prevenire errori possiamo:
'1) usare la proprietà Exist per verificare l'esistenza di un oggetto prima
'di fare una qualche operazione sullo stesso
'2) Tecniche di sincronizzazione per gestire il ritardo e l'attesa delle
'operazioni all'interno dello script
'3) usare Option Explicit per evitare problemi di parole scritte in modo errato

'Altri metodi per gestire errori sono:
'1) On Error Resume Next : muove il controllo del cursore alla linea successiva
'a dove c'è stato l'errore
'2) Oggetto Err : Metodo utilizzato per catturare i dettagli di un errore.
'Ha una lista di proprietà che sono:
'- Number : ritorna il valore intero del tipo di errore occorso
'- Description : da una descrizione dell'errore
'- Raise : permette di sollevare un errore mensionandone il numero
'- Clear : setta il gestore dell'errore a Nothing
'On Error Go To 0:
'setta l'error handler a Nothing, quindi non c'è alcun meccanismo di errore

'In VBScript il tipo VARIANT è il il tipo di dato predefinito e più flessibile. Può contenere qualsiasi tipo di dato, si adatta al tipo di valore assegnato
'Con VARIANT FAR* invece si intende il puntatore a variabile. Non si possono dichiarare puntatori a variabile direttamente, quello che si può fare è passare alla funzione una variabile che viene trattata come puntatore
'Per LPCTSTR dovrebbe bastare passare una stringa.


'ACTIVEX LABSPEC6
'Concetti utili:
'Detector : è il componente che trasforma il segnale fisico in segnale elettrico misurabile, l'occhio del sistema. Ci sono 2 tipi di Detector:
	'PMT(Photomultipler Tube) : rilevatore analogico molto sensibile alla luce debole, ha altissima sensibilità e basso rumore ma può rilevare un punto alla volta, non rileva immagini
	'CCD(Charge-Coupled Device) è un sensore digitale a matrice, usato per imaging spettrale, dove ogni pixel è un punto del campione, è meno sensibile ma ottimo per immagini e acquisire spettri completi
'La funzione Spike è un meccanismo che permette di rilevare e/o rimuovere picchi anomali nei dati acquisiti, causati normalmente da rumore elettronico, errori nel Detector, eventi casuali.
'Shutter : regola quanto tempo il sensore è esposto alla luce. Il processo di chiusura e apertura è chiamato tempo di esposizione. Deve sempre essere aperto se uso Detector PMT e chiuso dopo
'ICS (Integrated Calibration System): è un insieme di strumenti e procedure per calibrare e ottimizzare i sensori di movimento. Usato per garantire che i dati raccolti siano accurati e precisi.
'Dark Correction : procedura di correzione dei segnali di fondo o rumore di fondo che può influire sui dati raccolti, usata quando si riceve segnali da oggetti non di interesse, come il rumore.
'Binning : insieme dei pixel che vengono utilizzati insieme durante l'acquisizione per formare un singolo valore.
'Uno spettro è una rappresentazione della distribuzione dell’intensità di un segnale in funzione di una grandezza fisica come la lunghezza d'onda, la frequenza o l'energia
'Lo spettro Raman è un grafico che mostra l’intensità della luce diffusa da un campione in funzione dello scostamento in frequenza rispetto alla luce incidente, ovvero mostra quanto la luce che colpisce
'un campione cambia quando viene riflessa  o diffusa dal campione stesso, ciò aiuta a capire i legami chimici e le molecole presenti nel campione.
'Lo spettro di Raman ha 2 assi:
'Asse X : rappresenta lo spostamento di Raman(Raman shift) espresso in cm^(-1). Indica la differenza di energia tra la luce incidente e quella diffusa, correlata alle vibrazioni molecolari del campione.
'Quindi nell'origine c'è la frequenza della luce incidente. Misura quindi il cambiamento di frequenza
'Asse Y ; mostra l'intensità del segnale di Raman, proporzionale alla quantità di luce diffusa a ciascuno shift. Misura quindi la quantità di luce riflessa
'I picchi lungo l'asse X sono associati a vibrazioni specifiche delle molecole nel campione. L'altezza di ciascun picco sull'asse Y dice quanto quella vibrazione è forte o dominante.
'La frequenza è la misura di quante volte un onda si ripete in un secondo, ovvero quante oscillazioni fa l'onda luminosa in un secondo. Una luce con frequenza alta ha energia più alta. 

'Domande da fare: SPECTRUM_RTD? , MACRO_SPOT?, quale Detector usiamo(a regola CCD)?, modalità di acquisizione Detector?

'COMANDI
'ACQ: permette di iniziare un acquisizione
long Acq (long Mode, double IntegrationTime, long AccumulationNum, double From, double To)

'Attributo mode specifica la modalità di acquisizione che può essere:
'0 : ACQ_SPECTRUM (acquisizione spettrale)
'1 : ACQ_IMAGE (acquisizione CCD di immagine, con CCD si intente un sensore che converte la luce(immagine ottica) in segnali elettrici digitali, sarebbe il Detector)
'2 : ACQ_LABSPEC_PARAM (inizia un acquisizione spettrale con i parametri LabSpec, qui si fa una semplice acquisizione di uno spettro senza immagine, non cattura dati spaziali)
'3 : ACQ_SPECTRAL_IMAGE (acquisizione di immagini spettrali con parametri LabSpec, registra un cubo spettrale, e associa uno spettro a ogni pixel, quidi è quella da usare per lo spostamento, cattura info spaziali)
'4 : ACQ_GET_TEMPERATURE (ottiene la temperatura corrente del Detector)
'5 : ACQ_SPECTRUM_RTD (inizia acquisizione RTD, significa che viene acquisita anche la temperatura insieme ai dati spettrali?)
'6 : ACQ_SET_PMT_PARAMETER (setta il parametro PMT Step, non starta l'acquisizione, setta il detector PMT praticamente)
'7 : ACQ_MACRO_SPOT (inizia/stoppa la Macro spot, if IntegrationTime=0 Macro Spot ON else if IntegrationTime=1 Macro Spot OFF, dovrebbe significare che si fa una singola misura su un punto specifico del campione)
'8 : ACQ_CANCEL (cancella la corrente acquisizione)
'9 : ACQ_PMT_CCD (setta il corrente detector, IntegrationTime=1 PMT, IntegrationTime=2 CCD, in PMT mode bisogna aprire lo shutter prima di acquisire e chiuderlo dopo)
'10: ACQ_AUTO_SHOW (aggiunto a una qualsiasi modalità di acquisizione, mostra automaticamente i dati acquisiti)
'100: ACQ_NO_SPIKE_REMOVING : (disabilita la funzione di rimozione di Spike)
'200: ACQ_SINGLE_SPIKE_REMOVING : (usa Single pass Spike removing function, ovvero rimuove picchi anomali singoli)
'300: ACQ_DOUBLE_SPIKE_REMOVING : (usa doppio pass Spike removing function, ovvero rimuove picchi anomali doppi vicini tra loro, potrebbe richiedere intervento manuale per decidere quali picchi rimuovere)
'400: ACQ_DOUBLE_AUTOADD_SPIKE_REMOVING: (come la precedente ma i picchi vengono rimossi automaticamente)
'1000: ACQ_AUTO_SCANNING : (per usare AutoScanning)
'2000: ACQ_NO_CLOSE_SHUTTER : (non chiudere lo shutter dopo l'acquisizione)
'10000: ACQ_ACCUMULATION_MODE : (cambia la modalità di accumulo dei dati, immagini o segnali per ottenere il risultato finale) (media/somma/detector)
'100000: ACQ_NO_ICS : disabilita ICS
'200000: ACQ_ICS : abilita ICS
'1000000: ACQ_NO_DARK : disabilita la dark correction
'2000000: ACQ_DARK : abilita la dark correction

'IntegrationTime (in secondi, ignorato se si usa ACQ_LABSPEC_PARAM)
'0 : usa funzioni di esposizione automatica
'ACQ_ACCUMULATION_MODE : 
'0=average : il dispositivo esegue più misurazioni dello stesso segnale o spettrale e calcola la media aritmetica dei risultati
'1=sum : il dispositivo esegue più misurazioni dello stesso segnale o spettrale e somma i valori di ogni misurazione senza calcolare la media
'2=Detector : 

'AccumulationNum : numero di accumulazioni spettrali (ignorato se si usa ACQ_LABSPEC_PARAM), ovvero il numero di misurazioni spettrali da fare sullo stesso campione per avere risultati migliori

'From, To : Range di acquisizione. Se From = To la larghezza dell'acquisizione sarà la larghezza  del Detector

'Valore di ritorno: ritorna sempre 0 tranne nel caso in cui si ha ACQ_GET_TEMPERATURE dove ritorna la temperatura del Detector o -10000 se c'è un errore

'esempio di acquisizione
'inizia un acquisizione con 1 secondo di tempo di integrazione e 1 di accumulazione e senza acquisire più finestre
LabSpec.Acq ACQ_SPECTRUM + ACQ_AUTO_SHOW, 1, 1, 0, 0
Dim SpectrumID = 1

do 
	SpectrumID = LabSpec.GetAcqID() 'è una funzione che vediamo tra poco
Loop Until SpectrumID > 0

'AddID : aggiunge un data ID da salvare, tutti i dati salvati con questa funzione saranno salvati nello stesso file
long AddID(long ID)
 
'ID : data ID da salvare nella lista

'Valori di ritorno: >0 numero di ID aggiunti, -1 troppi ID aggiunti (il massimo è 1000)

'esempio 
LabSpec.AddID LabSpec.Load("C:est1.tsf") 'estensione .tfs usata per i file di configurazione di LabSpec
LabSpec.AddID LabSpec.Load("C:est2.tsf")

LabSpec.Save 0, "C:saveall.tfs", "tfs" 'vediamo dopo il comando save


'AutoFocus : fa un AutoFocus usando la corrente configurazone di LabSpec
long AutoFocus(long Mode)

'Mode specifica la modalità di autofocus:
'0 : START_AUTOFOCUS (inizia l'autofocus)
'1 : GET_AUTOFOCUS_STATUS (ottiene lo stato di autofocus(1 disturbato, 0 pronto))
'2 : STOP_AUTOFOCUS (ripristina le impostazioni precedenti)
'3 : GET_AUTOFOCUS_OFFSET (ottiene l'offset di autofocus in numero)
'4 : GET_AUTOFOCUS_STATE (ritorna 0 quando è settato a OFF, 1 quando è ON)
'5 : AUTOFOCUS_ENABLE (abilita l'autofocus)
'6 : AUTOFOCUS_DISABLE (disabilita l'autofocus)
'10: LASER_AUTOFOCUS (attiva l'autofocus basato su laser)
'11: RAMAN_AUTOFOCUS (Attiva l'autofocus basato su Raman)
'12: VIDEO_AUTOFOCUS (attiva l'autofocus per video)

'Valore di ritorno: ritorna sempre 0
'Esempio:
LabSpec.AutoFocus START_AUTOFOCUS

Dim ret 
do 
	ret = LabSpec.Autofocus (GET_AUTOFOCUS_STATE)
loop until ret = 0

Dim SpectrumID, Param
SpectrumID = 1
do 
	SpectrumID = LabSpec.GetAcqID()
loop until SpectrumID > 0

LabSpec.AutoFocus STOP_AUTOFOCUS



'ConverUnit : permette di convertire unità
double ConvertUnit(double Value, long Direction)

'Value : è il valore da convertire

'Direction :
'0 : CM1_TO_NM 
'1 : NM_TO_CM1
'2 : EV_TO_NM (ev sta per elettronVolt) 
'3 : NM_TO_EV

'Il valore di ritorno è il valore convertito



'CreateDataObject : crea uno spettro o immagine vuota
long CreateDataObject(LPCTSTR Type, long Size, long Size2, long Color)

'Type : tipo di dato, può essere
'"Spectrum" per spettro di una dimensione
'"image" per immagine in due dimensioni
'"FloatImage" per immagine in due dimensioni con tipo di dati float

'Size : la dimensione dello spettro, o prima dimensione dell'immagine

'Size2 : seconda dimensione dell'immagine

'Color : RGB Color.NO_SPECIFIED_COLOR = -1 lascia LabSpec gestire l'oggetto colore

'Valore di ritorno: se >0 è l'ID dell'oggetto, altrimenti -1 se fallisce la costruzione dell'Oggetto



'Exec : esegue comandi LabSpec
long Exec(long ID, long Command, VARIANT* pParam)

'ID : Data ID

'Command : Comando da eseguire:
'0 : SHOW_DATA 
'1 : HIDE_DATA
'2 : REMOVE_DATA (rimuove i dati dalla memoria)
'3 : CLONE_DATA (clona i dati correnti)
'4 : SHOW_STYLE (cambia lo stile del display)
'5 : SHOW_MODE (cambia la modalità di display)
'6 : SHOW_AXIS (mostra gli assi dello spettro/video o no)
'7 : HIDE_ALL (nasconde tutto lo sprettro nella finestra attiva)
'8 : GET_COLOR (ottiene il colore dell'area attiva)
'9 : SET_COLOR (setta il colore dei dati nell'area attiva)
'10: STOP_PROCESSES (stoppa tutti i video e le acquisizioni in corso)
'11: CLONE_TABLE (clona le tabelle di dati da ID a pParam)
'12: START_EXE (starta un eseguibile)

'pParam : per i comandi SHOW_*
'SHOW_DATA parametri:
'0 : SHOW_ACTIVATE (mostra e attiva i dati)
'SHOW_STYLE parametri:
'0 : SHOW_SINGLE dati singoli per vista
'1 : SHOW_OVERLAY molteplici spettri nella stessa view
'2 : SHOW_TILE una vista per spettro
'3 : SHOW_1D 1D display
'4 : SHOW_2D 2D display
'5 : SHOW_3D 3D display
'6 : SHOW_SMOOTH abilita lo smoothing
'SHOW_MODE parametri
'10000: SHOW_SCALE_NORMA_X normalizza x
'20000: SHOW_SCALE_NORMA_Y normalizza y
'1000: SHOW_SCALE_FIX_X fissa x
'2000: SHOW_SCALE_FIX_Y fissa y
'100: SHOW_SCALE_AUTO_X scala automaticamente x
'200: SHOW_SCALE_AUTO_Y scala automaticamente y
'10: SHOW_SCALE_SEP_X scala X separatamente
'20: SHOW_SCALE_SEP_Y scala y separatamente
'1: SHOW_SCALE_LOG_X log x scale
'2: SHOW_SCALE_LOG_Y log y scale
'SHOW_AXIS parametri:
'0 : AXIS_OFF non mostra gli assi
'1 : AXIS_ON mostra gli assi
'START_EXE path assoluto dell'eseguibile e parametri, se l'eseguibile contiene spazi il path deve essere tra virgolette

'Valore di ritorno: se > 0 è il clone ID, 0 : successo, -1 fallito

'esempio
Dim path 0 """C:Program Files(x86)/Notepad++/Notepad++.exe""d:myfile.txt"
LabSpec.Exec 0,START_EXE, Path



'GetAcqID : ottiene l'ID dell'ultima acquisizione di dati se disponibile e poi si resetta a -1

'Valore di ritorno: 
'>0 ID dello spettro
'0 Acquisizione in corso
'-1 Nessuna acquisizione in corso
'-2 L'acquisizione sta per essere cancellata



'GetActiveData : ottiene dati attivi di LabSpec
long GetActiveData(LPCTSTR DataType)

'DataType:
'"" : ottiene dati attivi senza tipo specifico
'"Spectrum" : Ottiene Active Spectrum
'"SpIm" : ottiene immagini o profili spettrali attivi
'"Map" : ottiene le Active Spectral Map, ovvero una mappa 2D in cui ogni pixel contiene uno spettro acquisito
'"Video" : ottiene Active video image
'"GetFirstData" : ottenere i primi dati attivi dalla finestra attiva
'"GetNextData" : ottenere i dati attivi successivi dalla finestra attiva

'Chiama GetFirstData e dopo ripeti GetNextData fino a che ID<=0 per ottenere tutti i dati dalla finestra Attiva

'Valori di ritorno: >0 Data ID, altrimenti -1 failed

Dim ID
ID = LabSpec.GetActiveData("GetFirstData")
if(ID>0) then
	LabSpec.Message "First ID: " & ID, MB_OK
	do
		ID = LabSpec.GetActiveData("GetNextData")
		If ID>0 Then LabSpec.Message "Next ID : " $ ID, MB_OK
	loop until ID<=0
End if




'GetDetectorZone : ottiene la zona attiva del detector, mettendo i valori nei parametri passati per riferimento
long GetDetectorZone(VARIANT FAR* FromX, VARIANT FAR* ToX, VARIANT FAR* BinningX,
	VARIANT FAR* FromY, VARIANT FAR* ToY, VARIANT FAR* BinningY)

'FromX : Posizione iniziale di X
'ToX : Posizione finale di X
'BinningX : X Binning orizzontale, ovvero quanti pixel orizzontali vengono messi insieme
'FromY : Posizione iniziale di Y
'ToY : Posizione finale di Y
'BinningY : Y Binning verticale

'Valori di ritorno: 0 -> successo, -1 ->failed




'GetMappingParams : ottiene la mappatura dei parametri per specifici assi
long GetMappingParams(LPCTSTR Axis, VARIANT FAR* From, VARIANT FAR* To, 
	VARIANT FAR* Step, VARIANT FAR* Mode, VARIANT FAR* Use)
	
'Axis : Motor Name (es "X", "Y")
'From : Posizione iniziale
'To : Posizione finale
'Step : Step size se Mode = INCREMENT_STEP, o numero di punti se Mode = INCREMENT_SIZE
'Mode : INCREMENT_SIZE = 0: numbero of points, 
	   'INCREMENT_STEP = 1: step size
'Use : DISABLE_AXIS = 0 : disabilita gli assi
	  'ENABLE_AXIS = 1 : abilita gli assi
		



'GetMotorPosition : ottiene la posizione attuale del motore
VARIANT GetMotorPosition(LPCTSTR MotorName, long Mode)

'MotorName : Motor Name (vediamo meglio in MoveMotor)
'Mode : 
	'0 : MOTOR_VALUE ritorna il valore del motore nella sua unità (number)
	'1 : MOTOR_STEP ritorna il valore del motore in step
	'2 : MOTOR_INDEX ritorna l'indice del motore
	'3 : MOTOR_SIZE ritorna il numero di posizioni discrete disponibili
	'4 : MOTOR_FULL_SIZE ritorna il numero di posizioni solo LS6
	'100: MOTOR_INDEXTOVALUE + Index ritorna il valore del motore in accordo
	'allo specifico indice
	'200: MOTOR_INDEXTOSTRING + Index ritorna la stringa del motore in accordo
	'allo specifico indice
	'300: MOTOR_FULL_INDEXTOVALUE + Index ritorna il valore del motore in accordo
	'allo specifico indice
	'400: MOTOR_FULL_INDEXTOSTRING + Index ritorna stringa del motore 
	'500: MOTOR_INDEXTOSTEP + Index ritorna motor step
	
	'Valore di ritorno: La posizione del motore. Se Mode = MOTOR_SIZE ritorna
	'-1 se motor non presente, 0 per motori continui(spettri), numero della posizione
	'per motori discreti (laser, filtri, ecc)


	
'GetTriggerMode : ritorna la corrente modalità Trigger (solo per script trigger)
long GetTriggerMode(LPCTSTR Mode)

'Mode :
'"BeforeAll" : ritorna 1 se prima di tutti i trigger di acquisizione
'"BeforeAcq" : ritorna 1 se prima dell'acquisizione di un Trigger
'"AfterDark" : ritorna 1 dopo dark acq, e prima della reale acq
'"AfterAcq" : ritorna 1 se dopo l'acquisizione 
'"AfterAll" : ritorna 1 se dopo tutte le acquisizioni
'"Dark" : ritorna 1 se la dark mode è abitiliata 

'valore di ritorno: 1 se Active Mode, 0 altrimenti



'GetValue : ottiene i valori 
long GetValue(longID, LPCTSTR pName, VARIANT FAR* pValue)

'ID : Data ID
'pName : tipo di valore da recuperare
	'"XYData" : ottiene un array bidimensionale contenente sia X(frequenza) che Y(intensità). Funziona solo per un singolo spettro
	'"Data" : ottiene un array contenente valori di intesità solo se i dati contengono alcuni sprettri(profili o immagini spettrali), tutti i dati sono uniti e bisogna splittarli per estrarre un singolo spettro.
	'"MapPoint:SpectrumIndex" : ottiene un singolo spettro dalla mappa. SpectrumIndex è l'inidice  dello spettro sulla mappa
	'"AxisLabels" : ottiene un Array contenente le etichette degli assi
	'"AxisUnits" : ottiene un array contenente le unità degli assi
	'"Axis" : ottiene un array a singola dimensione contenente gli assi. Questi assi sono uniti, usa "AxisSize" per ottenere la dimensione degli assi
	'"AxisIndex" : ottiene un array contenente gli indici degli assi
	'"AxisSize" : ottiene un array contenente la dimensione degli assi. L'intensity axis ha taglia 0
	'"AxisType" : ottiene un array contenente il tipo degli assi. Il tipo di assi dipende dal tipo di applicazione:
			'"intense" : intensity Axis
			'"Spectr" : frequency Axis
			'"X"
			'"Y"
			'"Z"
			'"Time" : assi del tempo
			'"DoubleCursor" : LS6 Only
			'(per il resto vedi video)
			
'pValue : array di valori

'Valore di ritorno : 0 in caso di successo, -1 altrimenti

'c'è anche GetValueEx e GetValueSimple ma è sconsigliato l'utilizzo, usarle 
'solo se GetValue non funziona (ad esempio VARIANT FAR* non supportati)



'Load : carica dati da file, usa LoadAll() se più di un dato è incluso nel file
long Load(LPCTSTR pFileName)

'pFileName : Data FileName

'Valore di ritorno: >0 DataID, -1 fallimento



'LoadAll carica tutti i dati da un file
VARIANT Load(LPCTSTR pFileName)

'Valore di ritorno: arrai di data ID



'ManageTemperature 
long ManageTemperature(long Mode, double HeatingSpeed, double HeatingTime,
	double CoolingSpeed, double CoolingTime, double HoldingTime)
	
'Mode: Modalità di riscaldamento e raffreddamento
	'CONSTANT_SPEED : usa velocità costante per riscaldamento e raffreddamento
	'CONSTANT_TIME : usa tempo costante (sec) per riscaldamento e raffreddamento
	'FREE_TEMPERATURE : libera la fase di raffreddamento
	'BACKUP_SETTINGS : Fa il backup delle impostazioni correnti
	'RESTORE_SETTING : Ripristina le impostazioni di backup
	
'HeatingSpeed : velocità di riscaldamento
'HeatingTime : tempo di riscaldamento
'CoolingSpeed : velocità di raffreddamento
'CoolingTime : tempo di raffreddamento
'HoldingTime : tempo di attesa

'Valori di ritorno: -1 nessuna tabella di linkam trovata, 0 successo



'Map : crea una mappa da uno specifico spettro, colorato da un'intensità media.
'Per mappe 2d più veloci, che conoscono dimensione e valore degli assi si
'usa MapEx()
long Map(long Mode, VARIANT FAR* DataID, VARIANT FAR* MapID, long SpectrumID,
	const VARIANT FAR& Values, const VARIANT FAR& Labels, const VARIANT FAR& Units,
	const VARIANT FAR& display, float From, float To)
	
'Mode : modalità di creazione della mappa
'0 : CREATE_MAP : crea la mappa
'1 : ADD_TO_MAP : aggiunge uno spettro alla mappa

'DataID : full data ID. Questo ID è definito se siamo in mode CREATE_MAP, e deve essere settato se siamo su ADD_TO_MAP
'MapID : Final map ID. Questo ID può essere modificato dalla funzione Map(). Non deve essere memorizzato
'SpectrumID : Spettro da aggiungere alla mappa
'Values : array di valori per lo spettro corrente, per ogni asse
'Labels : Array di etichette per ogni asse
'Units : Array di unità per ogni asse
'Display : Array di indici di assi. Setta quale asse deve essere mostrato nella mappa
	'Display(n) = X assi sulla mappa (con n numero della dimensione del display
'From : Limite di frequenza per intensità media
'To : Limite di frequenza per intensità media



'MapEx : Extended Mapping, crea una mappa da uno specifico spettro, colorata da
'un'intensità media. Usa questa funzione solo se si conosce già la dimensione
'della mappa 2D e i valori degli assi, altrimenti usa Map()
long MapEx(long Mode, long MapID, long SpectrumID, long SpectrumIndex
	const VARIANT FAR& AxisX, const VARIANT FAR& AxisY, const VARIANT FAR& Labels,
	const VARIANT FAR& Units)
	
'Mode : modalità di creazione della mappa
'0 : CREATE_MAP : crea la mappa
'1 : ADD_TO_MAP : aggiunge uno spettro alla mappa
'2 : EXTRACT_FROM_MAP : Estrae uno spettro da una mappa (valore di ritorno = spectrumID)
'MapID : setta il corrente Map ID (ignorato in CREATE_MAP)
'SpectrumID : Spettro da aggiungere alla mappa
'SpectrumIndex : Indice dello spettro da aggiungere
'AxisX : Array di valori per l'asse X 
'AxisY : Array di valori per l'asse Y
'Labels : Array di etichette per ogni asse
'Units : Array di unità per ogni asse



'Message: messaggio da mostrare in una messageBox o nella status bar
long Message(LPCTSTR pMessage, long Type)

'pMassage : messaggio da mostrare
'type : Tipo di messageBox
	'Button:
	'MB_OK = 0 singolo bottone di OK
	'MB_OKCANCEL = 1 bottoni di OK e CANCEL
	'MB_YESNO = 2 bottoni si/no
	'MB_YESNOCANCEL = 3 bottoni si/no/cancella
	'MB_RETRYCANCEL = 4 bottoni riprova/cancella 
	'MB_ABORTRETRYIGNORE = 5 Abort/retry/ignore Button
	'MB_STATUS_BAR = 6 mostra il messaggio nella status bar invece che nella box
	'MB_WAIT_FOR_EVENT = 7 popup (permette a Labspec di eseguire operazioni in background
	'MB_NON_BLOCKING = 8 popup non modal Message Box e ritorna immediatamente
	'MB_MULTI_BUTTONS = 9 popup una modal messag box con 10m bottoni
	'Icon:
	'MB_INCONEXCLAMATION = 10 
	'MB_ICONINFORMATION = 20
	'MB_ICONQUESTION = 30
	'MB_ICONSTOP = 40
	'MB_ICONWARNING = 50
	'MB_ICONERROR = 60
	'MB_ICONHAND = 70
	
'Valori di ritorno:
'0 : ID_OK
'1 : ID_YES
'2 : ID_NO
'3 : ID_CANCEL
'4 : ID_ABORT
'5 : ID_IGNORE
'6 : ID_RETRY

'se MB_NON_BLOCKING : 0 : popup closed, 1 popup Open



'MessageEx : apre un avanzata finestra di dialogo (InputBox e open/save file)
BSTR  MessageEx(LPCTSTR Message, long Type)

'pMessage : 
'MB_INPUTBOX = 0 : messaggio da mostrare
'MB_OPEN_FILE = 1 :  l'estensione del file da aprire
'MB_SAVE_FILE = 2 : estensione del file da salvare
'MB_FROM_TO_INPUT = 4 : messaggio da mostrare
'MB_BROWSE_FOR_FOLDER = 5 : carica la dialog Message
'MB_TRACE_DEBUG = 13 : DebugFileName;DebugText
	
'type : 
'MB_INPUTBOX = 0 : input box, chiede all'utente di inserire qualche informazione
'MB_OPEN_FILE = 1 :  mostra la finestra standard per aprire file
'MB_SAVE_FILE = 2 : mostra la finestra standard per salvare file
'MB_FROM_TO_INPUT = 4 : chiede all'utente di inserire alcune informazioni
'MB_BROWSE_FOR_FOLDER = 5 : finestra di visualizzazione standard per la ricerca delle cartelle
'MB_TRACE_DEBUG = 13 : memorizza informazioni di debug in un file di testo
'MB_STOP = 14 : stoppa l'esecuzione

'Valori di ritorno:
'MB_INPUTBOX = 0 : user message
'MB_OPEN_FILE = 1 :  file path
'MB_SAVE_FILE = 2 : file path
'MB_FROM_TO_INPUT = 4 : froms#to
'MB_BROWSE_FOR_FOLDER = 5 : folder path
'MB_TRACE_DEBUG = 13 :
'MB_STOP = 14 : 1 se stop è cliccato, 0 altrimenti



'MoveMotor : muovere un motore specificato
long MoveMotor(LPCTSTR MotorName, double PositionValue, LPCTSTR PositionName,
	long Mode)
	
'MotorName : Motor Name
	'"Spectro" : Spectrometer motor (nm)(step)
	'"Premono" : ForeMonochromator (nm)(step)
	'"Grating" : Grating motor (gr/mm)(index)
	'"Slit" : Slit motor (um)(step)
	'"Hole" : Hole motor (um)(step)
	'"X" : motore della direzione di scena (device attivo)
	'"Y" : motore della direzione di scena (device attivo)
	'"XL": motore della direzione di scena (stage attivo)
	'"YL": motore della direzione di scena (stage attivo)
	'"XT": motore della direzione di scena (device di scanning attivo)
	'"YT": motore della direzione di scena (device di scanning attivo)
	'"Z" : motore z
	'"Laser" : motore laser

'PositionValue : Valore da raggiungere
'PositionName : solo per motori con posizioni nominate (microscopi,...)
'Mode: Motor Mode
	'0 : MOTOR_VALUE setta il valore nella sua unità
	'1 : MOTOR_STEP setta il valore in step
	'2 : MOTOR_INDEX setta l'indice del motore
	'3 : MOTOR_STRING setta il motore usando la stringa
	'4 : MOTOR_CALIBRATE calibra il motore
	'5 : MOTOR_ORIGIN setta la posizione corrente come origine
	'6 : MOTOR_STOP stoppa il motore specificato
	'7 : VALUE_TO_STEP Converte Value (positionValue) in Step (Return Value). Non muove il motore
	'10: MOTOR_NO_WAIT se aggiunto al valore, il motore partirà, e il comando ritornerà immediatamente
	'100: MOTOR_NO_MESSAGE se aggiunto, il motore non informa che ha cambiato posizione


'Valore di ritorno: >0 MoveID, -1 fallimento
'se VALUE_TO_STEP ritorna Motor Step

'Paint : permette di disegnare una text box in una finestra collegato da una 
'freccia a uno spettro. è disponibile anche l'esportazione a Windows Meta file
long Paint(long Mode, long SpectrumID, float Value, double PosX, double PosY,
	double SizeX, double SizeY, LPCTSTR Text)
	
'Mode: Draw mode
'0 : ADD_BOX aggiunge una Box all'area
'1 : REMOVE_BOXES rimuove tutte le box
'2 : EXPORT_WMF : se value = 0, esporta la finestra attiva in un file WMF,
'se value = 1 esporta SpectrumID in un WMF file. Path di destinazione devono esistere
'3 : ACTIVATE_WINDOW : attiva una finestra presente per tipo
'SpectrumId : Spectrum ID (solo per ADD_BOX)
'Value : ADD_BOX : valore di frequenza, il livello di intensità è automaticamente rilevato.
'PosX : posizione degli angoli superiori del box
'PosY : posizione degli angoli sinistro del box
'SizeX : Box X Size (in % alla finestra)
'SizeY : Box Y Size (in % alla finestra)
'Text : ADD_BOX : Text che verrà mostrato nella box
		'EXPORT_WMF : WMF path e nome file
		
'Valore di ritorno: 0 OK, -1 rilevato un errore



'Pause : mette in pausa l'esecuzione dello script
long Pause(double Time)

'Time : Pause Time(ms)

'Print : disegna l'area Attiva
long Print(long Mode)

'Mode: Print Mode
'0 : FILE_PRINT_PREVIEW lancia la dialog print preview
'1 : FILE_PRINT_PAGE_SETUP lancia la dialog di page setup
'2 : FILE_PRINTER_SETUP lancia dialog printer setup preview 
'3 : FILE_PRINT disegna l'aria attiva
------------------------------------------------------------------------
'SEND : invia dati a un device esterno
VARIANT Send(LPCTSTR To, LPCTSTR Command, const VARIANT FAR& Param, long Mode,
	VARIANT FAR* Status)
	
'To : Device Name
'Command : comando da inviare 




--------------------------------------------------------------------------



'SetAutoExposure : parametri sono resettati ai correnti parametri di LabSpec
'alla fine dell'acquisizione, questa funzione deve quindi essere chiamata prima di acq()
long SetAutoExposure(double TestTime, double MinTime, double MaxTime,
	double DesiredIntensity)ù
	
'TestTime : tempo di esposizione utilizzato per testare l'intensità del segnale
'MinTime : Minimo tempo di esposizione
'MaxTime : massimo tempo di esposizione
'DesiredIntensity : intensità da raggiungere



'SetDetectorZone, per impostare la zona del detector
long SetDetectorZone(long FromX, long ToX, long BinningX, long FromY, long toY,
	long BinningY,)
	
'FromX : X start position
'ToX : X stop position
'BinningX : X Binning
'FromY : Y start position
'ToY : Y stop position
'BinningY : Y Binning

'Valore di ritorno: 0 successo, -1 altrimenti



'SetMappingParams per specifici assi
long SetMappingParams(LPCTSTR Axis, double Form, double To, double Step, long Mode,
	long Use)
	
'Axis : Motor Name
'From : posizione iniziale
'To : posizione finale
'Step : Step size se Mode = INCREMENT_STEP, numero di punti se Mode = INCREMENT_SIZE
'Mode:
'INCREMENT_SIZE = 0 : setta il numero di punti
'INCREMENT_STEP = 1 : setta step size
'USE_ONLY = 2 : abilita/disabilita solo gli assi
'DISABLE_ALL_MOTORS = 3 : disabilita tutti gli assi
'Use: DISABLE_AXIS = 0 disabilita gli assi, ENABLE_AXIS = 1 abilita gli assi



'SetScale
long SetScale(double FromX, double ToX, double fromY, double ToY)

'FromX : X from limit
'ToX : X to limit
'FromY : Y from limit
'ToY : Y to limit



'SetScriptParamOptions
long SetScriptParamOptions(LPCTSTR Description, long Mode)
' deve essere usato prima di chiamare SetConfigOptions per settare tutti i parametri

'Description: breve descizione dello script, da mostrare nella pag di configurazone
'showMode: opzioni per mostrare la dialog:
'0 : SHOW_ONCE mostra la dialog di configurazione una volta sola la prima volta che lo script viene lanciato
'1 : SHOW_ALWAYS mostra la dialog di configurazione ogni volta che lo script viene lanciato
'2 : SHOW_NEVER non mostra mai la dialog di configurazione

'Valori di ritorno:
'0 : la prima volta che lo script viene lanciato
'1 : lo script è stato già lanciato prima



'SetSingleScriptParam imposta i parametri dello script accessibili tramite GUI
long SetSingleScriptParam(LPCTSTR Name, LPCTSTR Unit, const VARIANT FAR& Value,
	long Mode)
	
'Name : Parameter Name
'Unit : Parameter Unit o broswe button 
	'per aggiungere un pulsante di esplorazione delle cartelle : Unit="BrowseForFolder;Dialog title msg"
	'per aggiungere un pulsante di salvataggio dei file: Unit="BrowseSaveFile;Dialog title msg;File extention"
	'per aggiungere un pulsante di apertura dei file: Unit="BrowseOpenFile;Dialog title msg;File extention"
'Value : Valori di default dei parametri. Il tipo dei parametri verrà controllato
'in configurazione
'Mode : Parameter mode
'0 : PARAM_DEFAULT : Imposta un parametro come default, e recupera il valore dalla pagina di configurazione
'1 : PARAM_OVERWRITE : sovrascrive il parametro, anche se è già stato salvato nella pagina di configurazione
'2 : PARAM_SAVE_INTERNAL : Salva parametri interni. i parametri interni non sono
'accessibili alla GUI, ma possono essere recuperati dallo script per il backup.
'3 : PARAM_RESTORE_INTERNAL : Recupera i parametri interni. i parametri devono essere salvati prima di venir recuperati
'4 : PARAM_LOAD_FROM_FILE : carica una lista di parametri interni da file
'5 : PARAM_SAVE_TO_FILE : salva una lista di parametri interni in un file
'6 : PARAM_REMOVE_INTERNAL : rimuove parametri dalla lista



'Template : carica/ salva Template
long Template(long Mode, LPCTSTR Param, VARIANT FAR* Value)

'Mode: Template Mode
'0 : LOAD_TEMPLATE carica un template dalla lista dei template
'1 : SAVE_TEMPLATE salva un template nella lista dei templete
'2 : ADD_TO_TEMPLATE_LIST aggiunge il template alla lista dei template custom
'3 : TEMPLATE_SET_VALUE setta un valore per uno specifico parametro
'4 : TEMPLATE_GET_VALUE ottiene il valore corrente del parametro
'5 : APPLY_TEMPLATE applica il templete specifico
'6 : GET_TEMPLATE_STATUS controlla stato applicativo
'7 : SAVE_CURRENT_CONFIG salva la configurazione corrente come template
'8 : TEST_TEMPLATE testa se il template è caricato e se è disponibile nel sistema
'9 : APPLY_TEMPLATE_NO_SPECTRO applica lo specifico templete senza muovere lo spectrometro

'Param : parameter name
'LOAD_TEMPLATE, SAVE_TEMPLATE, ADD_TO_TEMPLATE_LIST, APPLY_TEMPLATE
'Templete Name: TEMPLETE_SET_VALUE e TEMPLETE_GET_VALUE:
'"Laser", "Filter", "Accum", "Spike", "AutoExposure", "AutoFocus", "Grating"
'"RamanPolarizer", "LaserPolarizer", "CentralPosition", "PositionFrom", "PositionTo",
'"Expo", "Hole", "Slit", "AutoExposureMin", "AutoExposureMax", "ExtendedRange", "Objective"

'Valore di ritorno: GET_TEMPLATE_STATUS ritorna 1 mentre è applicato e 0 quando è fatto



'TickCount : recupera il numero di millisecondi che sono passati da quando
'il sistema è iniziato.
long TickCount()

'Valore di ritorno: Tempo trascorso (ms)



'Treat : funzione di trattamento (filtro, adattamento del picco, rimuovere baseline)
long Treat(long ID, LPCTSTR FunctinName, long FunctionMode, VARIANT FAR* Param1,
	VARIANT FAR* Param2, VARIANT FAR* Param3, VARIANT FAR* Param4, 
	VARIANT FAR* Param5, VARIANT FAR* Param6)
	
'ID : SpectrumID
'FunctionName : tratmente function name ci sono 3 opzioni vediamole

'1 OPZIONE FunctionName = "Filter" : Filtra le routine
'FunctionMode : 
'0 FILTER_START : inizia a filtrare con parametri specifici,
'se ritorna -1 significa Unknown filter, altrimenti ritorna 0 OK
'1 FILTER_GET_STATE : ottieni lo stato del filtro, ritorna -1 se l'operazione
'è in corso, 0 se è stata eseguita.
'Param1 : tipo di filtro
'0 FILTER_SMOOTH : smoothing filter
'1 FILTER:DER1 : filtro derivativo di 1 ordine
'2 FILTER_DER2 : filtro derivatico di 2 ordine
'3 FILTER_MEDIAN : Filtro mediano
'4 FILTER_FFT : filtro FFT
'5 FILTER_DENOISER : per rimuover il rumore
'10 FILTER_INTERPOLATE : filtro di interpolazione

'Param2 : grado
'Param3 : size
'Param4 : Binning (FILTER_INTERPOLATE solo), 0 polynomial interpolation, 1 binning interpolation
'Param5 : Factor(FILTER_FFT e FILTER_DENOISER solo) (double) 0.0 - 100.0

'2 OPZIONE FunctionName = "PeakFitting" : Peak Fitting routine, ritorna -1 se SpectrumID è sconosciuto, 0 se OK
'FunctionMode : 0 PEAKFIT_ADD_PEAK : aggiunge un picco da adattare
'Param1 : PeakID int o per NbPeaks
'Param2 : Peak Position : float 
'Param3 : Peak intensity : float
'Param4 : Peak Width : float
'Param5 : Gauss/Loren Ratio : float
'Param6 : Formula : String : "Gauss()", "Loren()" o "GaussLoren()"

'FunctionMode : 1 PEAKFIT_START : inizia l'adattamento, ritorna -1 se SpectrumID è sconosciuto, 0 se OK
'Param1 : Baseline correction : int 
	'PEAKFIT_NO_BASELINE = 0 
	'PEAKFIT_BASELINE = 1
	'PEAKTFIT_USE_EXISTING_BASELINE : usa la baseline già esistente
'Param2 : Numero di iterazioni : int 
'Param3 : Max peak shift : double : Default 0
'Param4 : Max peak width : double : Default 0
'Param5 : Max peak width : double : Default 0
'Param6 : Baseline Formula : String : se non specificato il valore di default è "b+c*xn+d*xn*xn"

'FunctionMode : 2 PEAKFIT_GET_RESULT : ritorna lo stato e il risultato dell'adattamento, ritorna -1 se SpectrumID è sconosciuto, 0 se OK
'Param1 : PeakID int o per NbPeaks
'Param2 : Peak Position : float 
'Param3 : Peak intensity : float
'Param4 : Peak Width : float
'Param5 : Gauss/Loren Ratio : float
'Param6 : Peak area : float

'FunctionMode : 3 PEAKFIT_FIX : fissa o unfissa una specifica variabile di adattamento, ritorna -1 se SpectrumID è sconosciuto, 0 se OK
'Param1 : PeakID int o per NbPeaks
'Param2 : Var to Fix/unFix : str "P", "A", "W", "G", "B", "C" o "D"
'Param3 : Fix value : 1 to Fix, 0 to unFix

'FunctionMode : 4 PEAKFIT_ADD_BASELINE : adatta una baseline, ritorna -1 se SpectrumID è sconosciuto, 0 se OK
'Param1 : Baseline degree
'Param2 : Baseline max point
'Param3 : Substraction (0:fit, 1: fit+substract)

'3 OPZIONE FunctinName = "RemoveBaseline" : Rimuove la baseline
'Function mode non è utilizzato
'Param1 : grado polinomiale (int)
'Param2 : non usato
'Param3 : non usato
'...



'Video mostra immagini video 
long Video(long Mode)

Mode: Start/Stop Video
'0 : START_VIDEO 
'1 : STOP_VIDEO
'2 : GET_VIDEO_ID
'3 : START_EXTENDED_VIDEO
'4 : GET:ACTIVE_CAMERE
'10+CameraID : SET_ACTIVE_CAMERA

'valore di ritorno >0 VideoID, 0 OK, -1 Error