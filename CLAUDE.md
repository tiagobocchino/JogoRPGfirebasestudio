# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**Crônicas do Discord** is an automated tabletop RPG system integrated with Discord. It uses AI (Gemini Flash) to act as a Game Master (GM), managing narration, rules, and NPC interactions.

**Technology Stack:**
- **Backend:** Python + Discord.py
- **Database:** Supabase (PostgreSQL)
- **AI:** Google Gemini Flash API
- **Rules Engine:** D20 Lite (Custom medieval system)

## Directory Structure

- `agents/`: AI persona definitions (Orchestrator, GameMaster).
- `skills/`: Technical and rule-based knowledge (RPG Rules).
- `src/`: Source code for the bot and database schemas.
- `docs/`: Documentation, NPC rosters, and planning.

## Development Commands

### Environment Setup
- Python 3.10+ required.
- Install dependencies: `pip install discord.py supabase google-generativeai python-dotenv`

### Bot Execution
- Run bot: `python src/bot.py`
- (Ensure `DISCORD_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, and `GEMINI_API_KEY` are in `.env`)

## Core Logic & Rules

### RPG System: D20 Lite
- **Attributes:** FOR, DES, CON, INT, SAB, CAR.
- **Rolls:** `1d20 + modifier` vs DC (Difficulty Class).
- **Criticals:** 1 (Fumble), 20 (Critical Success).

### Game Master (IA)
- System Prompt: `src/gm_system_prompt.md`
- Persona: Epic, mysterious, and fair.
- NPCs: 10 pre-defined companions in `docs/npcs_roster.md`.

## Workflow for New Features

1.  **Orchestration:** Consult `agents/RPG-Orchestrator.md` for architectural decisions.
2.  **Mecanics:** Update `skills/RPG-Rules-D20Lite.md` if changing the game engine.
3.  **Bot:** Implement commands or event handlers in `src/bot.py`.
4.  **Database:** Update `src/supabase-schema.sql` if adding character attributes or session states.

---
*Created on 2026-05-03 - Part of the ServidorDiscord ecosystem.*
