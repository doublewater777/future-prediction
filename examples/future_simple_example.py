"""
未来简事 - 基本使用示例
演示如何使用未来简事进行未来趋势预测
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import DeepSearchAgent, load_config, Config
from src.utils.config import print_config


def future_simple_example():
    """未来简事基本使用示例"""
    print("=" * 60)
    print("🔮 未来简事 - 基本使用示例")
    print("=" * 60)
    
    try:
        # 加载配置
        print("正在加载配置...")
        config = load_config()
        
        # 设置未来简事参数
        config.time_horizon = "3个月"  # 预测未来3个月
        config.analysis_angles = ["技术", "经济", "社会"]  # 从技术、经济、社会角度分析
        
        print_config(config)
        
        # 创建Agent
        print("正在初始化Agent...")
        agent = DeepSearchAgent(config)
        
        # 执行未来预测
        query = "人工智能的发展"
        print(f"\n开始预测: {query}")
        print(f"时间范围: {config.time_horizon}")
        print(f"分析角度: {', '.join(config.analysis_angles)}")
        
        final_report = agent.research(query, save_report=True)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("预测完成！最终报告预览:")
        print("=" * 60)
        print(final_report[:500] + "..." if len(final_report) > 500 else final_report)
        
        # 显示进度信息
        progress = agent.get_progress_summary()
        print(f"\n进度信息:")
        print(f"- 总段落数: {progress['total_paragraphs']}")
        print(f"- 已完成段落: {progress['completed_paragraphs']}")
        print(f"- 完成进度: {progress['progress_percentage']:.1f}%")
        print(f"- 是否完成: {progress['is_completed']}")
        
    except Exception as e:
        print(f"示例运行失败: {str(e)}")
        print("请检查：")
        print("1. 是否安装了所有依赖：pip install -r requirements.txt")
        print("2. 是否设置了必要的API密钥")
        print("3. 网络连接是否正常")
        print("4. 配置文件是否正确")


def future_custom_example():
    """未来简事自定义配置示例"""
    print("\n" + "=" * 60)
    print("🔮 未来简事 - 自定义配置示例")
    print("=" * 60)
    
    try:
        # 创建自定义配置
        config = Config(
            # API密钥（从环境变量或配置文件读取）
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            
            # 模型配置
            default_llm_provider="deepseek",
            deepseek_model="deepseek-chat",
            
            # 搜索配置
            max_search_results=5,
            max_reflections=3,
            
            # 未来简事配置
            time_horizon="1年",  # 预测未来1年
            analysis_angles=["技术", "经济", "社会", "环境"],  # 多角度分析
            
            # 输出配置
            output_dir="future_reports"
        )
        
        # 创建Agent
        agent = DeepSearchAgent(config)
        
        # 执行预测
        query = "电动汽车市场"
        print(f"\n开始预测: {query}")
        print(f"时间范围: {config.time_horizon}")
        print(f"分析角度: {', '.join(config.analysis_angles)}")
        
        # 也可以在research方法中直接指定参数
        final_report = agent.research(
            query,
            save_report=True,
            time_horizon="1年",
            analysis_angles=["技术", "经济", "社会"]
        )
        
        print("\n预测完成！")
        print(f"报告已保存到: {config.output_dir}")
        
    except Exception as e:
        print(f"示例运行失败: {str(e)}")


if __name__ == "__main__":
    # 运行基本示例
    future_simple_example()
    
    # 运行自定义配置示例（可选）
    # future_custom_example()

