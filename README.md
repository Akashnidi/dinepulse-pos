# DinePulse POS 🍽️⚡

> **An ultra-lightweight, 100% offline-first takeaway restaurant billing & token generation POS for Windows (<40MB RAM).**

---

## ⚡ Core Philosophy & Architecture
- **Ultra-Low Memory Footprint (<40MB RAM):** Zero Electron, zero Node.js build pipelines, zero heavy databases. Optimized for 4GB RAM Windows IoT / budget POS terminals.
- **100% Offline-First:** Zero external dependencies or CDN links. All assets served locally.
- **Sub-5ms Execution:** Client-side in-memory calculations, backed by SQLite in Write-Ahead Logging (`WAL`) mode with `synchronous=FULL` for power-loss data protection.
- **Dual KOT & Thermal Print:** Browser-driven 80mm/58mm thermal printing for Customer Receipts & Kitchen Order Tickets (KOT) simultaneously.

---

## 🛠️ Tech Stack
- **Backend:** Python 3.13 (managed via Astral `uv`), FastAPI, Pydantic, Uvicorn
- **Database:** SQLite 3 (native WAL mode + auto-migration)
- **Frontend:** Single-page Vanilla HTML5 / CSS3 / Vanilla JS (no bundlers, no frameworks)
- **Deployment Target:** Microsoft Edge Kiosk Mode (`--app`), PyInstaller standalone executable, Inno Setup installer

---

## 🚀 Getting Started (Development Mode)

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)

### Run Locally
```powershell
# 1. Clone repository
git clone https://github.com/Akashnidi/dinepulse-pos.git
cd dinepulse-pos

# 2. Run with uv
uv run python main.py
```
Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

To launch in borderless Windows Kiosk mode:
```cmd
msedge --app=http://127.0.0.1:8000 --start-fullscreen
```

---

## 🚧 Roadmap & Milestones
- [x] **Stage 1 (Current):** Core POS Billing, Menu Management, Daily Token Counter, Dual Print, Dashboard
- [ ] **Stage 2:** Pre-Packaging Verification & Stress Testing
- [ ] **Stage 3:** Standalone PyInstaller Executable + Inno Setup Windows Installer Wizard
- [ ] **Stage 4:** Clean OS Acceptance Testing on Windows Server
