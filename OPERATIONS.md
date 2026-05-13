# SkillZero 远程实验与仓库操作指南

本文说明：在远程 Linux + GPU 机器上如何安装依赖、准备数据、启动 ALFWorld 训练，以及如何将本仓库推送到 GitHub。更完整的官方说明见根目录 [README.md](README.md)。

---

## 1. 克隆本仓库

```bash
git clone https://github.com/xuc865/skillzero.git
cd skillzero
```

若使用 SSH：

```bash
git clone git@github.com:xuc865/skillzero.git
cd skillzero
```

---

## 2. Python 环境

建议使用 Conda，Python **3.12**（与仓库 README 一致）：

```bash
conda create -n skillzero python=3.12 -y
conda activate skillzero
```

安装推理与可编辑包（README 最小示例；若与训练脚本锁定的 vLLM 版本不一致，以你实际使用的脚本或 `scripts/install_vllm_sglang_mcore.sh` 为准）：

```bash
pip install vllm==0.10.0
pip install flash-attn==2.7.4.post1 --no-build-isolation --no-cache-dir
pip install -e .
```

 heavier 环境（固定 torch / vLLM / Megatron 等）可参考：

```bash
bash scripts/install_vllm_sglang_mcore.sh
```

---

## 3. ALFWorld 环境

```bash
pip install gymnasium==0.29.1 stable-baselines3==2.6.0 alfworld
alfworld-download -f
```

游戏与检测器等会下载到 **`~/.cache/alfworld/`**。

---

## 4. 训练数据与路径

`scripts/train_alfworld_skillzero_7b.sh` 中默认使用：

- `data.train_files=$HOME/data/verl-agent/visual/train.parquet`
- `data.val_files=$HOME/data/verl-agent/visual/test.parquet`

你需要在远程机器上按仓库内 **`examples/data_preprocess/`** 与 **README** 的说明生成或拷贝对应 **parquet**，并把脚本里的路径改成你的实际目录。

模型路径示例（脚本内）：`actor_rollout_ref.model.path=Qwen/Qwen2.5-VL-7B-Instruct`，请确保机器能访问 Hugging Face 或已提前下载到本地路径并改写该配置。

---

## 5. 可选：Weights & Biases

脚本中常启用 `trainer.logger=['console','wandb']`，需：

```bash
export WANDB_API_KEY=你的密钥
```

若不用 WandB，可在 Hydra 命令里改为 `trainer.logger=['console']`。

---

## 6. 启动训练（ALFWorld 示例）

在仓库根目录：

```bash
conda activate skillzero
cd /path/to/skillzero
bash scripts/train_alfworld_skillzero_7b.sh
```

按需修改脚本中的：**GPU 数量**、**batch 大小**、**数据路径**、**模型路径**。

---

## 7. 可选课程配置：`general_skills` 省略

本 fork 在 **`env.curriculum_learning.skill_internalize`** 下支持：当验证阶段「带全技能 vs 不带技能」的 **各 task 成功率之差的平均值** 持续很小时，从 train/val 的合并 prompt 中 **不再注入 `general_skills` 段落**；任务类技能文件仍只由原有 curriculum（`max_set_schedule`、按 task Δ 选 top‑k）控制，**不增加验证次数**。

Hydra 示例：

```text
env.curriculum_learning.skill_internalize.enable=True
env.curriculum_learning.skill_internalize.graduate_epsilon=0.02
env.curriculum_learning.skill_internalize.graduate_patience=2
env.curriculum_learning.skill_internalize.revive_delta=0.05
env.curriculum_learning.max_set_min_floor=0
```

默认值见 **`verl/trainer/config/ppo_trainer.yaml`** 中 `env.curriculum_learning` 一节。验证日志中会多出 `val/curriculum/internalized_skills`、`val/curriculum/general_skills_omitted` 等字段。

---

## 8. 单元测试（课程逻辑）

```bash
cd /path/to/skillzero
python -m unittest tests.test_curriculum_skill_internalize -v
```

---

## 9. 本地修改后推送到 GitHub

在仓库根目录（已配置 `origin` 指向 `xuc865/skillzero` 时）：

```bash
git add -A
git status   # 确认变更
git commit -m "描述你的修改"
git push origin main
```

首次在本机从空仓库克隆后，若尚未添加远程：

```bash
git remote add origin https://github.com/xuc865/skillzero.git
git branch -M main
git push -u origin main
```

---

## 10. Search 等其它环境

Search 检索服务、索引下载、Retriever 独立 conda 环境与 **README.md** 中「Install Supported Environments」章节一致；跑 Search 训练前需完成对应依赖与 `retrieval_launch.sh` 等步骤。

---

## 参考链接

- 上游 SkillZero 论文与说明：[README.md](README.md) 内 arXiv / 原仓库链接  
- 本仓库 GitHub：<https://github.com/xuc865/skillzero>
