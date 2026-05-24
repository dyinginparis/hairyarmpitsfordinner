# Windows-Service-Betrieb

Diese Anleitung beschreibt, wie der Python-Server dauerhaft als Windows-Dienst laeuft und wie Browser oder Desktop-App nur noch als Client verwendet werden.

## Zielbild

Im lokalen Desktop-Modus startet Electron den Python-Server selbst. Das ist bequem fuer Tests, aber nicht ideal fuer 24/7-Betrieb.

Fuer Dauerbetrieb sollte die Trennung so aussehen:

```text
Windows-Dienst
  -> startet den Python-Server dauerhaft auf 127.0.0.1:5050
  -> nutzt .env und data/smart_wallets.sqlite3
  -> wird von Windows automatisch gestartet und neu gestartet

Client
  -> Browser: http://127.0.0.1:5050
  -> oder Desktop-App als UI
  -> beendet den Dienst nicht beim Schliessen des Fensters
```

Wichtig: Wenn der Dienst bereits auf `127.0.0.1:5050` laeuft, verbindet sich die Desktop-App mit diesem Server. Sie startet dann keinen eigenen Python-Prozess. Wird die Desktop-App geschlossen, bleibt der Dienst weiter aktiv.

## Voraussetzungen

Diese Anleitung geht von diesem Projektpfad aus:

```text
C:\Projects\Jayanam\hairyarmpitsfordinner
```

Wenn das Projekt spaeter dauerhaft laufen soll, ist ein stabiler Pfad besser, zum Beispiel:

```text
C:\Apps\PredictionMarketBot
```

Der Pfad sollte nicht in einem temporaeren Download-Ordner liegen.

## Installation Auf Einem Anderen Rechner

Auf einem neuen Rechner sollte die Installation in dieser Reihenfolge erfolgen:

1. Repository in einen stabilen Ordner auschecken, zum Beispiel:

```powershell
cd C:\Apps
git clone <REPOSITORY_URL> PredictionMarketBot
cd C:\Apps\PredictionMarketBot
```

2. Python und Node.js muessen installiert sein.

Pruefen:

```powershell
python --version
node --version
npm.cmd --version
```

3. WinSW herunterladen.

Die WinSW-x64-EXE in den Projektordner legen. Der Installer akzeptiert eine dieser Varianten:

```text
PredictionMarketBotService.exe
WinSW-x64.exe
winsw.exe
```

Wenn die Datei `WinSW-x64.exe` oder `winsw.exe` heisst, kopiert der Installer sie automatisch nach `PredictionMarketBotService.exe`.

4. `Install Windows Service.bat` als Administrator ausfuehren.

Der Installer erledigt dann:

- erstellt `.venv`, falls nicht vorhanden
- installiert Python-Abhaengigkeiten aus `requirements.txt`
- installiert `waitress`
- erstellt `.env` aus `.env.example`, falls `.env` noch fehlt
- erstellt `data` und `logs`
- installiert Node-Abhaengigkeiten, falls `node_modules` fehlt
- schreibt `PredictionMarketBotService.xml` ueber `scripts/windows-service/write-service-xml.ps1`
- installiert den Windows-Dienst `PredictionMarketBot`
- setzt den Dienst auf automatischen Start
- startet den Dienst

5. Healthcheck pruefen:

```powershell
Invoke-RestMethod http://127.0.0.1:5050/api/health
```

6. Browser oeffnen:

```text
http://127.0.0.1:5050
```

7. `.env` konfigurieren.

Fuer Paper Trading reichen die Defaults. Fuer Live Trading muessen Account/Funder/API-Credentials/Private Key lokal in `.env` gesetzt werden. Nach Aenderungen an `.env` den Dienst neu starten.

```powershell
.\Restart Windows Service.bat
```

Die `.env` wird nicht committet und muss auf jedem Rechner lokal gepflegt werden.

## Batch-Dateien Fuer Den Dienst

Diese Batch-Dateien liegen im Projekt-Root:

```text
Install Windows Service.bat
Start Windows Service.bat
Stop Windows Service.bat
Restart Windows Service.bat
Status Windows Service.bat
Uninstall Windows Service.bat
```

Die Install-, Start-, Stop-, Restart- und Uninstall-Dateien muessen als Administrator ausgefuehrt werden, weil sie Windows-Dienste verwalten.

`Status Windows Service.bat` zeigt:

- Windows-Service-Status
- ob Port `5050` belegt ist
- Healthcheck-Antwort von `/api/health`

Die Batch-Dateien loeschen keine Daten. `.env`, `data`, `logs` und die SQLite-Datenbank bleiben auch beim Uninstall erhalten.

## Einmaliges Server-Setup

Im Projektordner:

```powershell
cd C:\Projects\Jayanam\hairyarmpitsfordinner

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt waitress

if (!(Test-Path .env)) {
  Copy-Item .env.example .env
}
```

Danach `.env` lokal konfigurieren. Fuer Paper Trading reichen die Defaults. Fuer Live Trading muessen Polymarket-Adresse, Funder, Signature Type, API Credentials und Private Key gesetzt sein.

## Server Manuell Testen

Vor dem Dienst zuerst manuell testen:

```powershell
cd C:\Projects\Jayanam\hairyarmpitsfordinner
.\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:5050 src.web_app:app
```

In einem zweiten PowerShell-Fenster pruefen:

```powershell
Invoke-RestMethod http://127.0.0.1:5050/api/health
```

Wenn JSON zurueckkommt, laeuft der Server.

Stoppen im ersten Fenster:

```text
CTRL+C
```

## Dienst Mit WinSW

Empfohlener Weg: WinSW. Das ist ein kleiner Wrapper, der ein normales Programm als Windows-Service laufen laesst.

1. WinSW x64 herunterladen.
2. Die EXE in den Projektordner kopieren.
3. Die EXE umbenennen in:

```text
PredictionMarketBotService.exe
```

4. Daneben diese Datei anlegen:

```text
PredictionMarketBotService.xml
```

Inhalt:

```xml
<service>
  <id>PredictionMarketBot</id>
  <name>Prediction Market Bot Server</name>
  <description>Runs the Prediction Market Bot backend server.</description>

  <workingdirectory>C:\Projects\Jayanam\hairyarmpitsfordinner</workingdirectory>
  <executable>C:\Projects\Jayanam\hairyarmpitsfordinner\.venv\Scripts\waitress-serve.exe</executable>
  <arguments>--listen=127.0.0.1:5050 src.web_app:app</arguments>

  <env name="PYTHONUNBUFFERED" value="1" />

  <logpath>C:\Projects\Jayanam\hairyarmpitsfordinner\logs</logpath>
  <log mode="roll-by-size">
    <sizeThreshold>10485760</sizeThreshold>
    <keepFiles>5</keepFiles>
  </log>

  <onfailure action="restart" delay="5 sec" />
  <onfailure action="restart" delay="30 sec" />
</service>
```

Der Wert `workingdirectory` ist wichtig, weil die App die `.env` aus dem aktuellen Arbeitsverzeichnis laedt und die SQLite-Datenbank standardmaessig relativ unter `data/smart_wallets.sqlite3` liegt.

## Dienst Installieren

Einfacher Weg:

```text
Install Windows Service.bat
```

Diese Datei als Administrator ausfuehren. Sie erledigt Setup, XML-Erzeugung, Service-Installation und Start.

Manueller Weg:

PowerShell als Administrator oeffnen:

```powershell
cd C:\Projects\Jayanam\hairyarmpitsfordinner
.\PredictionMarketBotService.exe install
```

Danach starten:

```powershell
.\PredictionMarketBotService.exe start
```

Status pruefen:

```powershell
.\PredictionMarketBotService.exe status
```

Healthcheck:

```powershell
Invoke-RestMethod http://127.0.0.1:5050/api/health
```

## Dienst Verwalten

Mit WinSW:

```powershell
.\PredictionMarketBotService.exe start
.\PredictionMarketBotService.exe stop
.\PredictionMarketBotService.exe restart
.\PredictionMarketBotService.exe status
.\PredictionMarketBotService.exe uninstall
```

Mit Windows-Bordmitteln:

```powershell
Get-Service PredictionMarketBot
Start-Service PredictionMarketBot
Stop-Service PredictionMarketBot
Restart-Service PredictionMarketBot
```

Oder:

```cmd
sc query PredictionMarketBot
net start PredictionMarketBot
net stop PredictionMarketBot
```

Logs liegen bei der obigen Konfiguration hier:

```text
C:\Projects\Jayanam\hairyarmpitsfordinner\logs
```

## Client Nutzen

Wenn der Dienst laeuft, gibt es zwei Client-Optionen.

Browser:

```text
http://127.0.0.1:5050
```

Desktop-App:

```powershell
.\Start Desktop App.bat
```

Die Desktop-App prueft beim Start `http://127.0.0.1:5050/api/health`. Wenn der Dienst bereits antwortet, nutzt sie diesen Server. Wird das Desktop-Fenster geschlossen, bleibt der Dienst aktiv.

Wenn der Dienst nicht laeuft, startet die Desktop-App weiterhin ihren eigenen lokalen Server. Dieser wird beim Schliessen der Desktop-App beendet. Fuer echten 24/7-Betrieb also immer zuerst den Dienst starten oder den Dienst auf automatischen Start setzen.

## Automatischer Start

Nach der Installation kann der Dienst ueber die Windows-Diensteverwaltung auf automatischen Start gestellt werden:

```powershell
Set-Service -Name PredictionMarketBot -StartupType Automatic
```

Pruefen:

```powershell
Get-Service PredictionMarketBot
```

## Update-Ablauf

Sauberer Ablauf fuer Code-Updates:

```powershell
cd C:\Projects\Jayanam\hairyarmpitsfordinner

Stop-Service PredictionMarketBot
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt waitress
Start-Service PredictionMarketBot
Invoke-RestMethod http://127.0.0.1:5050/api/health
```

Wenn `.env` geaendert wurde, muss der Dienst neu gestartet werden:

```powershell
Restart-Service PredictionMarketBot
```

## Daten Und Backups

Die lokalen Bot-Daten liegen standardmaessig hier:

```text
data\smart_wallets.sqlite3
```

Diese Datei enthaelt unter anderem:

- Watchlist
- Alerts
- Paper-Trading-Daten
- Live-Order-Logs
- Live-Positionsdaten des Bots
- Account-Snapshots

Ein einfaches Backup:

```powershell
Stop-Service PredictionMarketBot
Copy-Item data\smart_wallets.sqlite3 backups\smart_wallets-$(Get-Date -Format yyyyMMdd-HHmmss).sqlite3
Start-Service PredictionMarketBot
```

Vorher den Backup-Ordner anlegen:

```powershell
New-Item -ItemType Directory -Force backups
```

## Was Passiert Bei Einem Server-Ausfall?

Echte Orders und echte Positionen existieren bei Polymarket, nicht nur lokal. Die lokale SQLite-Datenbank speichert aber den Bot-Zustand und die Order-/Positionshistorie.

Wenn der Server aus ist:

- es werden keine neuen Wallet-Trades beobachtet
- es werden keine neuen Copytrades erstellt
- Paper Trading laeuft nicht weiter
- Live-Reconciliation und Account-Snapshots laufen nicht
- Alerts werden nicht aktualisiert

Bereits bei Polymarket platzierte Orders oder Positionen verschwinden dadurch nicht. Der Bot reagiert aber nicht, solange der Dienst nicht laeuft. Deshalb ist ein Windows-Dienst mit automatischem Neustart fuer 24/7-Betrieb erforderlich.

## Refactoring Fuer Dauerbetrieb

Der empfohlene Betriebsmodus bleibt ein einzelner Windows-Dienst:

```text
PredictionMarketBot Dienst
  -> waitress
  -> src.web_app:app
  -> bindet lokal auf 127.0.0.1:5050
```

Es soll also kein zweiter Windows-Dienst eingefuehrt werden. Trotzdem sollte die Anwendung intern sauberer getrennt werden, damit dieser eine Dienst stabiler und besser wartbar laeuft.

### Server Als Dauerprozess

Der Server sollte als dauerhafter Backend-Prozess verstanden werden. Browser und Desktop-App sind nur Clients.

Die Desktop-App sollte im Dienstbetrieb nicht der Besitzer des Servers sein. Sie darf sich mit dem laufenden Dienst verbinden, aber das Schliessen der Desktop-App darf den Bot nicht stoppen.

Sinnvolle Zielregel:

```text
Wenn 127.0.0.1:5050 erreichbar ist:
  Desktop-App nutzt den vorhandenen Dienst.

Wenn 127.0.0.1:5050 nicht erreichbar ist:
  Desktop-App kann fuer Entwicklung optional einen lokalen Server starten.
```

Fuer produktiven Betrieb sollte klar dokumentiert werden: Erst Dienst starten, dann Browser oder Desktop-App oeffnen.

### Background-Logik Aus Web-Routen Herausziehen

Aktuell enthaelt `src/web_app.py` Routen, Hilfsfunktionen und Background-Monitoring in einer Datei. Fuer Dauerbetrieb sollte die Logik intern aufgeteilt werden, auch wenn alles im selben Waitress-Dienst laeuft.

Zielstruktur:

```text
src/web_app.py
  -> Flask-App, Registrierung der Routen, statische UI

src/background.py
  -> Watchlist-Monitor
  -> Paper-Reconciliation
  -> Live-Reconciliation
  -> Account-Snapshots

src/services/
  -> wiederverwendbare Businesslogik
  -> keine Flask-request-Abhaengigkeit

src/routes/
  -> schlanke API-Endpunkte
  -> ruft Services auf
```

Der Background-Monitor kann weiterhin beim Start der Flask-App gestartet werden, aber er sollte als eigene Komponente gekapselt sein:

- eigener Start/Stop-Mechanismus
- Stop-Event statt endloser `while True`-Schleife ohne Shutdown-Signal
- sauberer Fehlerstatus
- konfigurierbares Intervall
- keine doppelten Monitor-Starts

### Polling Und Server Calls Reduzieren

Die UI ruft mehrere Endpunkte regelmaessig ab. Besonders Live-Ansichten koennen externe Polymarket-Calls und Datenbank-Snapshots ausloesen. Fuer Dauerbetrieb ist besser:

- UI liest bevorzugt gespeicherte Daten aus SQLite.
- Externe API-Reconciliation passiert im Background-Monitor.
- UI-Refresh loest moeglichst keine teuren externen API-Calls aus.
- Polling nur fuer den gerade aktiven Tab.
- Live-Refresh eher alle 15-30 Sekunden statt alle 5 Sekunden.
- Account-Snapshots nicht bei jedem UI-Request speichern, sondern zeitgesteuert im Background-Monitor.

Damit wird der Dienst stabiler und die App trifft weniger haeufig externe Rate Limits.

### Endpunkte Schlanker Machen

API-Endpunkte sollten moeglichst kurz bleiben:

```text
Request lesen
Parameter validieren
Service-Methode aufrufen
JSON zurueckgeben
```

Nicht ideal ist, wenn ein einzelner UI-Request gleichzeitig:

- mehrere externe Polymarket-APIs abfragt
- Live-Reconciliation ausfuehrt
- Account-Snapshots schreibt
- Positionen markiert
- und grosse UI-Datenpakete baut

Diese Arbeit sollte in Services und Background-Jobs verschoben werden. Die Route gibt dann nur den zuletzt bekannten Zustand zurueck.

### Konfiguration Erweitern

Fuer Dauerbetrieb sollten weitere Werte in `.env` konfigurierbar sein:

```env
APP_HOST=127.0.0.1
APP_PORT=5050
WATCHLIST_MONITOR_INTERVAL_SECONDS=30
LIVE_REFRESH_INTERVAL_SECONDS=30
ENABLE_BACKGROUND_MONITOR=1
```

Der Waitress-Dienst wuerde weiterhin explizit auf `127.0.0.1:5050` binden. Die App selbst koennte diese Werte fuer Statusanzeigen, Client-URLs und Background-Intervalle verwenden.

### SQLite Weiterhin Nutzen, Aber Kontrolliert

SQLite ist fuer einen lokalen Single-User-Bot ausreichend, solange nur ein Backend-Prozess aktiv ist.

Wichtig:

- nur ein Waitress-Dienst fuer denselben Datenbankpfad
- keine mehrfachen Server-Instanzen auf dieselbe SQLite-Datei
- regelmaessige Backups
- keine langen Schreibtransaktionen
- Background-Monitor und UI-Schreibzugriffe weiterhin mit Locks schuetzen

Die bestehende WAL-Konfiguration ist fuer parallele Lesezugriffe hilfreich.

### Logging Und Healthcheck

Fuer den Dienstbetrieb gibt es einen dedizierten Healthcheck:

```text
GET /api/health
```

Der Healthcheck antwortet schnell und ohne externe API-Calls, zum Beispiel:

```json
{
  "ok": true,
  "database": "ok",
  "backgroundMonitor": {
    "running": true,
    "intervalSeconds": 30
  }
}
```

Logs sollten klar unterscheiden:

- Server-Start/Stop
- Background-Monitor-Lauf
- externe API-Fehler
- Live-Trading-Entscheidungen
- Order-Versuche
- Risk-Rejections

### Reihenfolge Der Optimierungen

Pragmatische Reihenfolge:

1. Waitress-Dienst einrichten und stabil lokal auf `127.0.0.1:5050` betreiben.
2. Desktop-App nur noch als Client verwenden, wenn der Dienst laeuft.
3. Background-Monitor aus `web_app.py` in eine eigene Komponente verschieben.
4. UI-Polling reduzieren und nur fuer aktive Tabs ausfuehren.
5. Live-/Account-Endpunkte so umbauen, dass sie gespeicherten Zustand lesen und keine teuren Reconciliations pro Request starten.
6. bessere Logs ergaenzen.
7. Backup- und Update-Prozess standardisieren.

## Sicherheit

Der Server sollte lokal gebunden bleiben:

```text
127.0.0.1:5050
```

Nicht ohne Authentifizierung auf `0.0.0.0` oder ins Netzwerk freigeben. Die App hat lokale Verwaltungsendpunkte und kann Live-Trading ausloesen, wenn Credentials konfiguriert und Live aktiviert sind.

Die Datei `.env` enthaelt Secrets. Sie darf nicht committet werden und ist bereits in `.gitignore` eingetragen.

Optional die Zugriffsrechte auf `.env` einschraenken:

```powershell
icacls .env /inheritance:r
icacls .env /grant:r "$env:USERNAME:(R,W)"
```

Wenn der Dienst unter einem anderen Windows-Benutzer laeuft, muss dieser Benutzer zusaetzlich Zugriff auf `.env`, `data` und `logs` erhalten.

## Alternative: Aufgabenplanung

Die Windows-Aufgabenplanung kann den Server beim Systemstart starten. Das ist einfacher, aber weniger sauber als ein echter Service.

Beispiel:

```powershell
schtasks /Create /TN "PredictionMarketBot" /SC ONSTART /RL HIGHEST /TR "C:\Projects\Jayanam\hairyarmpitsfordinner\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:5050 src.web_app:app" /F
```

Manuell starten:

```powershell
schtasks /Run /TN "PredictionMarketBot"
```

Beenden:

```powershell
schtasks /End /TN "PredictionMarketBot"
```

Fuer laengerfristigen Betrieb ist WinSW oder ein vergleichbarer Service-Wrapper vorzuziehen.
