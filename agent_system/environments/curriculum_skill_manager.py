# Copyright 2026 AgentOCR Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Curriculum skill manager: helpfulness-based task-skill scheduling (SkillZero)
plus optional omission of *general* skills from the prompt when validation
shows little average lift from the full skill bundle vs. none.

Task-typed ("specific") skill files stay external: they are only pruned by the
existing max_set / delta>=0 curriculum, never by the general-omission path.
"""

import json
import os
from typing import Any, Dict, List, Optional, Set

from agent_system.environments.env_manager import load_skill_file


class CurriculumSkillManager:
    """
    Manages curriculum-based skill selection for ALFWorld / Search training.
    Dynamically updates active *task* skills from per-task validation deltas.
    Optionally stops injecting ``general_skills`` when average per-task delta
    stays near zero (same val runs as vanilla curriculum; no extra rollouts).
    """

    def __init__(
        self,
        skill_mapping_file: str,
        max_set_schedule: List[int],
        total_steps: int,
        test_freq: int,
        skill_internalize: Optional[Dict[str, Any]] = None,
        max_set_min_floor: int = 0,
    ):
        """
        Args:
            skill_mapping_file: Path to JSON with skill_files and task_to_skill.
            max_set_schedule: e.g. [6, 3, 0] — max active skill categories per phase
            total_steps: total training steps (e.g., 150)
            test_freq: validation frequency (e.g., 10)
            skill_internalize: optional dict:
                enable (bool): omit ``general_skills`` from merged prompt when
                    mean per-task val delta (with vs without skills) is persistently tiny
                graduate_epsilon (float): mean delta in [0, epsilon) counts toward omission
                graduate_patience (int): consecutive validations required
                revive_delta (float): reinject general when mean delta exceeds this
            max_set_min_floor: clamp ``get_current_max_set`` to at least this value
        """
        self.skill_mapping_file = os.path.abspath(skill_mapping_file)
        self._mapping_dir = os.path.dirname(self.skill_mapping_file)

        with open(self.skill_mapping_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)

        self.task_to_skill: Dict[str, str] = dict(mapping.get("task_to_skill", {}))
        skill_files_cfg: Dict[str, str] = dict(mapping.get("skill_files", {}))

        self.skill_files: Dict[str, Optional[str]] = {}
        for key, rel_path in skill_files_cfg.items():
            self.skill_files[key] = os.path.join(self._mapping_dir, rel_path)

        self.max_set_schedule = max_set_schedule
        self.total_steps = total_steps
        self.test_freq = test_freq
        self.max_set_min_floor = max(0, int(max_set_min_floor))

        si = skill_internalize or {}
        self._internalize_enable = bool(si.get("enable", False))
        self._graduate_epsilon = float(si.get("graduate_epsilon", 0.02))
        self._graduate_patience = max(1, int(si.get("graduate_patience", 2)))
        self._revive_delta = float(si.get("revive_delta", 0.05))
        # Only ``general_skills`` is omitted when "internalized"; task files stay external.
        self._internalized: Set[str] = set()
        self._graduate_streak: Dict[str, int] = {}

        num_validations = total_steps // test_freq
        assert num_validations % len(max_set_schedule) == 0, (
            f"len(max_set_schedule)={len(max_set_schedule)} must divide "
            f"total_steps/test_freq={num_validations}"
        )

        self._all_skills: Dict[str, Dict[str, str]] = {}
        for key, path in self.skill_files.items():
            if path is not None and os.path.isfile(path):
                self._all_skills[key] = load_skill_file(path)
            else:
                self._all_skills[key] = {}

        self._active_skill_names: List[str] = list(self.skill_files.keys())
        self._active_skills: Dict[str, str] = self._build_skills_from_names(
            self._active_skill_names
        )

    def _build_skills_from_names(
        self, active_names: List[str]
    ) -> Dict[str, str]:
        merged: Dict[str, str] = {}
        for name in active_names:
            if self._internalize_enable and name in self._internalized:
                continue
            if name not in self._all_skills:
                continue
            for sec, content in self._all_skills[name].items():
                merged[sec] = content
        return merged

    def get_task_to_sections(self) -> Dict[str, List[str]]:
        """Map each task id to section keys from that task's skill file."""
        out: Dict[str, List[str]] = {}
        for task, skill_name in self.task_to_skill.items():
            if skill_name in self._all_skills:
                out[task] = list(self._all_skills[skill_name].keys())
        return out

    def get_current_max_set(self, global_step: int) -> int:
        num_validations = self.total_steps // self.test_freq
        validations_per_phase = num_validations // len(self.max_set_schedule)
        validation_idx = (global_step - 1) // self.test_freq
        phase_idx = min(
            validation_idx // validations_per_phase,
            len(self.max_set_schedule) - 1,
        )
        return max(self.max_set_schedule[phase_idx], self.max_set_min_floor)

    @staticmethod
    def aggregate_task_deltas_to_skills(
        delta_success_rates: Dict[str, float],
        task_to_skill: Dict[str, str],
    ) -> Dict[str, float]:
        """Mean validation delta per task-typed skill file (excluding general_skills)."""
        skill_deltas: Dict[str, List[float]] = {}
        for key, delta in delta_success_rates.items():
            if key == "success_rate" or "success_rate" not in key:
                continue
            task = key.replace("_success_rate", "")
            skill_key = task_to_skill.get(task)
            if skill_key is None:
                continue
            skill_deltas.setdefault(skill_key, []).append(delta)
        return {k: sum(v) / len(v) for k, v in skill_deltas.items()}

    @staticmethod
    def mean_per_task_validation_delta(
        delta_success_rates: Dict[str, float],
    ) -> Optional[float]:
        """
        Mean of all ``<task>_success_rate`` deltas (excludes bare ``success_rate``).

        Under the existing two-pass val (full skills on vs all off), this is a
        cheap proxy for how much the *shared* skill bundle still lifts success
        across tasks — used only to decide omitting ``general_skills`` text.
        """
        vals: List[float] = []
        for key, d in delta_success_rates.items():
            if key == "success_rate":
                continue
            if not key.endswith("_success_rate"):
                continue
            vals.append(float(d))
        if not vals:
            return None
        return sum(vals) / len(vals)

    def _update_general_internalized(
        self, delta_success_rates: Dict[str, float]
    ) -> None:
        """Omit ``general_skills`` from the merged prompt when mean lift is tiny."""
        if not self._internalize_enable:
            return
        if "general_skills" not in self.skill_files:
            return
        mean_d = self.mean_per_task_validation_delta(delta_success_rates)
        if mean_d is None:
            return
        gkey = "general_skills"
        if gkey in self._internalized:
            if mean_d > self._revive_delta:
                self._internalized.discard(gkey)
                self._graduate_streak[gkey] = 0
            return
        if 0 <= mean_d < self._graduate_epsilon:
            self._graduate_streak[gkey] = self._graduate_streak.get(gkey, 0) + 1
            if self._graduate_streak[gkey] >= self._graduate_patience:
                self._internalized.add(gkey)
        else:
            self._graduate_streak[gkey] = 0

    def update_skill_set(
        self, delta_success_rates: Dict[str, float], max_set: Optional[int] = None
    ) -> Dict[str, str]:
        if max_set is None:
            max_set = self.max_set_schedule[0] if self.max_set_schedule else 6

        self._update_general_internalized(delta_success_rates)

        skill_deltas_agg = self.aggregate_task_deltas_to_skills(
            delta_success_rates, self.task_to_skill
        )

        candidates = [
            (k, v)
            for k, v in skill_deltas_agg.items()
            if v >= 0 and k != "general_skills"
        ]
        candidates.sort(key=lambda x: -x[1])

        active_names = ["general_skills"]
        if max_set > 0:
            for i, (name, _) in enumerate(candidates):
                if i >= max_set - 1:
                    break
                active_names.append(name)
        else:
            active_names = []

        self._active_skill_names = active_names
        self._active_skills = self._build_skills_from_names(active_names)
        return self._active_skills

    def get_active_skills(self) -> Dict[str, str]:
        return self._active_skills.copy()

    def get_full_skills(self) -> Dict[str, str]:
        """All sections from all skill files (curriculum and general-omit ignored)."""
        merged: Dict[str, str] = {}
        for name in self.skill_files:
            if name not in self._all_skills:
                continue
            for sec, content in self._all_skills[name].items():
                merged[sec] = content
        return merged

    def get_active_skill_names(self) -> List[str]:
        return self._active_skill_names.copy()

    def get_internalized_skill_names(self) -> List[str]:
        """Files omitted from the merged train/val prompt (``general_skills`` only)."""
        return sorted(self._internalized)
