# 🚀 Quickstart - Ads Quality Rater

**In 3 Schritten zur laufenden App!**

## ⚡ Schnellstart mit `./start.sh`

### 1️⃣ Environment-Variablen konfigurieren

```bash
# .env Datei erstellen
cp .env.example .env
```

Öffne `.env` und füge deinen Gemini API Key ein:

```bash
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

> **API Key erhalten:** https://makersuite.google.com/app/apikey

### 2️⃣ Alles starten

```bash
# Script ausführbar machen (einmalig)
chmod +x start.sh

# Backend + Frontend starten
./start.sh
```

### 3️⃣ Fertig! 🎉

Die App läuft jetzt auf:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📋 Was macht `./start.sh`?

Das Script erledigt automatisch:

1. ✅ **Prüft `.env` Datei**
   - Warnt, falls `GEMINI_API_KEY` fehlt

2. 📦 **Installiert Backend-Dependencies**
   - Erstellt Python Virtual Environment (`backend/venv`)
   - Installiert alle Python-Packages aus `requirements.txt`

3. 📦 **Installiert Frontend-Dependencies**
   - Installiert alle npm-Packages aus `package.json`

4. 🚀 **Startet Backend-Server**
   - Läuft auf Port 8000
   - Auto-Reload aktiviert (Änderungen werden automatisch neu geladen)

5. 🚀 **Startet Frontend-Server**
   - Läuft auf Port 3000
   - Next.js mit Turbopack (ultra-schnell)

6. 🛑 **Stoppt beide Server mit `Ctrl+C`**
   - Sauberes Herunterfahren beider Prozesse

---

## 🎯 App verwenden

### In der Web-UI

1. Öffne http://localhost:3000
2. Fülle das Formular aus:
   - **Ad-URL** oder **Ad-Bild hochladen**
   - **Landingpage-URL**
   - Optional: Zielgruppe, Kampagnenziel, Brand Guidelines
3. Klicke **"Analyse starten"**
4. Sieh zu, wie die KI-Agents in Echtzeit arbeiten
5. Erhalte detaillierten Quality-Report

### Via API (Terminal)

```bash
curl -X POST http://localhost:8000/api/v1/analyze/stream \
  -F "ad_url=https://example.com/ad.jpg" \
  -F "landing_page_url=https://example.com/landing-page" \
  -F "target_audience=B2B Decision Makers"
```

---

## 🔧 Troubleshooting

### ❌ Problem: "GEMINI_API_KEY not set"

**Lösung:**
```bash
# Prüfe .env Datei
cat .env | grep GEMINI_API_KEY

# Sollte ausgeben:
# GEMINI_API_KEY=AIza...

# Falls nicht, füge deinen Key in .env ein
```

### ❌ Problem: "Port 8000 already in use"

**Lösung:**
```bash
# Stoppe Prozess auf Port 8000
lsof -ti:8000 | xargs kill -9

# Starte neu
./start.sh
```

### ❌ Problem: "Port 3000 already in use"

**Lösung:**
```bash
# Stoppe Prozess auf Port 3000
lsof -ti:3000 | xargs kill -9

# Starte neu
./start.sh
```

### ❌ Problem: "Playwright browser not found"

**Lösung:**
```bash
cd backend
source venv/bin/activate
playwright install chromium
cd ..
./start.sh
```

### ❌ Problem: "Permission denied: ./start.sh"

**Lösung:**
```bash
# Script ausführbar machen
chmod +x start.sh

# Nochmal versuchen
./start.sh
```

---

## 🔄 Manueller Start (ohne start.sh)

Falls du lieber manuell starten möchtest:

### Backend (Terminal 1)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn src.api.main:app --reload --port 8000
```

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

---

## 🛑 Server stoppen

### Mit start.sh
```bash
# Einfach Ctrl+C im Terminal drücken
# Script stoppt automatisch beide Server
```

### Manuell
```bash
# Alle Prozesse stoppen
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

---

## 💡 Tipps

- **Erste Analyse:** Nutze die Beispiel-URLs aus der UI
- **Brand Guidelines:** Schau dir `backend/config/brand_guidelines/example_brand.json` an
- **API erkunden:** Öffne http://localhost:8000/docs (Swagger UI)
- **Logs ansehen:** Das Terminal zeigt alle Agent-Aktivitäten in Echtzeit

---

## 📚 Weitere Infos

- **Vollständige Doku:** [README.md](README.md)
- **Architektur:** Siehe "Multi-Agent-System" in README.md
- **API Referenz:** http://localhost:8000/docs

---

**Das wars! Viel Spaß beim Analysieren deiner Ads! 🎯**

*Bei Fragen: team@flin.com*
