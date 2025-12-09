"""
Prompt模块
定义Deep Search Agent各个阶段使用的系统提示词
"""

from .prompts import (
    SYSTEM_PROMPT_REPORT_STRUCTURE,
    SYSTEM_PROMPT_FIRST_SEARCH,
    SYSTEM_PROMPT_FIRST_SUMMARY,
    SYSTEM_PROMPT_REFLECTION,
    SYSTEM_PROMPT_REFLECTION_SUMMARY,
    SYSTEM_PROMPT_REPORT_FORMATTING,
    get_report_structure_prompt,
    get_first_search_prompt,
    get_first_summary_prompt,
    get_reflection_prompt,
    get_reflection_summary_prompt,
    get_report_formatting_prompt,
    output_schema_report_structure,
    output_schema_first_search,
    output_schema_first_summary,
    output_schema_reflection,
    output_schema_reflection_summary,
    input_schema_report_formatting
)

__all__ = [
    "SYSTEM_PROMPT_REPORT_STRUCTURE",
    "SYSTEM_PROMPT_FIRST_SEARCH", 
    "SYSTEM_PROMPT_FIRST_SUMMARY",
    "SYSTEM_PROMPT_REFLECTION",
    "SYSTEM_PROMPT_REFLECTION_SUMMARY",
    "SYSTEM_PROMPT_REPORT_FORMATTING",
    "get_report_structure_prompt",
    "get_first_search_prompt",
    "get_first_summary_prompt",
    "get_reflection_prompt",
    "get_reflection_summary_prompt",
    "get_report_formatting_prompt",
    "output_schema_report_structure",
    "output_schema_first_search",
    "output_schema_first_summary", 
    "output_schema_reflection",
    "output_schema_reflection_summary",
    "input_schema_report_formatting"
]
