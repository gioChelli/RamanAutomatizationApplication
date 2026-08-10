Il software RamanAutomatizationApplication è stato sviluppato per interagire attraverso l'intermediazione di un server con il microscopio LabSpec 6 di Horiba.
Lo scopo del software è quello consentire l'associazione in coordinate micron tra vetrini contenenti sezioni dello stesso tessuto con colorazione oppure no e
attraverso questa associazione consentire l'acquisizione di spettri Raman sulle sezioni senza colorazione a partire dalla selezione della zona di acquisizione 
dalla corrispettiva sezione con colorazione.

Per un corretto funzionamento della procedura il protocollo da seguire è il seguente:
- Avvio del server_raman, contenuto nella cartella Raman_server, da terminale dopo la configurazione dei parametri nel corrispettivo file JSON
- Avvio dello script LabSpec_matching_operation, contenuto nella cartella LabSpec_script, sul software proprietario Horiba
- Avvio dell'applicazione RamanAutomatizationApplication

Le precedenti operazioni possono essere eseguite in un qualunque ordine.
A partire da questa configurazione nel primo notebook dell'interfaccia dell'applicazione è possibile utilizzare avviare un acquisizione del mosaic di un vetrino oppure caricare un vetrino già
acquisito precedentemente. Sul mosaic caricato o acquisito è poi possibile avviare l'analisi che permettte di andare a identificare le coordinate delle
sezioni all'interno del vetrino e deve essere fatta prima di avviare una qualsiasi operazione di matching con il vetrino stesso.

Nel secondo notebook è possibile andare a selezionare il vetrino del campione colorato e di quello naturale da utilizzare per l'associazione attraverso la selezione
del mosaic in cui sono contenuti dal file system. A questo punto è possibile far partire la fase di matching che può richiedere un numero variabile di minuti e 
restituirà la rotazione ottimale individuata.

Dopo aver eseguito il matching sarà attivo anche il terzo notebook che invece consente di selezionare una o più celle dal campione colorato (visualizzato a grandezza 5x)
e richiedere attraverso la selezione del pulsante o acquisizione a più alta risoluzione oppure acquisizioni Raman su quelle celle alla distanza impostata nel 
parametro utente che è possibile modificare attraverso interfaccia.
In questo caso è importante ricordare che è necessaria nuovamente l'interazione con l'hardware è necessario:
- Nel caso di acquisizione a più alta risoluzione bisogna selezionare manualmente nel microscopio l'obiettivo ottico successivo alla risoluzione visualizzata nell'applicazione.
- Nel caso di acquisizione Raman è necessario impostare il microscopio 50x e spegnere tutte le luci, comprese quelle ambientali.

Naturalmente tutte le operazioni di interazione con l'hardware saranno disponibili solo se questo è effettivamente connesso.

Nella cartella LabSpec_script è presente anche lo script setStartSlide che consente di andare a settare come origine degli assi utilizzati dal microscopio
il punto dove inizia il vetrino caricato nell'hardware. Questo script è utile quando un vetrino già acquisito viene ricaricato nell'hardware mentre nell'applicazione 
RamanAutomatizationApplication viene utilizzato il mosaic acquisito precedentemente. Andando a settare l'origine a inizio vetrino, proprio come succede durante 
un'acquisizione le coordinate in micron del software proprietario andranno a coincidere nuovamente con quelle sul software RamanAutomatizationApplication.

Nella cartella Raman_server invece è presente lo script merge_image che è quello che viene avviato e sfruttato dal server per creare il mosaic con le immagini
che gli vengono inviate dal LabSpec.

In risultati_raman_pancreas è possibile vedere lo spettro medio Raman calcolato con 25 acquisizioni su pancreas avviate dall'applicazione come risultato di test.
In tessuti invece sono contenute le cartelle di ogni vetrino acquisito per tetare il funzionamenteo dell'algoritmo di matching e la validazione dei risultati. Per ogni vetrino è già stata acquisita la
fasa di analisi (necessaria per il matching) e sono quindi visibili le varie cartelle di ogni cella del pattern e i contorni individuati per la fase di matching.

Infine il file VBS dummy_LabSpec6 è lo script utilizzato per simulare una connessione al dispositivo LabSpec quando questo non era disponibile.
Durante la fase di acquisizione di immagini è possibile inviare immagini acquisite precedentemente mentre per la fase di acquisizioni Raman si può utilizzare l'invio di
un file txt che rappresenta acquisizione Raman già eseguita. Questo script può essere avviato da terminale utilizzando il comando wscript.
