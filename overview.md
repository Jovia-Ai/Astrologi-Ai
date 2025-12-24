Project Overview (High-Level Documentation)
* Purpose: A holistic astrology platform that computes natal and synastry charts, translates rule-engine outputs into the poetic “Jovia language,” and layers AI for premium interpretations.
* MVP → v1 → Growth roadmap: MVP handles natal chart calc, rule-driven interpretations, and a deterministic “Jovia” builder. v1 adds synastry/transits, weighted narratives, and flow linking. Growth roadmap (v2+) expands AI prompts, celebrity similarity, life timeline, Aura/Story cards, conversational AI, and deeper multi-language output.
* User flow: Chart request → auth validation → chart engine (Swiss Ephemeris) → rule engine (category/tagged outputs) → builder (weighted + flow for free, PRO AI for premium) → API response. Add parallel synastry/transit paths.
* Backend role: Glue between frontend and astrophysics/AI: exposes FastAPI endpoints, orchestrates calculations (astro, rules, builder, AI proxies), enforces auth, caches, logs, and monitors deployments.
* Core components:
    * Astrology Engine: Swiss Ephemeris-based planetary positions, houses, angles; handles timezone→UTC, Julian Day, multiple house systems (Placidus).
    * Rule Engine: Loads JSON rules (sign/house/aspect/meta), evaluates matches, yields tagged output (cause/mechanism/effect/shadow/potential) per category.
    * AI Layer: Premium Groq/LLama/Supabase-assisted builder that rewrites fragments, with prompt engineering and caching/fallback strategy.
    * Database: MongoDB/Supabase store for users, charts, interpretations, synastry data, AI caches; indexes for fast lookup.
    * Auth Layer: JWT-based signup/login, profile, scope enforcement, rate limiting.
    * API Gateway: FastAPI routing, versioning, documentation, CORS/security headers.
    * Ephemeris System: Maintains Swiss Ephemeris files (archived in repo), accessible to astrology engine for precise calculations.
Jovia Astrology-AI Backend Overview
Project Purpose & Vision
The Jovia Astrology-AI backend exists to transform raw celestial data into emotionally resonant, astrology-informed narratives. It combines deterministic astrology computation, a rules-driven “Jovia language system,” and modular AI layers so that natal, synastry, and transit charts can be delivered with human-quality storytelling. The broader vision is a platform where every chart query results in a beautifully structured interpretation, where premium users can unlock advanced AI prose while free users receive deterministic but elegant flow.
Core Features
* Natal chart calculation using Swiss Ephemeris + timezone management.
* Ships in synastry & transit data for relational and temporal insights.
* Rule Engine that tags outputs into cause/mechanism/effect/shadow/potential.
* Builder pipeline (weighted + flow + PRO) creating connected paragraphs per category.
* AI integration (Groq, LLaMA, fallback) for premium interpretive layers.
* Auth & persistence in MongoDB/Supabase, with JWT + request logging.
* Ephemeris management for accurate planetary/house data across releases.
High-Level Architecture
           +--------------------+
           |    API Gateway     |
           |  (FastAPI endpoints)|
           +---------+----------+
                     |
       +-------------+--------------+
       |     Backend Services       |
       |  - Astrology Engine         |
       |  - Rule Engine              |
       |  - Builder (Flow + Weighted |
       |    + PRO)                   |
       |  - AI Layer Dispatcher      |
       |  - Auth / DB                |
       +-------------+--------------+
                     |
    +----------------+---------------+
    |   Persistence & External APIs  |
    | - MongoDB / Supabase            |
    | - Swiss Ephemeris files + ephe  |
    | - Groq / LLaVA / Llama runtimes |
    +---------------------------------+
Key Backend Modules
Astrology Engine
* Responsible for planetary placements, houses, angles from Swiss Ephemeris.
* Converts local birth information → UTC → Julian Day → planetary coordinates.
* Supports Placidus house system and other optional systems via chart_engine.
Rule Engine
* Loads structured rule JSON (planet/sign/house/aspect/meta).
* Matches conditions and emits tagged output per category (cause/mechanism/effect/shadow/potential).
* Maintains the interpretation map so builders and AI layers can reference the exact sentences used.
AI Layer
* Wraps premium narrative generation (Groq, local LLaMA) via jovia_narrative_builder.py.
* Includes prompt engineering, caching, harmful-output filters, and fallback strategy (Groq → OpenAI → localhost LLaMA).
* Works alongside deterministic builders to keep premium/free separation clean.
Builder/Interpretation Layer
* JoviaWeightedNarrativeBuilder selects best sentences per slot with planet weights.
* JoviaNarrativeFlowEngine connects those sentences into flowing paragraphs.
* JoviaSemanticNarrativeBuilder (PRO) rewrites fragments for premium stories.
Database & Auth Layer
* MongoDB/Supabase store users, charts, interpretations, synastry data, AI caches, request logs.
* JWT-based auth + middleware guard ensures secure API access.
* Profiles, stories, and synastry models live beside rule output storage.
API Gateway & Ephemeris
* FastAPI exposes endpoints for chart calculation, interpretation, transits, dataset inspection, AI-driven interpretation, and debugging.
* Ephemeris files (Swiss ephemeris) are packaged or downloaded via scripts, referenced by the astrology engine.
Data Flow Summary
1. Request intake (birth data or synastry/transit payload) via FastAPI.
2. Validation & auth ensures user permissions.
3. Astrology Engine calculates houses/planets/angles based on ephemeris/timezone.
4. Rule Engine evaluates structured rule set, producing tagged interpretation fragments.
5. Builder pipeline (Weighted → Flow → AI) converts fragments into paragraphs.
6. Response assembles metadata, planets, aspects, interpretations, combined insights, and narrative_interpretation.
Supported Chart Types
Chart Type	Description
Natal	Individual birth chart with planets, houses, aspects, narrative.
Synastry	Composite/relationship chart combining two natal charts plus interpretation layer.
Transit	Temporal overlays of current planets against natal positions for forecasting.
Interpretation Engine Overview (Jovia Language System)
* Maintains 5-slot grammar (cause/mechanism/effect/shadow/potential) per category (identity/psychology/relationships/mind/career/karma).
* The rule engine tags each sentence accordingly, preserving planetary metadata.
* Weighted builder prioritizes planets per category (Sun/Asc etc.) to pick the most resonant lines.
* Flow engine glues cause→mechanism→shadow→potential with connectors, delivering “Jovia flow” regardless of slot availability.
* Premium builder (JoviaSemanticNarrativeBuilder) rewrites fragments into poetic, AI-level prose using semantic scoring and prefix normalization.
AI Integration Overview
* Free mode uses deterministic builder pipeline (weighted + flow) for consistent narratives.
* Premium mode routes to JoviaSemanticNarrativeBuilder, which rewrites fragments from rule engine via Groq/LLaMA:
    * Prompt engineering enforces cause/mechanism/effect/shadow/potential order.
    * Caching stores generated text to avoid repeat costs.
    * Fallback strategy uses multiple models in order (Groq → OpenAI → local LLaMA) for resilience.
    * Rate limiting and filters guard harmful output, while logging ensures traceability.
Roadmap Summary
Phase	Focus
MVP	Natal chart calc + deterministic builder + rule engine + FastAPI endpoints + auth/logging.
v1	Synastry/transits, weighted narrative builder, flow connectors, ROI on premium AI, improved API docs.
Growth	AI conversation, celebrity similarity, life timeline, story/aura cards, background tasks (CRON/Celery), enhanced monitoring, multi-language support.
