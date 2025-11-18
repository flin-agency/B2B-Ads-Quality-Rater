# 🎯 Ads Quality Rater

KI-basierter Quality Rater mit Crew AI + Gemini 2.0 Flash für automatisierte Bewertung von Ad-LP-Kohärenz und Markenkonformität.

## 📋 Übersicht

Dieses System analysiert automatisiert die Qualität und Konsistenz von Werbeanzeigen und deren Landingpages:

- **Visuelle Analyse** von Ads (Gemini 2.0 Flash Vision)
- **Landingpage-Scraping** (Playwright für dynamische Seiten)
- **Copywriting-Bewertung** (Message Match, Tonalität)
- **Brand-Compliance-Prüfung** gegen Guidelines
- **Streaming-Interface** mit Echtzeit-Updates

## 🚀 Quick Start

### Voraussetzungen

- Python 3.11+
- Node.js 18+
- Gemini API Key ([hier erstellen](https://makersuite.google.com/app/apikey))

### Installation & Start

```bash
# 1. Repository klonen
git clone https://github.com/your-org/ads-quality-rater.git
cd ads-quality-rater

# 2. Environment-Variablen konfigurieren
cp .env.example .env
# Öffne .env und füge deinen Gemini API Key ein:
# GEMINI_API_KEY=your-actual-api-key-here

# 3. Alles starten (Backend + Frontend)
chmod +x start.sh
./start.sh
```

Das wars! Die App läuft jetzt auf:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Was macht start.sh?

1. ✅ Prüft `.env` und `GEMINI_API_KEY`
2. 📦 Installiert Backend-Dependencies (Python venv)
3. 📦 Installiert Frontend-Dependencies (npm)
4. 🚀 Startet Backend (Port 8000)
5. 🚀 Startet Frontend (Port 3000)
6. 🛑 Stoppt beide Server mit `Ctrl+C`

## 🏗️ Architektur

### Multi-Agent-System (Crew AI)

Das System verwendet 5 spezialisierte Agents in sequentieller Ausführung:

1. **Ad_Visual_Analyst** → Analysiert Werbemotiv visuell
2. **Landing_Page_Scraper** → Extrahiert LP-Text
3. **Copywriting_Expert** → Bewertet Message Match
4. **Brand_Consistency_Agent** → Prüft Markenkonformität
5. **Quality_Rating_Synthesizer** → Erstellt finalen Markdown-Report

### Tech Stack

**Backend:**
- Framework: Crew AI (Multi-Agenten-Orchestrierung)
- LLM: Gemini 2.0 Flash (Text + Vision)
- API: FastAPI mit Server-Sent Events (SSE)
- Scraping: Playwright + trafilatura
- Validation: Pydantic 2.x

**Frontend:**
- Framework: Next.js 15 (Turbopack)
- Styling: Tailwind CSS
- Markdown: React Markdown
- TypeScript: 5.x

## 💻 Verwendung

### In der UI

1. Öffne http://localhost:3000
2. Gib Ad-URL oder lade Ad-Bild hoch
3. Gib Landingpage-URL ein
4. Optional: Zielgruppe, Kampagnenziel, Brand Guidelines
5. "Analyse starten" klicken
6. Sieh zu, wie die Agents in Echtzeit arbeiten
7. Erhalte detailliertes Markdown-Report

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/analyze/stream \
  -F "ad_url=https://example.com/ad.jpg" \
  -F "landing_page_url=https://example.com/landing" \
  -F "target_audience=Young professionals (25-35)"
```

**Streaming Response:**
```
data: {"type": "log", "data": "🎨 Analysiere Ad-Visual..."}
data: {"type": "log", "data": "🌐 Scrappe Landingpage..."}
data: {"type": "log", "data": "✍️ Bewerte Copywriting..."}
data: {"type": "result", "data": "# Ad Quality Report\n\n..."}
```

## 🎨 Brand Guidelines Format

Brand Guidelines können als JSON-Text eingefügt werden:

```json
{
  "brand_name": "YourBrand",
  "tone_of_voice": ["professional", "friendly", "innovative"],
  "prohibited_words": ["cheap", "free", "scam"],
  "color_palette": {
    "primary": "#FF6B35",
    "secondary": "#004E89",
    "accent": "#F7B32B"
  },
  "visual_style": "minimalist, modern, clean",
  "values": ["transparency", "quality", "sustainability"]
}
```

Beispiel: [backend/config/brand_guidelines/example_brand.json](backend/config/brand_guidelines/example_brand.json)

## 📁 Projektstruktur

```
ads-quality-rater/
├── .env                    # Environment-Variablen (nicht committen!)
├── .env.example            # Template für .env
├── start.sh                # Quickstart-Script
├── backend/
│   ├── src/
│   │   ├── agents/         # 5 Crew AI Agents
│   │   ├── tools/          # Gemini Vision, Playwright, trafilatura
│   │   ├── crew/           # Crew-Orchestrierung
│   │   └── api/            # FastAPI mit SSE
│   ├── requirements.txt
│   └── venv/              # Python Virtual Environment
├── frontend/
│   ├── app/               # Next.js App Router
│   ├── components/        # React Components
│   └── node_modules/      # npm Dependencies
└── README.md              # Dieses Dokument
```

## 🔧 Development

### Manueller Start (ohne start.sh)

**Backend:**
```bash
cd backend
source venv/bin/activate
python3 -m uvicorn src.api.main:app --reload --port 8000
```

**Frontend (neues Terminal):**
```bash
cd frontend
npm run dev
```

### Tests ausführen

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Code-Style

```bash
# Backend
cd backend
black src/ tests/
ruff check src/ tests/

# Frontend
cd frontend
npm run lint
```

## 🐛 Troubleshooting

### GEMINI_API_KEY nicht gesetzt

```bash
# Prüfen ob .env existiert
cat .env | grep GEMINI_API_KEY

# Sollte ausgeben:
# GEMINI_API_KEY=AIza...

# Falls nicht, kopiere .env.example und füge deinen Key ein
cp .env.example .env
```

### Playwright Browser fehlt

```bash
cd backend
source venv/bin/activate
playwright install chromium
```

### Port 8000 oder 3000 bereits belegt

```bash
# Backend-Port frei machen
lsof -ti:8000 | xargs kill -9

# Frontend-Port frei machen
lsof -ti:3000 | xargs kill -9
```

### Module-Import-Fehler

```bash
# Sicherstellen, dass uvicorn als Python-Modul läuft
cd backend
python3 -m uvicorn src.api.main:app --reload
# NICHT: uvicorn src.api.main:app
```

## 📊 Features im Detail

### Streaming-Interface

- Echtzeit-Updates während der Analyse
- Agent-Logs zeigen Fortschritt
- Server-Sent Events (SSE) für Live-Updates

### Markdown-Reports

- Strukturierte, lesbare Reports
- Direkt im UI gerendert
- Enthält Scores, Empfehlungen, Details

### File & URL Support

- Ad-Bilder per Upload oder URL
- Landingpages via URL
- Brand Guidelines als JSON-Text

## 📝 Environment-Variablen

**Minimal (.env):**
```bash
GEMINI_API_KEY=your-gemini-api-key
```

**Erweitert (.env):**
```bash
# Gemini API
GEMINI_API_KEY=your-gemini-api-key
MODEL=gemini-2.0-flash-exp

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO

# Frontend (für Production)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Support

- **Issues:** [GitHub Issues](https://github.com/your-org/ads-quality-rater/issues)
- **API Docs:** http://localhost:8000/docs (wenn Server läuft)
- **Contact:** team@flin.com

## 📄 License

MIT

---

**Status:** ✅ Vollständig implementiert und einsatzbereit
**Powered by:** Gemini 2.0 Flash & Crew AI
**© 2025 flin. All rights reserved.**
