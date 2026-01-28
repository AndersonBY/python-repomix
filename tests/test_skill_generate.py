"""
Test suite for Skill Generation functionality
"""

import pytest

from src.repomix.core.skill.skill_generate import (
    SkillReferences,
    SkillRenderContext,
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
from src.repomix.core.file.file_types import ProcessedFile


class TestValidateSkillName:
    """Test cases for validate_skill_name function"""

    def test_simple_name(self):
        """Test simple skill name"""
        assert validate_skill_name("myskill") == "myskill"

    def test_name_with_spaces(self):
        """Test name with spaces"""
        assert validate_skill_name("my skill") == "my-skill"

    def test_name_with_underscores(self):
        """Test name with underscores"""
        assert validate_skill_name("my_skill") == "my-skill"

    def test_name_with_uppercase(self):
        """Test name with uppercase"""
        assert validate_skill_name("MySkill") == "myskill"

    def test_name_with_special_chars(self):
        """Test name with special characters"""
        assert validate_skill_name("my@skill!") == "myskill"

    def test_empty_name_raises(self):
        """Test empty name raises ValueError"""
        with pytest.raises(ValueError):
            validate_skill_name("")

    def test_only_special_chars_raises(self):
        """Test name with only special chars raises ValueError"""
        with pytest.raises(ValueError):
            validate_skill_name("@#$%")


class TestGenerateDefaultSkillName:
    """Test cases for generate_default_skill_name function"""

    def test_with_root_dirs(self):
        """Test with root directories"""
        result = generate_default_skill_name(["/path/to/my-project"])
        assert result == "my-project"

    def test_empty_root_dirs(self):
        """Test with empty root directories"""
        result = generate_default_skill_name([])
        assert result == "codebase"


class TestGenerateProjectName:
    """Test cases for generate_project_name function"""

    def test_with_root_dirs(self):
        """Test with root directories"""
        result = generate_project_name(["/path/to/MyProject"])
        assert result == "MyProject"

    def test_empty_root_dirs(self):
        """Test with empty root directories"""
        result = generate_project_name([])
        assert result == "Project"


class TestGenerateSkillDescription:
    """Test cases for generate_skill_description function"""

    def test_basic_description(self):
        """Test basic description generation"""
        result = generate_skill_description("my-skill", "MyProject")
        assert "MyProject" in result
        assert "Codebase reference" in result


class TestGenerateSkillMd:
    """Test cases for generate_skill_md function"""

    def test_basic_skill_md(self):
        """Test basic SKILL.md generation"""
        context = SkillRenderContext(
            skill_name="my-skill",
            skill_description="Test skill",
            project_name="TestProject",
            total_files=10,
            total_lines=500,
            total_tokens=1000,
            has_tech_stack=False,
        )
        result = generate_skill_md(context)

        assert "name: my-skill" in result
        assert "TestProject" in result
        assert "10 files" in result
        assert "500 lines" in result
        assert "1000 tokens" in result

    def test_skill_md_with_tech_stack(self):
        """Test SKILL.md with tech stack"""
        context = SkillRenderContext(
            skill_name="my-skill",
            skill_description="Test skill",
            project_name="TestProject",
            total_files=10,
            total_lines=500,
            total_tokens=1000,
            has_tech_stack=True,
        )
        result = generate_skill_md(context)

        assert "tech-stack.md" in result

    def test_skill_md_with_source_url(self):
        """Test SKILL.md with source URL"""
        context = SkillRenderContext(
            skill_name="my-skill",
            skill_description="Test skill",
            project_name="TestProject",
            total_files=10,
            total_lines=500,
            total_tokens=1000,
            has_tech_stack=False,
            source_url="https://github.com/test/project",
        )
        result = generate_skill_md(context)

        assert "https://github.com/test/project" in result


class TestCalculateStatistics:
    """Test cases for calculate_statistics function"""

    def test_basic_statistics(self):
        """Test basic statistics calculation"""
        files = [
            ProcessedFile(path="file1.py", content="line1\nline2"),
            ProcessedFile(path="file2.py", content="line1"),
        ]
        line_counts = {"file1.py": 2, "file2.py": 1}

        result = calculate_statistics(files, line_counts)

        assert result["total_files"] == 2
        assert result["total_lines"] == 3


class TestGenerateStatisticsSection:
    """Test cases for generate_statistics_section function"""

    def test_statistics_section(self):
        """Test statistics section generation"""
        stats = {"total_files": 10, "total_lines": 500}
        result = generate_statistics_section(stats)

        assert "Total Files: 10" in result
        assert "Total Lines: 500" in result


class TestDetectTechStack:
    """Test cases for detect_tech_stack function"""

    def test_detect_python(self):
        """Test Python detection"""
        files = [
            ProcessedFile(path="main.py", content="print('hello')"),
            ProcessedFile(path="utils.py", content="def helper(): pass"),
        ]
        result = detect_tech_stack(files)

        assert result is not None
        assert "Python" in result["languages"]

    def test_detect_frameworks(self):
        """Test framework detection"""
        files = [
            ProcessedFile(path="app.py", content="from flask import Flask"),
        ]
        result = detect_tech_stack(files)

        assert result is not None
        assert "Flask" in result["frameworks"]

    def test_no_tech_stack(self):
        """Test no tech stack detected"""
        files = [
            ProcessedFile(path="readme.md", content="# README"),
        ]
        result = detect_tech_stack(files)

        assert result is None


class TestGenerateTechStackMd:
    """Test cases for generate_tech_stack_md function"""

    def test_tech_stack_md(self):
        """Test tech stack markdown generation"""
        tech_stack = {
            "languages": ["Python", "JavaScript"],
            "frameworks": ["Flask", "React"],
        }
        result = generate_tech_stack_md(tech_stack)

        assert "# Technology Stack" in result
        assert "Python" in result
        assert "JavaScript" in result
        assert "Flask" in result
        assert "React" in result


if __name__ == "__main__":
    pytest.main([__file__])
