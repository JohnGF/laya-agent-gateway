# ⚡ Laya Agent Gateway

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#)

High-speed, zero-token System 1 decision gateway for AI coding agents (Antigravity CLI, OpenCode, Claude Code, Codex).

---

## Overview

Modern AI coding agents face a major architectural bottleneck: **the session and cost penalty**.

When a user submits a prompt, typical workflows launch a heavy frontier LLM and spawn an interactive agent session immediately. For trivial lookups (such as *"how many stars in the solar system"* or simple syntax checks), this wastes token budgets, incurs unnecessary latency, and pollutes conversation histories with zombie sessions.

**Laya Agent Gateway** solves this by inserting a local **System 1 decision layer** in front of your coding agents. Running on top of a local Laya inference daemon, it evaluates user prompts in ~400ms on CPU with zero LLM token costs across two critical dimensions:

1. **Model Tier Axis:** Dynamically selects `flash_lite` (e.g. Gemini 3.8 Flash Low / local Qwen), `flash` (standard coding), or `pro` (deep architecture) to optimize token costs.
2. **Session Mode Axis:** Detects whether a prompt requires an **interactive session** (`--prompt-interactive`) or a **1-shot direct answer** (`--print`), bypassing session initialization entirely when no files need modification.

---

## Comparison: Laya Agent Gateway vs. Existing Alternatives

| Dimension | `laya-router-skill` | **Laya Agent Gateway** |
| :--- | :--- | :--- |
| **Routing Dimensions** | 1D: Task complexity only | **2D: Complexity Tier + Session Mode** (`print` vs `interactive`) |
| **Session Overhead** | Always spawns an interactive agent session | **Zero-session direct terminal answer** for informational Q&A |
| **Runtime Architecture** | Cold CLI process per invocation | **Warm persistent daemon** (`laya.serve` on CPU, 0 MB VRAM) |
| **Forward-Pass Latency** | Variable (often cold model reload) | **~400ms on CPU** (~30ms with CUDA) |
| **Agent Support** | Codex / Claude Code wrappers | **Antigravity (`agy`), OpenCode, Claude Code, Codex** |
| **Lifecycle Integration** | Pre-prompt classification only | **Two-layer synergy:** Pre-LLM gateway + In-flight MCP safety guardrails |

---

## Key Features

* 🚀 **Sub-second Routing:** Evaluates complex intents in ~400ms using a local CPU model, zero latency penalty compared to large remote calls.
* 💸 **Zero Token Cost:** Preserves your expensive frontier model budget for tasks that actually need deep reasoning.
* 🧠 **Dual-Axis Classification:** Right-sizes both the **model tier** and the **session mode** to give you exactly what you need.
* 🔌 **Universal Agent Support:** Drops straight in front of Antigravity CLI, OpenCode, and Claude Code without changing your workflow.
* 🛡️ **In-Flight Safety Guardrails:** Integrates directly with Laya MCP for subagent sizing and dangerous diff verification.

---

## Architecture

```mermaid
flowchart TD
    User([User Prompt]) --> Gateway[Laya Agent Gateway]
    
    subgraph System 1 Decision Layer
        Gateway -- ~400ms Forward Pass --> TierEval{1. Model Tier}
        Gateway --> ModeEval{2. Session Mode}
    end
    
    TierEval -->|Trivial/Facts| Lite[flash_lite]
    TierEval -->|Standard Code| Flash[flash]
    TierEval -->|Complex/Arch| Pro[pro]
    
    ModeEval -->|Q&A| PrintMode[1-Shot Direct Answer]
    ModeEval -->|Task| InteractiveMode[Interactive Session]
    
    Lite -.-> PrintMode
    Lite -.-> InteractiveMode
    Flash -.-> InteractiveMode
    Pro -.-> InteractiveMode
    
    PrintMode --> AgyPrint[agy --model flash-low -p<br/>*(No zombie session created)*]
    InteractiveMode --> AgyInt[agy --model flash -i<br/>*(Full workspace tools)*]
    Pro --> AgyPro[agy --model pro -i<br/>*(Frontier reasoning)*]

    style Gateway fill:#f9f,stroke:#333,stroke-width:2px
    style System 1 Decision Layer fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
```

---

## Project Structure

```
laya-agent-gateway/
├── bin/                 # Executable CLI tools
│   ├── agy-route        # Pre-LLM router for Antigravity CLI
│   ├── claude-route     # Pre-LLM router for Claude Code
│   ├── laya-router      # Core system 1 task dispatcher
│   └── oc-route         # Pre-LLM router for OpenCode
├── skills/              # Agent skill configurations
│   └── laya-router/     # Laya router skill spec
├── systemd/             # Systemd service configurations
│   └── laya.service     # Daemon service file
├── tests/               # Comprehensive test suite
├── install.sh           # Automated installer
└── README.md            # You are here
```

---

## Quickstart

### 1. Prerequisites
Laya Agent Gateway relies on a running local Laya HTTP daemon (`laya.serve`).

To run the daemon on CPU (consuming 0 MB GPU VRAM):
```bash
env LAYA_DEVICE=cpu LAYA_PORT=8791 python -m laya.serve
```

Alternatively, use the provided systemd user service:
```bash
mkdir -p ~/.config/systemd/user
cp systemd/laya.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now laya
```

Verify daemon health:
```bash
curl http://127.0.0.1:8791/health
```

### 2. Installation
Clone the repository and run the installer:
```bash
git clone https://github.com/JohnGF/laya-agent-gateway.git
cd laya-agent-gateway
./install.sh
```

This symlinks the CLI tools into `~/.local/bin/` and registers the agent skill in `~/.agents/skills/`.

---

## Usage

### CLI Commands

#### Fast 2-Question Routing (Tier + Mode)
Evaluates model tier and session mode in ~400ms:
```bash
laya-router route "how many stars in the solar system"
# Output: flash_lite print

laya-router route "Fix typo in line 42 of README.md"
# Output: flash_lite interactive

laya-router route "Refactor database migrations and verify safety"
# Output: flash interactive

laya-router route "Architect a distributed Raft consensus engine"
# Output: pro interactive
```

#### Detailed Task Classification
Provides full rubric evaluation including complexity score, risk assessment, and tool requirements:
```bash
laya-router decide "Refactor database migrations and verify safety" --json
```

Output:
```json
{
  "status": "ok",
  "model_tier": "flash",
  "mode": "interactive",
  "elapsed_ms": 445.2,
  "answers": {
    "model_tier": {
      "type": "choice",
      "choice": "flash",
      "probabilities": { "flash_lite": 0.25, "flash": 0.46, "pro": 0.29 }
    },
    "interaction": {
      "type": "choice",
      "choice": "task"
    },
    "complexity": {
      "type": "score",
      "score": 1.82
    },
    "risk": {
      "type": "choice",
      "choice": "medium"
    },
    "needs_tools": {
      "type": "noul",
      "noul": 0.72
    }
  }
}
```

---

## Pre-LLM Agent Launchers

Instead of launching default heavy configurations, use the smart launchers:

### Antigravity CLI (`agy-route`)
Automatically selects between `gemini-3.8-flash-low`, `gemini-3.8-flash-medium`, and `gemini-3.1-pro-high`, while switching between `--print` and `--prompt-interactive`:
```bash
# Direct 1-shot answer (no session initialized):
agy-route "how many stars in the solar system"

# Interactive workspace session:
agy-route "Refactor auth middleware to support bearer tokens"
```

Manual flag overrides (`-p`, `-i`, `-c`) are always honored.

### OpenCode (`oc-route`)
Routes tasks between local relay (`iaedu/iaedu-relay`), standard model (`opencode/gemini-3.8-flash`), and frontier model (`opencode/gemini-3.1-pro`):
```bash
oc-route "Implement unit test for parser"
```

### Claude Code (`claude-route`)
Routes between Haiku and Sonnet based on task complexity:
```bash
claude-route "Explain how quicksort works"
```

---

## In-Flight MCP Guardrails

Using Laya as an upfront gateway does not preclude in-flight verification. Keep the native Laya MCP server active within your agent environment for mid-turn tasks:
* **Diff Verification:** Run `laya_preset(preset="guard")` before applying critical modifications to security, database, or hardware configuration files.
* **Subagent Sizing:** Evaluate subagent subtask descriptions via `laya_predict` to choose between `flash_lite`, `flash`, and `pro` worker tiers.

---

## License

Apache-2.0.
