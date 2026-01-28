"""
Skill Generation Module - Generates Claude Agent Skills from codebase
"""

from .skill_generate import (
    SkillReferences,
    SkillRenderContext,
    SkillReferencesResult,
    validate_skill_name,
    generate_default_skill_name,
    generate_project_name,
    generate_skill_description,
    generate_skill_md,
    calculate_statistics,
    generate_statistics_section,
    detect_tech_stack,
    generate_tech_stack_md,
)

__all__ = [
    "SkillReferences",
    "SkillRenderContext",
    "SkillReferencesResult",
    "validate_skill_name",
    "generate_default_skill_name",
    "generate_project_name",
    "generate_skill_description",
    "generate_skill_md",
    "calculate_statistics",
    "generate_statistics_section",
    "detect_tech_stack",
    "generate_tech_stack_md",
]
