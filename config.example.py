# Deep Search Agent 配置文件模板
# 请复制此文件为 config.py 并填入您的API密钥
# 或者使用环境变量设置 API 密钥（推荐方式）

import os

# ===== API 密钥配置 =====
# 优先从环境变量读取，如果没有则使用配置文件中的值
# 推荐方式：使用环境变量设置，避免将密钥提交到版本控制

# DeepSeek API Key
# 方式1：使用环境变量（推荐）
# export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
# 方式2：直接在此文件中设置（不推荐，会被 git 跟踪）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key_here")

# OpenAI API Key (可选)
# 方式1：使用环境变量（推荐）
# export OPENAI_API_KEY="your_openai_api_key_here"
# 方式2：直接在此文件中设置（不推荐，会被 git 跟踪）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# Tavily搜索API Key
# 方式1：使用环境变量（推荐）
# export TAVILY_API_KEY="your_tavily_api_key_here"
# 方式2：直接在此文件中设置（不推荐，会被 git 跟踪）
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "your_tavily_api_key_here")

# ===== 模型配置 =====
DEFAULT_LLM_PROVIDER = "deepseek"  # deepseek 或 openai
DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"

# ===== Agent 配置 =====
MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
SAVE_INTERMEDIATE_STATES = True

