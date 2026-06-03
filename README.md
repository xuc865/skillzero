<h1 align="center">
Harness-X: Evolving LLM Harness for Pluggable Agentic Control
</h1>

<p align="center">
  <em>A training-free framework that treats LLM harness — strategies, memory, protocols, and guards — as an evolving module library governed at inference time.</em>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-method">Method</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-supported-benchmarks">Benchmarks</a> •
  <a href="#%EF%B8%8F-citation">Citation</a>
</p>

---

## 🔥 Overview

Most LLM agent systems rely on a **static harness** — a fixed prompt preamble containing instructions, few-shot examples, and tool schemas. **HarnessX** replaces this with a **dynamically governed module library** that evolves purely at inference time, requiring **no gradient updates or fine-tuning**.

### Key Ideas

- **Modular harness**: The harness is decomposed into four typed modules — **Strategy** (task-solving plans), **Memory** (experience summaries), **Protocol** (output-format rules), and **Guard** (error-prevention checks).
- **Evolutionary loop**: A four-stage cycle — **Act → Experience → Reflect → Govern** — continuously births, evaluates, and retires modules based on measured utility.
- **Behavioral internalization**: Modules are tested for genuine usefulness via on-policy ablation; those that are internalized by the LLM are gracefully elided to save context budget.
- **Training-free**: Everything happens through in-context learning at test time. HarnessX works with any black-box LLM API (GPT-4o, DeepSeek, Llama, etc.).

---

## 🧩 Method

### The EHG Loop (Evolutionary Harness Governance)

```
┌─────────────────────────────────────────────────────────┐
│                    Per-Epoch Cycle                       │
│                                                         │
│   ① ACT          Agent solves tasks with selected       │
│                   harness modules injected               │
│                            ↓                             │
│   ② EXPERIENCE   Collect rollout trajectories +          │
│                   outcome scores                         │
│                            ↓                             │
│   ③ REFLECT      LLM distills new module candidates     │
│                   from successful / failed rollouts      │
│                            ↓                             │
│   ④ GOVERN       Utility-driven admission + diversity-   │
│                   preserving lifecycle management        │
│                                                         │
│              ← loops back to ① next epoch →             │
└─────────────────────────────────────────────────────────┘
```

### Module Types

| Kind | Color | Purpose | Example |
|------|-------|---------|---------|
| **Strategy** | 🟣 Purple | Task-solving plans and decomposition | "For multi-hop questions, search each entity separately then combine" |
| **Memory** | 🟢 Green | Accumulated experience and patterns | "Wikipedia disambiguation pages rarely contain direct answers" |
| **Protocol** | 🟠 Orange | Output format and interaction rules | "Always output `<search>query</search>` on a single line" |
| **Guard** | 🔴 Red | Error prevention and edge-case checks | "Never repeat the same search query twice in a row" |

### Lifecycle States

Each module transitions through lifecycle states based on its measured utility:

- **Active** — Currently selected and injected into prompts
- **Elided** — Utility dropped below threshold; temporarily removed but recoverable
- **Revived** — Previously elided module brought back when relevant context reappears
- **Archived** — Permanently retired after sustained low utility

### Governor: Utility-Driven Admission

The **HarnessGovernor** manages the library each epoch with two governance principles:

1. **Utility-driven selection**: Online EMA tracking of per-module success rates → elide / revive / decay
2. **Diversity-preserving evolution**: Birth gate → merge → contradiction detection → promote

New modules must pass an **on-policy helpfulness validation**: the governor runs matched tasks with and without the candidate module, admitting only those that demonstrate measurable improvement.

---

## 🏗️ Architecture

```
harness_evolution/
├── harness_library.py        # HarnessModule + HarnessLibrary data structures
├── harness_reflector.py      # Reflect stage: distill modules from rollouts
├── harness_governor.py       # Govern stage: lifecycle + admission control
├── rollout_harness_eval.py   # Main EHG evaluation loop (Act + Experience)
├── analyze_results.py        # Result analysis utilities
└── collect_results_csv.py    # CSV export for experiment tracking

agent_system/
├── environments/             # Environment wrappers (ALFWorld, Search, etc.)
├── memory/                   # Agent memory management
├── multi_turn_rollout/       # Multi-turn interaction engine
└── reward_manager/           # Reward computation and scoring
```

### Core Components

- **`HarnessLibrary`** — The central module store. Supports typed insertion, LLM-based selection, serialization, and lifecycle queries.
- **`HarnessReflector`** — Takes rollout trajectories and asks an LLM to distill reusable modules (strategies from successes, guards from failures, etc.).
- **`HarnessGovernor`** — Runs utility-based governance each epoch: admits promising candidates via ratio-based admission (`admit_ratio`), elides underperformers, merges duplicates, and resolves contradictions.
- **`rollout_harness_eval`** — The main loop that orchestrates Act → Experience → Reflect → Govern across multiple epochs and models.

---

## 📊 Supported Benchmarks

HarnessX has been evaluated across diverse agentic tasks:

### Task A: Open-Domain QA (Search)
- **Datasets**: NQ, HotpotQA, 2WikiMultiHopQA, MuSiQue, Bamboogle, TriviaQA, PopQA
- **Setup**: Agent uses a search API to retrieve information and answer questions
- **Metric**: QA F1 score

### Task B: Hard Search (Complex Reasoning)
- **Datasets**: GAIA, HLE, SimpleQA, WebWalkerQA
- **Setup**: Multi-step web search with reasoning chains
- **Metric**: QA F1 score

### Task C: Long-Context Memory
- **Datasets**: LoCoMo, LongMemEval
- **Setup**: QA over long conversation histories (~14k tokens of evidence)
- **Metric**: QA F1 + LLM-Judge

### Task D: Embodied Planning
- **Datasets**: ALFWorld (6 task types: pick, clean, heat, cool, examine, pick-two)
- **Setup**: Text-based household task completion
- **Metric**: Task success rate

---

## 🛠️ Installation

```bash
# Create environment
conda create -n harnessx python=3.12 -y
conda activate harnessx
pip install -e .

# For ALFWorld experiments
pip install gymnasium==0.29.1 alfworld
alfworld-download -f

# For Search experiments (retriever server)
cd ./agent_system/environments/env_package/search/third_party
pip install -e .
```

---

## 🚀 Quick Start

### Run HarnessX Evolution

```bash
python -m harness_evolution.rollout_harness_eval \
    --tasks data/your_tasks.jsonl \
    --epochs 10 \
    --models gpt-4o \
    --samples-per-epoch 200 \
    --out-dir outputs/my_experiment
```

### Task JSONL Format

Each line in the task file should be a JSON object with:

```json
{
  "task_id": "unique_id",
  "question": "What is the capital of France?",
  "gold_answer": "Paris",
  "evidence": "optional context..."
}
```

### Evaluate with Frozen Library

After evolution, evaluate on test sets with a frozen (non-evolving) library:

```bash
python -m harness_evolution.rollout_harness_eval \
    --tasks data/test_tasks.jsonl \
    --epochs 1 \
    --models gpt-4o \
    --load-library outputs/my_experiment/library_final.json \
    --frozen \
    --out-dir outputs/frozen_eval
```

---

## ⭐️ Citation

If you find this project useful, please cite our work:

```bibtex
@article{harnessx2026,
    title={HarnessX: Evolving LLM Harness Modules as a Dynamically Governed Library},
    year={2026}
}
```

---

## 🤝 Acknowledgement

This project builds upon [verl-agent](https://github.com/langfengQ/verl-agent), [veRL](https://github.com/volcengine/verl), [ALFWorld](https://github.com/alfworld/alfworld), [Search-R1](https://github.com/PeterGriffinJin/Search-R1), and [ARPO](https://github.com/AlibabaResearch/ARPO). We thank the authors of those projects.