# 🐙 Octopus PowerUp Helper per Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Maintainer](https://img.shields.io/badge/maintainer-Il_Tuo_Nome-blue.svg)](https://github.com/tuo_username)

Un Custom Component per Home Assistant dedicato agli utenti di **Octopus Energy Italia**. 
Questa integrazione calcola automaticamente la tua **Baseline dei 10 giorni precedenti** in base alla fascia oraria del "PowerUp", permettendoti di sapere esattamente quanta energia devi consumare per ottenere lo sconto in bolletta.

## ✨ Caratteristiche
- ⚙️ **Configurazione UI (Config Flow):** Nessun file YAML da modificare. Si configura tutto dall'interfaccia grafica.
- 📊 **Calcolo Dinamico:** Usa il database storico di Home Assistant (`recorder`) per calcolare la media esatta dei consumi nella fascia oraria scelta.
- 🕒 **Selettori Orario Nativi:** Genera automaticamente le entità `time` per selezionare l'ora di inizio e fine direttamente dalla tua Plancia.
- 🌞 **Perfetto per il Fotovoltaico:** Calcola il delta basandosi esclusivamente sull'energia prelevata dalla rete.

## 📦 Installazione

### Metodo 1: Tramite HACS (Consigliato)
Questa integrazione non è ancora in HACS di default, ma puoi aggiungerla come repository personalizzato.

1. Apri **HACS** nel tuo Home Assistant.
2. Clicca sui tre puntini in alto a destra e seleziona **Repository personalizzati**.
3. Incolla l'URL di questo repository: `https://github.com/tuo_username/ha-octopus-powerup`
4. Scegli la categoria **Integrazione** e clicca su Aggiungi.
5. Cerca "Octopus PowerUp Helper" in HACS, clicca su **Scarica** e riavvia Home Assistant.

### Metodo 2: Manuale
1. Scarica l'ultima release da questo repository.
2. Copia l'intera cartella `octopus_powerup` all'interno della cartella `custom_components/` del tuo Home Assistant.
3. Riavvia Home Assistant.

---

## ⚙️ Configurazione

Dopo aver riavviato Home Assistant:
1. Vai su **Impostazioni** > **Dispositivi e Servizi**.
2. Clicca su **Aggiungi Integrazione** in basso a destra.
3. Cerca **Octopus PowerUp Helper**.
4. Nel menu a tendina, seleziona il tuo sensore di **Prelievo dalla Rete** (es. `sensor.energia_oggi_prelevata`). 
   *Nota: Deve essere un sensore di energia cumulativo (giornaliero, mensile o totale).*
5. Clicca su Invia. Finito!

## 🕹️ Entità Generate

L'integrazione creerà automaticamente 3 entità:
- `sensor.baseline_octopus_10_giorni`: Il sensore che mostra i kWh medi da superare. Si aggiorna all'istante al cambio dell'orario.
- `time.inizio_powerup`: Selettore per l'ora di inizio della sfida.
- `time.fine_powerup`: Selettore per l'ora di fine della sfida.

Puoi aggiungere queste entità a qualsiasi plancia per monitorare la tua strategia durante i PowerUp!

> **💡 Vuoi una grafica dedicata?**
> Scarica anche la Custom Card frontend ufficiale da HACS: [DomHouse Octopus Powerup Card](https://github.com/tuo_username/domhouse-octopus-powerup-card) *(Sostituisci col link della tua futura repo)*.

## ⚠️ Disclaimer
Questo progetto è stato creato da appassionati per la community e **non è un prodotto ufficiale di Octopus Energy**. L'accuratezza dei dati dipende dal database del tuo Home Assistant.
