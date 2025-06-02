# Music Sync App

Una semplice app GUI per sincronizzare musica tra una cartella locale del PC e un dispositivo Android tramite ADB (Android Debug Bridge) over Wi-Fi.

---

## Caratteristiche

- Scansione della rete locale per dispositivi Android con ADB attivo sulla porta 5555
- Connessione automatica ad uno o più dispositivi via Wi-Fi
- Sincronizzazione solo dei nuovi brani musicali (.mp3, .m4a)
- Sincronizzazione cancellando prima tutta la musica presente sul dispositivo
- Cancellazione completa dei file musicali dal dispositivo
- Visualizzazione in tempo reale dello stato e progresso
- Salvataggio delle impostazioni (cartella locale, tema, IP auto-connessi, range IP per scansione)
- Interfaccia grafica basata su Tkinter e ttkbootstrap con temi chiari/scuri
- Tooltip di aiuto per alcune opzioni

---

## Requisiti

- Python 3.x
- adb installato e configurato nel PATH
- nmap installato (per la scansione dei dispositivi)
- Libreria Python `ttkbootstrap`
  
```bash
pip install ttkbootstrap

Come usare

    Avvia l'applicazione (python music_sync_app.py o come si chiama il file).

    All'avvio, se non configurato, ti verrà chiesto di inserire il range IP della tua rete locale (es. 192.168.1.0/24).

    Usa il pulsante Scan for Devices per cercare dispositivi Android con ADB over Wi-Fi attivo.

    Seleziona un dispositivo dalla lista per connetterti.

    Puoi ora scegliere tra:

        Sincronizzare solo le nuove canzoni

        Cancellare la musica sul dispositivo e poi sincronizzare

        Cancellare tutta la musica dal dispositivo

    Usa il pannello Settings per cambiare la cartella locale della musica, il tema, e modificare il range IP per la scansione.

    Premi Stop per fermare eventuali operazioni in corso.

Struttura del codice

    MusicSyncApp — classe principale che gestisce la GUI e le operazioni

    Funzioni per:

        Scansione rete con nmap

        Connessione ADB via Wi-Fi

        Lettura/scrittura file musicali locale e dispositivo

        Calcolo hash file

        Gestione impostazioni salvate in JSON (~/.music_sync_settings.json)

        Threading per mantenere la GUI reattiva

Note

    Assicurati che il dispositivo Android abbia abilitato il debug USB e l'ADB over Wi-Fi (porta 5555).

    L'app utilizza comandi di sistema adb e nmap; devono essere presenti e funzionanti nel PATH.

    Il percorso di destinazione della musica sul dispositivo è hardcoded in /sdcard/Music.

    La sincronizzazione si basa sul nome file, non sul contenuto.

    Usa con cautela la funzione di cancellazione: elimina TUTTI i file musicali nella cartella destinazione.

Licenza

Questo progetto è rilasciato sotto licenza MIT.
Sentiti libero di modificarlo e adattarlo alle tue esigenze.
Contatti

Per domande o contributi: apri una issue o invia una pull request su GitHub.
