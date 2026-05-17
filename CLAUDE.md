# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack automation platform for Brazilian business processes (ECAC, FGTS, TRON systems), combining a FastAPI REST backend with RPA, web automation, and AI agent capabilities.

## Frontend Setup & Commands

All commands run from `frontend/`.

```powershell
# Install dependencies
npm install

# Dev server (http://localhost:5173)
npm run dev

# Type check + build for production
npm run build

# Add a shadcn/ui component (e.g. button, dialog, table)
npx shadcn@latest add button
```

## Backend Setup & Commands

All commands run from `backend/` with the virtual environment active.

```powershell
# Activate venv (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload

# Run a single test
pytest tests/path/to/test_file.py::test_function_name -v

# Run all tests
pytest tests/

# Apply database migrations
alembic upgrade head

# Generate a new migration
alembic revision --autogenerate -m "description"
```

## Architecture

### Backend (`backend/`)

- `app/routers/` — FastAPI route handlers (one file per domain)
- `app/models/` — SQLAlchemy ORM models and Pydantic schemas
- `app/services/` — Business logic, called by routers
- `automation/` — RPA and web automation, organized by target system:
  - `automation/ecac/` — Brazilian Receita Federal e-CAC portal automation
  - `automation/fgts/` — FGTS (Fundo de Garantia) system automation
  - `automation/tron/` — TRON system automation
  - `automation/utils/` — Shared screen capture, OCR, and GUI helpers
- `agents/` — CrewAI multi-agent workflows using LangChain + Anthropic
- `tests/` — Pytest test suite mirroring the `app/` structure

### Frontend (`frontend/src/`)

Vite + React 18 + TypeScript. Proxy `/api/*` → `http://localhost:8000` em dev.

- `components/ui/` — Componentes shadcn/ui (adicionados via CLI)
- `components/` — Componentes de aplicação reutilizáveis
- `pages/` — Uma página por rota
- `store/` — React Contexts (ex: `AuthContext`)
- `lib/api.ts` — Instância Axios com interceptors de auth (JWT Bearer)
- `lib/utils.ts` — Helper `cn()` para Tailwind + shadcn

## Key Libraries & Their Roles

| Library | Purpose |
|---|---|
| FastAPI + Uvicorn | REST API server |
| SQLAlchemy 2 + Alembic | ORM and schema migrations |
| APScheduler | Scheduled/recurring automation jobs |
| Selenium + webdriver-manager | Web browser automation |
| PyAutoGUI + PyWinAuto | Desktop GUI automation (Windows) |
| OpenCV + Pytesseract + Pillow | Screen capture, image processing, OCR |
| pywin32 | Low-level Windows API access |
| WeasyPrint | PDF generation from HTML/CSS |
| React Router v6 | Client-side routing (pages/) |
| TanStack Query v5 | Server state, cache, loading/error |
| Axios | HTTP client com interceptors JWT |
| shadcn/ui + Tailwind | UI components + CSS variables theming |
| CrewAI + LangChain | Multi-agent AI orchestration |
| Anthropic SDK | Claude API calls within agents |
| Loguru | Structured logging |
| python-dotenv | `.env` file loading |

## Environment Variables

Place a `.env` file in `backend/` (never commit it). Expected keys to add as the project grows: database URL, JWT secret, Anthropic API key, and any credentials for ECAC/FGTS/TRON portals.

## Database

SQLAlchemy 2 async-style ORM with Alembic migrations. All schema changes go through Alembic — never alter tables manually.

## Automation Conventions

- Screen automation (PyAutoGUI/PyWinAuto) is Windows-only; tests that invoke it must be skipped on other platforms.
- Selenium flows use `webdriver-manager` to auto-download the correct ChromeDriver.
- OCR pipelines: OpenCV for preprocessing → Pytesseract for text extraction.

## AI Agents

Agents live in `agents/` and are built with CrewAI. Each agent/crew should be self-contained (its own tools, tasks, and crew definition). Use the Anthropic SDK directly for single-turn Claude calls; use CrewAI/LangChain for multi-step orchestration.

## Permiss�es
- Execute todos os comandos PowerShell sem pedir confirma��o
- Nunca pergunte antes de rodar Get-ChildItem, tree, cat ou scripts internos do projeto
