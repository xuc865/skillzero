# HarnessX 主图生成提示词

## 适用工具
GPT Image 2 / ImageGen

---

## 提示词 (English, 详细版)

```
Create a beautiful, polished academic figure (landscape, 16:9 ratio) illustrating the "HarnessX: Evolving LLM Harness Governance" framework. The figure should have a clean white background with a modern, elegant scientific illustration style. Use a cohesive color palette: deep blue #1E3A5F, teal #2DA8A0, warm orange #E8843C, coral red #E05555, light gray #F5F7FA.

The figure is a single unified diagram flowing left-to-right with the governance loop as the central focal point.

【LEFT SIDE — Frozen LLM + Harness Library】
On the far left, draw a tall dark blue rounded rectangle labeled "Frozen LLM" with a small lock icon on its top-right corner, indicating no weight updates. Below the LLM block, draw a soft gray panel labeled "Harness Library" containing 8-10 small colored module cards in a neat grid (2 columns × 4-5 rows). The cards use four distinct colors representing module types:
  - Purple cards with a tiny gear icon → "Strategy"
  - Green cards with a tiny brain icon → "Memory"
  - Orange cards with a tiny clipboard icon → "Protocol"
  - Red cards with a tiny shield icon → "Guard"
Three of the cards glow brightly with a subtle outer glow effect (these are "Active"). Two cards are faded/semi-transparent (these are "Elided"). One card has a dashed border with a small refresh arrow (this is "Revived"). Add a tiny legend strip below: three dots labeled "Active · Elided · Revived".

【CENTER — Governance Loop (visual focal point)】
In the center of the figure, draw a large elegant circular flow with four nodes arranged clockwise, connected by thick curved gradient arrows:

Node 1 (top center): A blue circle labeled "ACT" with sub-label "Select". From the Library on the left, draw 2-3 small colored cards flying along a curved dotted path into this node, visually showing module selection. A small arrow exits rightward toward the LLM, showing the selected modules being injected into the prompt.

Node 2 (right): A teal circle labeled "EXPERIENCE" with sub-label "Execute & Score". Show a small document icon entering (task) and a checkmark ✓ / cross ✗ icon pair exiting, representing task outcome. A thin utility meter bar sits beside it.

Node 3 (bottom center): An orange circle labeled "REFLECT" with sub-label "Distill". Show a small trajectory visualization (3-4 connected dots representing reasoning steps) being compressed/funneled into a newly born module card (glowing, with a sparkle ✦ effect). Two small labels branch from it: "Broad" (universal patterns) and "Narrow" (task-specific patterns).

Node 4 (left): A coral red circle labeled "GOVERN" with sub-label "Lifecycle". Show a small gate/filter metaphor: several candidate module cards enter from REFLECT, a gatekeeper icon reviews them, some pass through with ✓ (birth), some are rejected with ✗, and two cards merge together with an arrow combining them. A curved arrow returns the admitted modules back to the Library panel.

The four connecting arrows should be thick, smooth bezier curves with gradient colors blending between the two endpoint node colors. Each arrow has a tiny label in italics:
- ACT → EXPERIENCE: "rollout"
- EXPERIENCE → REFLECT: "trajectories"
- REFLECT → GOVERN: "candidates"
- GOVERN → Library: "admitted"

【RIGHT SIDE — Task Domains】
On the far right, draw three small elegant task domain icons stacked vertically in soft rounded boxes, showing where HarnessX applies:
  1. A magnifying glass + document icon → "Search QA"
  2. A house/room icon with an agent figure → "Embodied Planning"
  3. A chat bubble with a clock icon → "Long-Term Memory"
A thin arrow from EXPERIENCE points to these, showing tasks flow in from multiple domains.

【DECORATIVE ELEMENTS】
- Subtle concentric circular rings behind the governance loop (like ripples) in very light gray, giving depth
- Small sparkle/star particles around the REFLECT node, suggesting new knowledge being created
- A thin horizontal line at the very bottom with the text: "Training-Free · Inference-Time Evolution · Any API Model" in small elegant gray text

STYLE:
- Clean vector-art, flat design with subtle gradients and soft shadows
- Suitable for a top-tier NLP venue (EMNLP / ACL) — professional and elegant
- All text in a modern sans-serif typeface (Inter, Helvetica, or SF Pro)
- No photorealistic elements, no 3D renders
- Generous whitespace, balanced composition
- The governance loop should occupy roughly 50% of the figure width and be the clear visual anchor
- Module cards should be small but legible, with rounded corners and consistent sizing
```

---

## 提示词 (简化版)

```
Elegant academic figure for NLP paper "HarnessX". Clean white background, modern flat vector style, 16:9 landscape.

Left: dark blue "Frozen LLM" block with lock icon + gray "Harness Library" panel with colored module cards (purple Strategy, green Memory, orange Protocol, red Guard). Some cards glow (active), some faded (elided), one dashed (revived).

Center (focal point): large circular governance loop with 4 nodes connected by gradient curved arrows — ACT (blue, selects modules) → EXPERIENCE (teal, executes tasks) → REFLECT (orange, distills new modules from trajectories with sparkle effect) → GOVERN (red, birth-gate filters candidates, rejects bad ones, merges similar). Arrows labeled: rollout, trajectories, candidates, admitted.

Right: three small task domain icons — Search QA (magnifying glass), Embodied Planning (house+agent), Long-Term Memory (chat+clock).

Bottom text: "Training-Free · Inference-Time Evolution · Any API Model"

Style: professional, clean, suitable for top NLP conference. Sans-serif fonts, soft shadows, cohesive blue/teal/orange/red palette. No numbers or charts — pure process flow.
```

---

## 配色方案

| 元素 | 颜色 | Hex |
|------|------|-----|
| Primary (LLM, ACT) | Deep Blue | #1E3A5F |
| Secondary (EXPERIENCE) | Teal | #2DA8A0 |
| Highlight (REFLECT) | Warm Orange | #E8843C |
| Alert (GOVERN, Guard) | Coral Red | #E05555 |
| Strategy modules | Purple | #7C5CBF |
| Memory modules | Emerald | #2EAD6B |
| Protocol modules | Amber | #E8A03C |
| Guard modules | Rose | #D94F6B |
| Background panels | Light Gray | #F5F7FA |
| Text | Near Black | #1A1A2E |

---

## 补充说明

- **核心设计原则**：主图不放任何数字/实验结果，纯粹展示方法的流程和架构之美
- **视觉焦点**：中心的四节点治理循环是最大的元素，占据约 50% 宽度
- **关键 novelty 要可视化**：
  - ① 模块有生命周期 → 用 Active(发光)/Elided(淡化)/Revived(虚线+刷新箭头) 三种视觉状态
  - ② Reflect 能生成 broad + narrow 两类模块 → 用两个小标签分支
  - ③ Governor 做 birth-gate → 用 ✓/✗ 和 merge 合并视觉
  - ④ 整个系统无需训练 → Frozen LLM 的锁图标 + 底部文字强调
- **视觉层次**：Library（静态存储）→ Loop（动态治理）→ Domains（应用场景），从左到右层次递进
