# 🐙 Octopus PowerUp Helper per Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-v1.0.0-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)

Un Custom Component avanzato per Home Assistant dedicato agli utenti di **Octopus Energy Italia**. 
Questa integrazione replica fedelmente l'algoritmo di Octopus per calcolare la tua **Baseline** (Consumo Abituale), permettendoti di massimizzare il risparmio durante gli eventi PowerUp.
 
## ✨ Caratteristiche
- ⚙️ **Configurazione UI (Config Flow):** Nessun file YAML da modificare. Si configura tutto dall'interfaccia grafica.
- 🧠 **Algoritmo Intelligente (Regolamento 2026):** Calcola la media basandosi sui 10 giorni precedenti della **stessa tipologia** (distingue automaticamente tra giorni feriali e fine settimana/festivi).
- 📊 **Calcolo Dinamico:** Usa il database storico di Home Assistant (`recorder`) per calcolare la media esatta dei consumi nella fascia oraria scelta.
- 🕒 **Selettori Orario Nativi:** Genera automaticamente le entità `time` per selezionare l'ora di inizio e fine direttamente dalla tua Plancia.
- 🌞 **Perfetto per il Fotovoltaico e non:** Calcola il delta basandosi esclusivamente sull'energia prelevata dalla rete.

## 🔬 Come funziona il Calcolo
L'integrazione segue rigorosamente i Termini e Condizioni di Octopus Energy Italia:
- **Se il PowerUp è Feriale (Lun-Ven):** Il sensore cercherà i 10 giorni feriali precedenti, ignorando i weekend.
- **Se il PowerUp è Festivo (Sab-Dom):** Il sensore cercherà i 10 giorni festivi precedenti, ignorando i giorni lavorativi.

Questo garantisce che la baseline visualizzata su Home Assistant sia la stessa identica usata da Octopus per calcolare il tuo rimborso in bolletta.

## 📦 Installazione

### Metodo 1: Tramite HACS (Consigliato)
Questa integrazione non è ancora in HACS di default, ma puoi aggiungerla come repository personalizzato.

1. Apri **HACS** nel tuo Home Assistant.
2. Clicca sui tre puntini in alto a destra e seleziona **Repository personalizzati**.
3. Incolla l'URL di questo repository: `https://github.com/SalvatoreITA/Octopus-PowerUp-Helper`
4. Scegli la categoria **Integrazione** e clicca su Aggiungi.
5. Cerca "Octopus PowerUp Helper" in HACS, clicca su **Scarica** e riavvia Home Assistant.

### Metodo 2: Manuale
1. Scarica l'ultima release da questo repository.
2. Copia l'intera cartella `octopus_powerup` all'interno della cartella `custom_components/` del tuo Home Assistant.
3. Riavvia Home Assistant.

## ⚙️ Configurazione

Dopo aver riavviato Home Assistant:
1. Vai su **Impostazioni** > **Dispositivi e Servizi**.
2. Clicca su **Aggiungi Integrazione** in basso a destra.
3. Cerca **Octopus PowerUp Helper**.
4. Nel menu a tendina, seleziona il tuo sensore di **Prelievo dalla Rete** (es. `sensor.energia_oggi_prelevata`). 
   *Nota: Deve essere un sensore di energia cumulativo kwh (giornaliero, mensile o totale).*
5. Clicca su Invia. Finito!

## 🕹️ Entità Generate

L'integrazione creerà automaticamente 3 entità:
- `sensor.baseline_octopus_10_giorni`: Il sensore che mostra i kWh medi da superare. Si aggiorna all'istante al cambio dell'orario.
- `time.inizio_powerup`: Selettore per l'ora di inizio della sfida.
- `time.fine_powerup`: Selettore per l'ora di fine della sfida.

Puoi aggiungere queste entità a qualsiasi plancia per monitorare la tua strategia durante i PowerUp!

> **💡 Vuoi una grafica dedicata?**
> Scarica anche la Custom Card frontend ufficiale da HACS: [DomHouse Octopus Powerup Card](https://github.com/SalvatoreITA/DomHouse-Octopus-PowerUp-Card)

## ☕ Supporta il Progetto

Ogni piccolo supporto fa un'enorme differenza: mi aiuta a mantenere vivo l'entusiasmo e mi stimola a creare e condividere nuove soluzioni per la community. Grazie di cuore per il tuo aiuto! 🚀

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/salvatore_dh)

## ❤️ Crediti
Sviluppato da [Salvatore Lentini - DomHouse.it](https://www.domhouse.it)
