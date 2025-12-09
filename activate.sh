#!/bin/bash
# 激活虚拟环境的便捷脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 激活虚拟环境
source "$SCRIPT_DIR/venv/bin/activate"

echo "✅ 虚拟环境已激活！"
echo "📍 当前 Python: $(which python)"
echo "📍 当前 pip: $(which pip)"
echo ""
echo "💡 提示：使用 'deactivate' 退出虚拟环境"

