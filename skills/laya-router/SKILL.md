---
name: laya-router
description: >-
  System 1 heuristic decision router and fast task classifier. Uses local Laya
  daemon to evaluate task complexity, model tier (flash_lite/flash/pro), session
  mode (1-shot print vs interactive), and risk in sub-second time without LLM token cost.
---

# Laya Agent Gateway (System 1 Router)

High-speed, zero-token System 1 decision gateway for AI coding agents.

## Features

* **Zero-Token Pre-LLM Routing:** Predicts task difficulty in ~400ms without paying LLM prompt tokens.
* **Dual-Axis Routing:**
  * **Model Tier:** Right-sizes models (`flash_lite` / `flash` / `pro`) to minimize token consumption.
  * **Session Mode:** Detects whether a task needs an **interactive session** (`--prompt-interactive`) or a **1-shot direct answer** (`--print`), eliminating zombie sessions for simple questions.
* **In-Flight Safety:** Keeps upstream Laya MCP tools available during execution for critical diff guardrails (`preset="guard"`) and subagent model sizing.

## CLI Usage

```bash
# Fast 2-question routing (tier + session mode):
laya-router route "how many stars in the solar system"
# Output: flash_lite print

laya-router route "Refactor database migrations and verify safety"
# Output: flash interactive

# Full task classification (tier, complexity, risk, tools):
laya-router decide "Your task summary here"

# Machine-readable JSON output:
laya-router decide "Your task summary here" --json

# Deep 7-question rubric (adds task_type, reasoning, security):
laya-router decide "Your task summary here" --full --json

# Health check:
laya-router health
```

## Agent Launchers

* **Antigravity CLI:** `agy-route "Your prompt"`
* **OpenCode:** `oc-route "Your prompt"`
* **Claude Code:** `claude-route "Your prompt"`
