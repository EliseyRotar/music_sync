🎵 Music Sync App

Music Sync App è una GUI in Python che permette di sincronizzare automaticamente la tua musica tra il tuo computer e il tuo dispositivo Android via ADB (USB o Wi-Fi). Supporta la sincronizzazione solo dei brani nuovi, la cancellazione di tutta la musica prima della sincronizzazione e la scansione della rete per dispositivi ADB.
🧠 Funzionalità principali

    🔍 Scansione della rete per dispositivi ADB connessi via Wi-Fi (porta 5555)

    📂 Sincronizzazione intelligente: copia solo i file musicali non ancora presenti nel dispositivo

    💣 Modalità "Clear and Sync": cancella la musica esistente e poi sincronizza tutto da capo

    ❌ Elimina solo i file musicali dal dispositivo

    📡 Connessione automatica ai dispositivi salvati

    💾 Salvataggio delle impostazioni in un file JSON locale

    🎨 Interfaccia moderna con ttkbootstrap

    🛑 Stop per interrompere il task corrente

🧰 Requisiti

    Python 3.7+

    ADB (Android Debug Bridge)

    nmap installato nel sistema per la scansione IP

    Moduli Python:

        ttkbootstrap

        tkinter (incluso nella maggior parte delle distribuzioni Python)

        Altri moduli standard: os, subprocess, socket, hashlib, json, threading, ipaddress

Installa ttkbootstrap con:

pip install ttkbootstrap

🚀 Avvio dell'app

Assicurati che ADB sia configurato e che il tuo dispositivo Android sia connesso via USB o Wi-Fi (porta 5555 abilitata).

Esegui l'app con:

python3 nome_script.py

📁 Percorsi predefiniti

    Cartella locale della musica: ~/Spotube

    Cartella di destinazione nel dispositivo: /sdcard/Music

    File di configurazione: ~/.music_sync_settings.json

⚙️ Impostazioni configurabili

Le impostazioni vengono salvate automaticamente e includono:

    Cartella locale della musica

    Tema dell'interfaccia grafica (darkly, litera, ecc.)

    Lista degli IP dei dispositivi con connessione automatica

    Range IP per la scansione (192.168.x.0/24)

💻 Funzioni principali dell’interfaccia
Pulsante	Descrizione
Scan for Devices	Scansiona la rete alla ricerca di dispositivi ADB via Wi-Fi
Check ADB Connection	Verifica che ADB sia correttamente connesso al dispositivo
Sync Only New Songs	Sincronizza solo i brani assenti sul dispositivo
Clear and Sync	Elimina tutti i brani nel dispositivo e sincronizza tutto da capo
Delete Only Music Files	Elimina solo i file musicali dal dispositivo
Settings	Modifica la cartella locale o il tema dell’interfaccia
Stop	Interrompe l'operazione corrente
🧪 Testato su

    Android 10+ con ADB abilitato

    Linux (Arch Linux, Debian)

    Desktop environment: GTK/Hyprland

🛟 Note importanti

    Verifica che la modalità debug USB sia attiva sul tuo dispositivo.

    Per usare ADB via Wi-Fi, puoi eseguire sul dispositivo:

    adb tcpip 5555
    adb connect <device_ip>:5555

📜 Licenza

Questo progetto è open-source. Usalo, miglioralo e condividilo!
