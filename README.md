<h1 align="center">
HarnessX: Evolving LLM Harness for Pluggable Agentic Control 
</h1>

<p align="center">
  <em>A unified framework that treats LLM harness — strategies, memory, protocols, and guards — as an evolving module library, supporting both <strong>training-free</strong> (API-based) and <strong>training-based</strong> (RL + harness co-evolution) paradigms.</em>
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-method">Method</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-training-based-ehg">Training-Based EHG</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-supported-benchmarks">Benchmarks</a> •
  <a href="#%EF%B8%8F-citation">Citation</a>
</p>

---

## 🔥 Overview

Most LLM agent systems rely on a **static harness** — a fixed prompt preamble containing instructions, few-shot examples, and tool schemas. **HarnessX** replaces this with a **dynamically governed module library** that evolves over time, combining the flexibility of inference-time harness evolution with the power of gradient-based reinforcement learning.

### Two Paradigms, One Framework

| Paradigm | Backbone | Harness Evolution | Use Case |
|----------|----------|-------------------|----------|
| **Training-Free EHG** | Any LLM API (GPT-4o, DeepSeek, etc.) | Pure in-context learning at inference time | Rapid prototyping, black-box models |
| **Training-Based EHG** | Local models (Qwen2.5-7B/3B) | RL (GRPO/GiGPO) + outer-loop harness co-evolution | Maximum performance, end-to-end optimization |

### Key Ideas

- **Modular harness**: The harness is decomposed into four typed modules — **Strategy** (task-solving plans), **Memory** (experience summaries), **Protocol** (output-format rules), and **Guard** (error-prevention checks).
- **Evolutionary loop**: A four-stage cycle — **Act → Experience → Reflect → Govern** — continuously births, evaluates, and retires modules based on measured utility.
- **Agent self-selection**: In training-based mode, the agent autonomously decides which harness modules to apply via `<apply_harness>` tags — the model learns *when* to use *which* harness through RL.
- **Dual-layer optimization**: Inner loop (RL) updates model parameters via gradient descent; outer loop (EHG) evolves the harness library through reflection and governance.
- **On-policy helpfulness validation**: New modules must demonstrate measurable improvement through with/without ablation before admission.

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

| Kind | Icon | Purpose | Example |
|------|------|---------|---------|
| **Strategy** | 🟣 | Task-solving plans and decomposition | "For multi-hop questions, search each entity separately then combine" |
| **Memory** | 🟢 | Accumulated experience and patterns | "Wikipedia disambiguation pages rarely contain direct answers" |
| **Protocol** | 🟠 | Output format and interaction rules | "Always output `<search>query</search>` on a single line" |
| **Guard** | 🔴 | Error prevention and edge-case checks | "Never repeat the same search query twice in a row" |

### Lifecycle States

Each module transitions through lifecycle states based on its measured utility:

```
                    birth gate
  Candidate ─────────────────→ Active
                                 │
                    utility < θ  │  utility > θ (revive)
                                 ↓
                              Elided ←──────────────────
                                 │
                    freshness    │
                    decay < α    │
                                 ↓
                             Archived (permanent retirement)
```

- **Active** — Currently selected and injected into prompts
- **Elided** — Utility dropped below threshold; temporarily removed but recoverable
- **Revived** — Previously elided module brought back when relevant context reappears
- **Archived** — Permanently retired after sustained low utility

### Governor: Utility-Driven Admission

The **HarnessGovernor** manages the library each epoch with two governance principles:

1. **Utility-driven selection**: Online EMA tracking of per-module success rates → elide / revive / decay
2. **Diversity-preserving evolution**: Birth gate → merge → contradiction detection → promote / demote

**Birth gate** is a two-phase process:
- **Phase 1**: Verify all candidates via on-policy helpfulness (with/without ablation)
- **Phase 2**: Rank by measured improvement, admit top `admit_ratio` fraction (capped at `max_admits_per_epoch`)

---

## 🧬 Training-Based EHG

The training-based paradigm co-evolves model parameters and harness modules simultaneously.

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  Harness Evolution Layer                      │
│                                                              │
│  Each RL epoch:                                              │
│  ┌──────────┐      ┌──────────┐      ┌───────────────────┐  │
│  │ Reflector │ ───→ │ Governor │ ───→ │  Harness Library  │  │
│  │ (from     │      │ (verify, │      │  (strategy,guard, │  │
│  │  failures)│      │  prune)  │      │   memory,protocol)│  │
│  └────▲─────┘      └──────────┘      └────────┬──────────┘  │
│       │                                        │             │
│       │ rollout results                        │ inject into │
│       │ (success/fail)                         │ prompt as   │
│       │                                        │ skill_ctx   │
│  ┌────┴────────────────────────────────────────▼──────────┐  │
│  │              RL Training Loop (GRPO / GiGPO)           │  │
│  │                                                        │  │
│  │  ┌────────┐  ┌────────┐  ┌───────────┐  ┌──────────┐  │  │
│  │  │Rollout │→ │ Reward │→ │ Advantage │→ │ Gradient │  │  │
│  │  │(agent  │  │ (F1,EM)│  │ (GRPO/    │  │ Update   │  │  │
│  │  │ + env) │  │        │  │  GiGPO)   │  │          │  │  │
│  │  └────────┘  └────────┘  └───────────┘  └──────────┘  │  │
│  │                                                        │  │
│  │             Qwen2.5-7B / 3B (local, offline)           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### How It Works

1. **Prompt injection**: All active harness modules are summarized and injected into the agent's system prompt as a "harness catalogue":

   ```
   ## Available Harness Modules
   Below are reasoning strategies you can optionally apply.
   To use one, output <apply_harness>MODULE_ID</apply_harness> before your reasoning.

   - **verify_multi_hop_chain** (id=`a3f2b1c8`, type=strategy):
     For multi-hop questions, verify each step of the reasoning chain...
   - **avoid_premature_answer** (id=`d7e9f0a1`, type=guard):
     Do not output <answer> until you have searched at least twice...
   ```

2. **Agent self-selection**: During rollout, the agent decides whether and which harness to apply by outputting `<apply_harness>MODULE_ID</apply_harness>`. The environment detects this tag and returns the full harness module text as part of the next observation.

3. **RL optimization**: The agent's choices (including harness usage) are optimized through standard RL reward signals (QA F1, success rate). Over training, the model **learns to invoke harness modules when beneficial**.

4. **Epoch-end evolution**: After each RL epoch, the harness library evolves:
   - **Reflect**: An external LLM (e.g., DeepSeek-V3) analyzes failed rollouts to propose new candidate modules
   - **Govern**: Candidates are validated, merged with duplicates, and admitted to the library
   - **Next epoch**: The updated library is used for the next round of rollouts

### Configuration

Training-based EHG is controlled via the `harness_evolution` config section:

```yaml
harness_evolution:
  enable: True                    # Toggle harness evolution
  start_library: null             # Path to a pre-trained library (optional)
  api_key: "sk-..."              # API key for the reflection LLM
  base_url: "https://..."        # API base URL
  reflect_model: "deepseek-v3.2" # LLM used for reflection
  max_admits_per_epoch: 6         # Max new modules admitted per epoch
  admit_ratio: 0.9                # Fraction of candidates to consider
  validation_budget: 3            # Ablation runs per candidate
  save_dir: null                  # Auto-set if null
```

### Supported RL Algorithms

| Algorithm | Description | Config |
|-----------|-------------|--------|
| **GRPO** | Group Relative Policy Optimization — advantage normalized within groups | `algorithm.adv_estimator=grpo` |
| **GiGPO** | Group-in-Group Policy Optimization — step-level advantage with discounted returns | `algorithm.adv_estimator=gigpo` |

Both algorithms work with the multi-turn search environment where multiple responses per prompt are generated and compared.

---

## 🏗️ Architecture

### Repository Structure

```
skillzero/
├── harness_evolution/                # Evolutionary Harness Governance
│   ├── harness_library.py            #   HarnessModule + HarnessLibrary data structures
│   ├── harness_reflector.py          #   Reflect: distill modules from rollout trajectories
│   ├── harness_governor.py           #   Govern: lifecycle management + admission control
│   ├── harness_integration.py        #   RL ↔ Harness bridge (SkillAdapter, ActionParser, Callback)
│   ├── rollout_harness_eval.py       #   Training-free EHG loop (Act + Experience)
│   ├── analyze_results.py            #   Result analysis utilities
│   └── collect_results_csv.py        #   CSV export for experiment tracking
│
├── agent_system/                     # Agent Environment System
│   ├── environments/                 #   Environment wrappers
│   │   ├── env_manager.py            #     SearchEnvironmentManager (harness-aware)
│   │   ├── prompts/search.py         #     Prompt templates with {skill_context} slot
│   │   ├── base.py                   #     EnvironmentManagerBase
│   │   └── env_package/              #     Environment implementations
│   │       ├── search/               #       Web search QA environment
│   │       ├── alfworld/             #       ALFWorld household tasks
│   │       ├── gym_cards/            #       Card game environments
│   │       ├── sokoban/              #       Sokoban puzzle environment
│   │       └── webshop/              #       Web shopping environment
│   ├── memory/                       #   Agent memory (history) management
│   ├── multi_turn_rollout/           #   Multi-turn interaction engine
│   │   ├── rollout_loop.py           #     TrajectoryCollector for RL rollouts
│   │   └── utils.py                  #     Data processing utilities
│   └── reward_manager/               #   Reward computation and scoring
│       ├── episode.py                #     EpisodeRewardManager
│       └── episode_with_compression.py  # Compression-aware reward
│
├── verl/                             # Reinforcement Learning Infrastructure
│   ├── trainer/
│   │   ├── ppo/
│   │   │   ├── ray_trainer.py        #     RayPPOTrainer (harness evolution integrated)
│   │   │   ├── core_algos.py         #     PPO/GRPO advantage computation
│   │   │   ├── reward.py             #     Reward function loading
│   │   │   └── metric_utils.py       #     Training metrics
│   │   ├── main_ppo.py               #     Standard PPO entry point
│   │   └── config/
│   │       └── ppo_trainer.yaml      #     Base trainer config
│   ├── workers/                      #   Distributed workers (FSDP, Megatron)
│   ├── single_controller/            #   Ray-based single controller
│   └── utils/                        #   Utilities (tokenizer, dataset, etc.)
│
├── gigpo/                            # GiGPO Algorithm
│   └── core_gigpo.py                 #   Step-level advantage computation
│
├── recipe/                           # Training Recipes
│   ├── ehg_grpo/                     #   EHG + GRPO/GiGPO training
│   │   ├── main_ehg_grpo.py          #     Entry point
│   │   └── config/
│   │       └── ehg_grpo_trainer.yaml #     Config with harness_evolution section
│   ├── dapo/                         #   DAPO recipe
│   ├── prime/                        #   PRIME recipe
│   ├── r1/                           #   R1 recipe
│   ├── spin/                         #   SPIN recipe
│   └── sppo/                         #   SPPO recipe
│
├── scripts/                          # Launch Scripts
│   ├── run_ehg_grpo_7b.sh            #   EHG + GRPO on Qwen2.5-7B
│   ├── run_ehg_grpo_3b.sh            #   EHG + GRPO on Qwen2.5-3B
│   ├── run_ehg_gigpo_7b.sh           #   EHG + GiGPO on Qwen2.5-7B
│   ├── train_search_text.sh          #   Vanilla GRPO text-only search
│   ├── train_search_skillzero_7b.sh  #   SkillZero VL 7B search
│   └── ...                           #   Other training scripts
│
├── skills/                           # Skill Files (curriculum learning)
├── data/                             # Training/evaluation data
└── outputs/                          # Experiment outputs
```

### Core Components

#### Harness Evolution

- **`HarnessLibrary`** — The central module store. Supports typed insertion, LLM-based or rule-based selection, JSON serialization, and lifecycle state queries. Each module carries online utility statistics (EMA success rate, selection count, freshness).

- **`HarnessReflector`** — Takes rollout trajectories (both successes and failures) and asks an external LLM to distill reusable modules. Strategies are extracted from successes, guards from failures, and memory from recurring patterns.

- **`HarnessGovernor`** — Runs utility-based governance each epoch: admits promising candidates via a two-phase birth gate, elides underperformers, merges near-duplicates via text similarity, detects contradictions, and promotes strategies that generalize across task types to protocols.

- **`HarnessEvolutionCallback`** *(new)* — Orchestrates one round of reflect → govern at the end of each RL epoch, bridging the verl training loop with the harness evolution system.

- **`HarnessSkillAdapter`** *(new)* — Converts the `HarnessLibrary` into a prompt-injectable skill context string listing all active modules with IDs and summaries.

- **`HarnessActionParser`** *(new)* — Detects `<apply_harness>MODULE_ID</apply_harness>` tags in agent output, resolves them to full module text, and tracks usage statistics.

#### Agent System

- **`SearchEnvironmentManager`** — Manages the search QA environment. Now harness-aware: injects harness module catalogues into prompts via `_get_skill_context()`, parses harness invocations in `step()`, and returns harness guidance as part of observations.

- **`TrajectoryCollector`** — Collects multi-turn agent-environment interaction trajectories for RL training. Supports vanilla and dynamic (DAPO-style) sampling.

- **`EpisodeRewardManager`** — Computes per-episode rewards based on QA F1 / exact match scores.

#### RL Training

- **`RayPPOTrainer`** — The core RL trainer with Ray-based distribution. Now includes `_init_harness_evolution()` for setup and `_run_harness_evolution()` triggered at each epoch boundary. Supports GRPO, GiGPO, PPO, REINFORCE++, RLOO, and REMAX advantage estimators.

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

### Prerequisites

- Python 3.12+
- CUDA 12.1+ (for GPU training)
- 4× A100 80GB (recommended for 7B model training)

### Setup

```bash
# Create environment
conda create -n harnessx python=3.12 -y
conda activate harnessx
pip install -e .

# Install vLLM and SGLang for rollout acceleration
bash scripts/install_vllm_sglang_mcore.sh

# For ALFWorld experiments
pip install gymnasium==0.29.1 alfworld
alfworld-download -f

# For Search experiments (retriever server)
cd ./agent_system/environments/env_package/search/third_party
pip install -e .
```

### Models (Offline Loading)

Models are loaded offline from local paths. Download and place them at:

```
/mnt/workspace/wxc/Agent/models/
├── Qwen2.5-7B-Instruct/     # For 7B experiments
├── Qwen2.5-3B-Instruct/     # For 3B experiments
└── ...
```

---

## 🚀 Quick Start

### 1. Training-Based EHG (Recommended)

**Start the search retrieval server** (required for search environments):

```bash
# In a separate terminal
cd agent_system/environments/env_package/search/third_party
python -m skyrl_gym.tools.search --port 8000
```

**Run EHG + GRPO on Qwen2.5-7B:**

```bash
bash scripts/run_ehg_grpo_7b.sh
```

**Run EHG + GiGPO on Qwen2.5-7B:**

```bash
bash scripts/run_ehg_gigpo_7b.sh
```

**Run EHG + GRPO on Qwen2.5-3B:**

```bash
bash scripts/run_ehg_grpo_3b.sh
```

**Run vanilla GRPO baseline (no harness evolution):**

```bash
EHG_ENABLE=False bash scripts/run_ehg_grpo_7b.sh
```

#### Key Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EHG_ENABLE` | `True` | Enable/disable harness evolution |
| `EHG_API_KEY` | — | API key for the reflection LLM |
| `EHG_BASE_URL` | — | API base URL for the reflection LLM |
| `EHG_REFLECT_MODEL` | `deepseek-v3.2` | Model used for reflection |
| `EHG_MAX_ADMITS` | `6` | Max new modules admitted per epoch |
| `EHG_START_LIBRARY` | `null` | Path to a pre-trained library to continue from |
| `ADV_ESTIMATOR` | `grpo` | RL algorithm (`grpo` or `gigpo`) |
| `MODEL_PATH` | Qwen2.5-7B path | Path to the backbone model |
| `SEARCH_URL` | `http://127.0.0.1:8000/retrieve` | Search retrieval server URL |
| `TOTAL_TRAINING_STEPS` | `180` | Total RL training steps |

### 2. Training-Free EHG

For rapid prototyping with API-based LLMs:

```bash
python -m harness_evolution.rollout_harness_eval \
    --tasks data/your_tasks.jsonl \
    --epochs 10 \
    --models deepseek-v3.2 \
    --samples-per-epoch 200 \
    --max-admits 6 \
    --admit-ratio 0.9 \
    --validation-budget 3 \
    --out-dir outputs/my_experiment
```

### 3. Evaluate with Frozen Library

After evolution (either training-free or training-based), evaluate on test sets with a frozen library:

```bash
python -m harness_evolution.rollout_harness_eval \
    --tasks data/test_tasks.jsonl \
    --epochs 1 \
    --models deepseek-v3.2 \
    --frozen-library outputs/my_experiment/library_final.json \
    --out-dir outputs/frozen_eval
```

### Task Data Format

Each line in the task JSONL file should be a JSON object:

```json
{
  "task_id": "unique_id",
  "question": "What is the capital of France?",
  "gold_answer": "Paris",
  "evidence": "optional context...",
  "task_type": "single_hop",
  "domain": "geography"
}
```

For RL training, data should be in Parquet format with a `prompt` column.

---

## 🔬 Advanced Usage

### Continuing Training from a Pre-trained Library

You can bootstrap RL training with a library evolved through the training-free pipeline:

```bash
EHG_START_LIBRARY=outputs/pretrained/library_final.json \
    bash scripts/run_ehg_grpo_7b.sh
```

### Custom Reflection Model

The reflection LLM can be any model accessible via an OpenAI-compatible API:

```bash
EHG_REFLECT_MODEL=gpt-4o \
EHG_API_KEY=sk-your-key \
EHG_BASE_URL=https://api.openai.com/v1 \
    bash scripts/run_ehg_grpo_7b.sh
```

### Monitoring with Weights & Biases

Training metrics (including harness evolution stats) are logged to W&B by default:

| Metric | Description |
|--------|-------------|
| `harness/candidates_from_reflect` | New candidate modules from reflection |
| `harness/active_modules` | Currently active modules in library |
| `harness/total_modules` | Total modules (all lifecycle states) |
| `training/global_step` | RL training step |
| `training/epoch` | Current epoch |

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

This project builds upon [verl-agent (GiGPO)](https://github.com/langfengQ/verl-agent), [veRL](https://github.com/volcengine/verl), [ALFWorld](https://github.com/alfworld/alfworld), [Search-R1](https://github.com/PeterGriffinJin/Search-R1), and [ARPO](https://github.com/AlibabaResearch/ARPO). We thank the authors of those projects.

---

## 📜 License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.