# Copyright 2026 AgentOCR Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Unit tests: general_skills omission vs task skills stay mergeable."""

import json
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agent_system.environments.curriculum_skill_manager import CurriculumSkillManager


def _write_repo(tmp: Path) -> str:
    (tmp / "g.md").write_text(
        "### GENERAL SKILLS ###\ngen\n", encoding="utf-8"
    )
    (tmp / "h.md").write_text(
        "### TASK: heat ###\nheat tips\n", encoding="utf-8"
    )
    mapping = {
        "skill_files": {"general_skills": "g.md", "heat": "h.md"},
        "task_to_skill": {"pick_heat_then_place_in_recep": "heat"},
    }
    mp = tmp / "skill_mapping.json"
    mp.write_text(json.dumps(mapping), encoding="utf-8")
    return str(mp)


class TestCurriculumGeneralOmit(unittest.TestCase):
    def test_mean_per_task_validation_delta(self):
        d = {
            "pick_heat_then_place_in_recep_success_rate": 0.1,
            "pick_and_place_success_rate": 0.3,
            "success_rate": 0.2,
        }
        self.assertAlmostEqual(
            CurriculumSkillManager.mean_per_task_validation_delta(d), 0.2
        )

    def test_aggregate_task_deltas_to_skills(self):
        task_to_skill = {"t1": "a", "t2": "a"}
        deltas = {"t1_success_rate": 0.1, "t2_success_rate": 0.3}
        agg = CurriculumSkillManager.aggregate_task_deltas_to_skills(
            deltas, task_to_skill
        )
        self.assertAlmostEqual(agg["a"], 0.2)

    def test_general_omitted_after_patience(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            mp = _write_repo(Path(td))
            mgr = CurriculumSkillManager(
                skill_mapping_file=mp,
                max_set_schedule=[6],
                total_steps=30,
                test_freq=10,
                skill_internalize={
                    "enable": True,
                    "graduate_epsilon": 0.05,
                    "graduate_patience": 2,
                    "revive_delta": 0.15,
                },
            )
            low = {"pick_heat_then_place_in_recep_success_rate": 0.01}
            mgr.update_skill_set(low, max_set=6)
            self.assertNotIn("general_skills", mgr.get_internalized_skill_names())
            mgr.update_skill_set(low, max_set=6)
            self.assertIn("general_skills", mgr.get_internalized_skill_names())
            active = mgr.get_active_skills()
            self.assertNotIn("GENERAL SKILLS", active)
            self.assertIn("TASK: heat", active)

    def test_task_skill_not_omitted_by_internalize_even_if_low_delta(self):
        """Low per-skill delta must not remove task file; only general uses mean path."""
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            mp = _write_repo(Path(td))
            mgr = CurriculumSkillManager(
                skill_mapping_file=mp,
                max_set_schedule=[6],
                total_steps=30,
                test_freq=10,
                skill_internalize={
                    "enable": True,
                    "graduate_epsilon": 0.05,
                    "graduate_patience": 1,
                    "revive_delta": 0.99,
                },
            )
            # Mean delta high -> general not omitted; heat delta low but heat not in internalized
            deltas = {"pick_heat_then_place_in_recep_success_rate": 0.5}
            mgr.update_skill_set(deltas, max_set=6)
            self.assertEqual(mgr.get_internalized_skill_names(), [])
            self.assertIn("TASK: heat", mgr.get_active_skills())

    def test_revive_general(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            mp = _write_repo(Path(td))
            mgr = CurriculumSkillManager(
                skill_mapping_file=mp,
                max_set_schedule=[6],
                total_steps=30,
                test_freq=10,
                skill_internalize={
                    "enable": True,
                    "graduate_epsilon": 0.05,
                    "graduate_patience": 1,
                    "revive_delta": 0.1,
                },
            )
            mgr.update_skill_set(
                {"pick_heat_then_place_in_recep_success_rate": 0.01}, max_set=6
            )
            self.assertIn("general_skills", mgr.get_internalized_skill_names())
            mgr.update_skill_set(
                {"pick_heat_then_place_in_recep_success_rate": 0.2}, max_set=6
            )
            self.assertNotIn("general_skills", mgr.get_internalized_skill_names())

    def test_get_full_skills_always_has_general(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            mp = _write_repo(Path(td))
            mgr = CurriculumSkillManager(
                skill_mapping_file=mp,
                max_set_schedule=[6],
                total_steps=30,
                test_freq=10,
                skill_internalize={
                    "enable": True,
                    "graduate_epsilon": 0.05,
                    "graduate_patience": 1,
                    "revive_delta": 0.99,
                },
            )
            mgr.update_skill_set(
                {"pick_heat_then_place_in_recep_success_rate": 0.01}, max_set=6
            )
            full = mgr.get_full_skills()
            self.assertIn("GENERAL SKILLS", full)

    def test_max_set_min_floor(self):
        repo_mapping = _REPO_ROOT / "skills" / "alfworld" / "skill_mapping.json"
        if not repo_mapping.is_file():
            self.skipTest("repo skill_mapping.json not found")
        mgr = CurriculumSkillManager(
            skill_mapping_file=str(repo_mapping),
            max_set_schedule=[0],
            total_steps=10,
            test_freq=10,
            max_set_min_floor=1,
        )
        self.assertEqual(mgr.get_current_max_set(1), 1)


if __name__ == "__main__":
    unittest.main()
