---
name: "🧭 MASTER SKILLS ROUTER (v7.0-WAVE1 FOUNDATION)"
tags: ["antigravity", "api", "atomized", "backend", "routing", "skills", "orchestration", "infrastructure"]
tier: 4
risk: "high"
applies_to_agents: ["cursor", "claude", "copilot", "cline", "continue", "kiro", "roo"]
industry: ["web", "product"]
---
# 🧭 MASTER SKILLS ROUTER (v7.0-WAVE1 FOUNDATION)

> **PURPOSE:** Central routing engine orchestrating and accessing modular capability files.
> **MANDATE:** AI MUST read this file BEFORE executing any non-trivial tasks (Rule 1).
> **UPDATE:** 2026-06-17 (v7.0-WAVE1 - COMPLIANCE FIX)

---

## 📋 RETRIEVAL STRATEGY / CHIẾN LƯỢC TRUY XUẤT

1. **Step 1: Identify Category & Master Inventory**
   - Match the active domain (Frontend, Backend, Security, Workflows, Specialized, Marketing, AI-Agents, Data, DevOps, AI-ML, Mobile, Web3, IoT).
   - Load the target `master-inventory.md` file from that category.

2. **Step 2: Narrow Down Query (Search-First)**
   - Use `grep_search` to pull the precise skill block or examine the index.
   - For high-complexity tasks (Tier 3/4), load: **`specialized/cognitive-behavior-framework.md`**.

---

## 🏗️ TIER SYSTEM / MA TRẬN PHÂN TẦNG

| Tier | Meaning | Scope | Load Mechanism |
|------|---------|---------|-------------|
| **TIER 1** | Snippet/Refactor | CRUD, Type fixes, Typo, Read | Skip `MASTER_ROUTER.md`. |
| **TIER 2** | Mandatory | New Feature, Bugfix, Security, SEO | Load `MASTER_ROUTER.md` + Target Inventory. |
| **TIER 3** | Advanced | Scalability, Architecture, Multi-agent | Full Chain + `cognitive-behavior-framework.md`. |
| **TIER 4** | Expert | Deep Tech, Firmware, Quant, OS | Full Chain + `gemini-extended-rules.md`. |

---

## 🚨 EXECUTION RULES

- **Path Verification Rule:** Before referencing any file path, verify its existence using directory scan or `view_file` verification. If the file is not found, log it as MISSING and skip instead of guessing content.
- **Strict Evidence Hierarchy:** Rely on active runtime diagnostics and tests over documentation or inferences.

---

## 🗂️ CAPABILITY MAPPING / BẢN ĐỒ SIÊU HỆ THỐNG

### 1. FRONTEND & UI (Atomized)
- **Inventory File:** `frontend/frontend-master-inventory.md`
- **Core Capabilites:** 3d-web-experience, ab-test-setup, cro-skills, tailwind-patterns, react-patterns.
- **Tags:** `[React, NextJS, CSS, UI/UX, State, Animation, Flutter, Mobile]`

### 2. BACKEND & API (Atomized)
- **Inventory File:** `backend/backend-master-inventory.md`
- **Core Capabilites:** nestjs-expert, prisma-expert, algolia-search, api-documentation-generator.
- **Tags:** `[Nodejs, Python, API, DB, Auth, Schema, Serverless, Edge]`

### 3. SECURITY & AUDITING (Atomized)
- **Inventory File:** `security/security-master-inventory.md`
- **Core Capabilites:** api-security-best-practices, burp-suite-testing, sql-injection-testing, red-team-tactics.
- **Tags:** `[XSS, SQLi, IDOR, Pentest, Red-Team, Audit, OWASP]`

### 4. WORKFLOWS & AUTOMATION (Atomized)
- **Inventory File:** `workflows/workflows-master-inventory.md`
- **Core Capabilites:** analyze-codebase, refactor-code, debug-errors, documentation-templates.
- **Tags:** `[Debug, Testing, Git, Planning, Automation, Documentation]`

### 5. SPECIALIZED & COGNITIVE
- **Inventory File:** `specialized/specialized-master-inventory.md`
- **Core Cognitive File:** `specialized/cognitive-behavior-framework.md` (Mandatory for Tier 3/4)
- **Tags:** `[Reasoning, Analysis, Writing, Synthesis, Problem-Solving]`

### 6. MARKETING & GROWTH
- **Inventory File:** `specialized/marketing-master-inventory.md`
- **Core Capabilites:** programmatic-seo, social-content, email-sequence, launch-strategy.
- **Tags:** `[Marketing, SEO, Social, Email, Growth, Campaigns, Ads]`

### 7. AI AGENTS & ORCHESTRATION
- **Inventory File:** `ai-agents/ai-agents-master-inventory.md`
- **Core Capabilites:** orchestrate-workflows, autonomous-agents-design, llm-coordination.
- **Tags:** `[Agents, Orchestration, LangGraph, CrewAI, AutoGen, Multi-Agent]`

### 8. DATA ENGINEERING & ANALYTICS
- **Inventory File:** `data-engineering/data-engineering-master-inventory.md`
- **Core Capabilites:** clickhouse-io, data-transformation, segment-cdp, data-quality-frameworks.
- **Tags:** `[Data, ETL, ELT, SQL, Spark, Pandas, Analytics, CDO]`

### 9. DEVOPS & INFRASTRUCTURE
- **Inventory File:** `devops/devops-master-inventory.md`
- **Core Capabilites:** cicd-pipelines, containerization, observability, terraform-skill, kubernetes-architect.
- **Tags:** `[DevOps, CI/CD, IaC, Docker, Kubernetes, Terraform, Observability, SRE]`

### 10. AI/ML & DATA SCIENCE
- **Inventory File:** `ai-ml/ai-ml-master-inventory.md`
- **Core Capabilites:** pytorch-transformers, model-evaluation, data-science-core, vector-database-tuning.
- **Tags:** `[AI, ML, PyTorch, HuggingFace, Scikit-Learn, MLOps, VectorDB, Pandas]`

### 11. MOBILE DEVELOPMENT
- **Inventory File:** `mobile/mobile-master-inventory.md`
- **Core Capabilites:** swiftui-expert, ios-lifecycle, jetpack-compose, flutter-deep, react-native-pro.
- **Tags:** `[Mobile, iOS, Android, Swift, Kotlin, Flutter, ReactNative]`

### 12. WEB3 & FINTECH
- **Inventory File:** `web3-fintech/web3-fintech-master-inventory.md`
- **Core Capabilites:** smart-contract-audit, defi-protocols, financial-ledgers, zero-knowledge-proofs.
- **Tags:** `[Web3, DeFi, Solidity, SmartContract, Fintech, Cryptography, Ledgers, ZKP]`

### 13. IOT & EMBEDDED SYSTEMS
- **Inventory File:** `iot-hardware/iot-hardware-master-inventory.md`
- **Core Capabilites:** firmware-development, hardware-interfaces, iot-networking, iot-security.
- **Tags:** `[IoT, Hardware, Embedded, C, ESP32, STM32, BLE, MQTT, Firmware]`

---

## ❓ CLARIFICATION-FIRST PROTOCOL (MANDATORY)

When a request has multiple plausible interpretations or missing constraints, routing MUST load:
- `specialized/ask-questions-if-underspecified/SKILL.md`

Execution policy:
1. Ask 1-5 must-have questions before implementation.
2. Do not edit files or run irreversible commands before clarification.
3. If user replies `defaults`, proceed using recommended defaults and state assumptions.

---

## 🚨 SYSTEM OPTIMIZATION RULES

1. **Read-as-Needed:** Avoid loading full inventories. Utilize `grep_search` to retrieve targeted capability blocks.
2. **Context Pruning:** Discard transient files/logs once the task is marked completed to prevent token drift.
3. **Always Load Workflows First on Error:** In case of failure, prioritize loading the relevant debug workflow.

---

**Version:** 7.0-WAVE1 (Foundation Compliance)  
**Last Updated:** 2026-06-17  
**Maintained by:** Antigravity System

### 14. HERMES AGENT SKILLS (Imported)
- **Inventory File:** `hermes-collection/hermes-master-inventory.md`
- **Tags:** `[Hermes, Subagent, Delegation, Research, Autonomous, Cron, Sandboxes]`
