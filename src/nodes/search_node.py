"""
搜索节点实现
负责生成搜索查询和反思查询
"""

import json
from typing import Dict, Any
from datetime import datetime
from json.decoder import JSONDecodeError

from .base_node import BaseNode
from ..prompts import SYSTEM_PROMPT_FIRST_SEARCH, SYSTEM_PROMPT_REFLECTION, get_first_search_prompt, get_reflection_prompt
from ..utils.text_processing import (
    remove_reasoning_from_output,
    clean_json_tags,
    extract_clean_response
)


class FirstSearchNode(BaseNode):
    """为段落生成首次搜索查询的节点"""
    
    def __init__(self, llm_client, time_horizon: str = None):
        """
        初始化首次搜索节点
        
        Args:
            llm_client: LLM客户端
            time_horizon: 时间范围（未来简事专用）
        """
        super().__init__(llm_client, "FirstSearchNode")
        self.time_horizon = time_horizon
    
    def validate_input(self, input_data: Any) -> bool:
        """验证输入数据"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                return "title" in data and "content" in data
            except JSONDecodeError:
                return False
        elif isinstance(input_data, dict):
            return "title" in input_data and "content" in input_data
        return False
    
    def run(self, input_data: Any, **kwargs) -> Dict[str, str]:
        """
        调用LLM生成搜索查询和理由
        
        Args:
            input_data: 包含title和content的字符串或字典
            **kwargs: 额外参数
            
        Returns:
            包含search_query和reasoning的字典
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("输入数据格式错误，需要包含title和content字段")
            
            # 准备输入数据
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("正在生成首次搜索查询")
            
            # 优化输入：移除段落内容中的模糊关键词，保留核心信息
            if isinstance(input_data, dict):
                title = input_data.get("title", "")
                content = input_data.get("content", "")
                # 从标题和内容中提取关键信息，移除模糊词汇
                optimized_input = {
                    "title": self._extract_key_concepts(title),
                    "content": self._extract_key_concepts(content)
                }
                message = json.dumps(optimized_input, ensure_ascii=False)
            
            # 选择提示词
            if self.time_horizon:
                # 获取当前日期
                now = datetime.now()
                current_date = f"{now.year}年{now.month}月{now.day}日"
                prompt = get_first_search_prompt(self.time_horizon, current_date)
            else:
                prompt = SYSTEM_PROMPT_FIRST_SEARCH
            
            # 调用LLM
            response = self.llm_client.invoke(prompt, message)
            
            # 处理响应
            processed_response = self.process_output(response)
            
            # 清理搜索查询中的模糊关键词
            if processed_response.get('search_query'):
                processed_response['search_query'] = self._clean_search_query(
                    processed_response['search_query']
                )
            
            # 确保搜索查询包含正确的日期信息
            if self.time_horizon and processed_response.get('search_query'):
                processed_response = self._enhance_search_query_with_date(
                    processed_response, self.time_horizon
                )
            
            self.log_info(f"生成搜索查询: {processed_response.get('search_query', 'N/A')}")
            return processed_response
            
        except Exception as e:
            self.log_error(f"生成首次搜索查询失败: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        处理LLM输出，提取搜索查询和推理
        
        Args:
            output: LLM原始输出
            
        Returns:
            包含search_query和reasoning的字典
        """
        try:
            # 清理响应文本
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            # 解析JSON
            try:
                result = json.loads(cleaned_output)
            except JSONDecodeError:
                # 使用更强大的提取方法
                result = extract_clean_response(cleaned_output)
                if "error" in result:
                    raise ValueError("JSON解析失败")
            
            # 验证和清理结果
            search_query = result.get("search_query", "")
            reasoning = result.get("reasoning", "")
            
            if not search_query:
                raise ValueError("未找到搜索查询")
            
            return {
                "search_query": search_query,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.log_error(f"处理输出失败: {str(e)}")
            # 返回默认查询
            return {
                "search_query": "相关主题研究",
                "reasoning": "由于解析失败，使用默认搜索查询"
            }
    
    def _extract_key_concepts(self, text: str) -> str:
        """
        从文本中提取关键概念，移除模糊词汇
        
        Args:
            text: 原始文本
            
        Returns:
            提取的关键概念
        """
        if not text:
            return text
        
        # 模糊关键词列表
        vague_keywords = ["未来简事", "简事", "未来", "趋势", "发展", "展望", "预测", "分析"]
        
        # 移除模糊关键词
        cleaned_text = text
        for keyword in vague_keywords:
            cleaned_text = cleaned_text.replace(keyword, "")
        
        # 清理多余空格
        cleaned_text = " ".join(cleaned_text.split())
        
        # 如果清理后文本太短，保留原文本但添加说明
        if len(cleaned_text.strip()) < 5:
            return text
        
        return cleaned_text.strip()
    
    def _clean_search_query(self, query: str) -> str:
        """
        清理搜索查询，移除模糊关键词
        
        Args:
            query: 原始搜索查询
            
        Returns:
            清理后的搜索查询
        """
        vague_keywords = ["未来简事", "简事"]
        cleaned = query
        for keyword in vague_keywords:
            cleaned = cleaned.replace(keyword, "").replace(keyword.lower(), "")
        
        # 清理多余空格
        cleaned = " ".join(cleaned.split())
        return cleaned.strip() if cleaned.strip() else query
    
    def _enhance_search_query_with_date(self, processed_response: Dict[str, str], time_horizon: str) -> Dict[str, str]:
        """
        增强搜索查询，确保包含正确的日期信息
        
        Args:
            processed_response: 处理后的响应
            time_horizon: 时间范围
            
        Returns:
            增强后的响应
        """
        search_query = processed_response.get('search_query', '')
        if not search_query:
            return processed_response
        
        # 获取当前年份
        current_year = datetime.now().year
        
        # 计算未来年份
        now = datetime.now()
        if "个月" in time_horizon:
            months = int(time_horizon.replace("个月", ""))
            try:
                from dateutil.relativedelta import relativedelta
                future_date = now + relativedelta(months=months)
                future_year = future_date.year
            except ImportError:
                # 如果没有dateutil，使用简单的月份计算
                future_year = now.year
                future_month = now.month + months
                while future_month > 12:
                    future_year += 1
                    future_month -= 12
        elif "年" in time_horizon:
            years = int(time_horizon.replace("年", ""))
            future_year = current_year + years
        else:
            future_year = current_year + 1
        
        # 检查查询中是否包含过时的年份（2024年及以前）
        import re
        year_pattern = r'20\d{2}年?'
        years_in_query = re.findall(year_pattern, search_query)
        
        # 如果查询中包含2024年及以前的年份，替换为当前年份或未来年份
        needs_update = False
        for year_str in years_in_query:
            year_num = int(re.search(r'\d{4}', year_str).group())
            if year_num < current_year:
                needs_update = True
                # 替换为未来年份
                search_query = search_query.replace(year_str, f"{future_year}年")
        
        # 如果查询中没有明确的年份，添加未来年份
        if not years_in_query and self.time_horizon:
            # 在查询末尾或适当位置添加年份信息
            if "年" not in search_query and "月" not in search_query:
                search_query = f"{search_query} {future_year}年"
        
        processed_response['search_query'] = search_query
        return processed_response


class ReflectionNode(BaseNode):
    """反思段落并生成新搜索查询的节点"""
    
    def __init__(self, llm_client, time_horizon: str = None):
        """
        初始化反思节点
        
        Args:
            llm_client: LLM客户端
            time_horizon: 时间范围（未来简事专用）
        """
        super().__init__(llm_client, "ReflectionNode")
        self.time_horizon = time_horizon
    
    def validate_input(self, input_data: Any) -> bool:
        """验证输入数据"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                required_fields = ["title", "content", "paragraph_latest_state"]
                return all(field in data for field in required_fields)
            except JSONDecodeError:
                return False
        elif isinstance(input_data, dict):
            required_fields = ["title", "content", "paragraph_latest_state"]
            return all(field in input_data for field in required_fields)
        return False
    
    def run(self, input_data: Any, **kwargs) -> Dict[str, str]:
        """
        调用LLM反思并生成搜索查询
        
        Args:
            input_data: 包含title、content和paragraph_latest_state的字符串或字典
            **kwargs: 额外参数
            
        Returns:
            包含search_query和reasoning的字典
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("输入数据格式错误，需要包含title、content和paragraph_latest_state字段")
            
            # 准备输入数据
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("正在进行反思并生成新搜索查询")
            
            # 获取反思轮次（从kwargs中获取，如果没有则默认为0）
            reflection_iteration = kwargs.get('reflection_iteration', 0)
            
            # 选择提示词
            if self.time_horizon:
                # 获取当前日期
                now = datetime.now()
                current_date = f"{now.year}年{now.month}月{now.day}日"
                prompt = get_reflection_prompt(self.time_horizon, current_date, reflection_iteration)
            else:
                prompt = SYSTEM_PROMPT_REFLECTION
            
            # 调用LLM
            response = self.llm_client.invoke(prompt, message)
            
            # 处理响应
            processed_response = self.process_output(response)
            
            # 清理搜索查询中的模糊关键词
            if processed_response.get('search_query'):
                processed_response['search_query'] = self._clean_search_query(
                    processed_response['search_query']
                )
            
            # 确保搜索查询包含正确的日期信息
            if self.time_horizon and processed_response.get('search_query'):
                processed_response = self._enhance_search_query_with_date(
                    processed_response, self.time_horizon
                )
            
            self.log_info(f"反思生成搜索查询: {processed_response.get('search_query', 'N/A')}")
            return processed_response
            
        except Exception as e:
            self.log_error(f"反思生成搜索查询失败: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        处理LLM输出，提取搜索查询和推理
        
        Args:
            output: LLM原始输出
            
        Returns:
            包含search_query和reasoning的字典
        """
        try:
            # 清理响应文本
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            # 解析JSON
            try:
                result = json.loads(cleaned_output)
            except JSONDecodeError:
                # 使用更强大的提取方法
                result = extract_clean_response(cleaned_output)
                if "error" in result:
                    raise ValueError("JSON解析失败")
            
            # 验证和清理结果
            search_query = result.get("search_query", "")
            reasoning = result.get("reasoning", "")
            
            if not search_query:
                raise ValueError("未找到搜索查询")
            
            return {
                "search_query": search_query,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.log_error(f"处理输出失败: {str(e)}")
            # 返回默认查询
            return {
                "search_query": "深度研究补充信息",
                "reasoning": "由于解析失败，使用默认反思搜索查询"
            }
    
    def _clean_search_query(self, query: str) -> str:
        """
        清理搜索查询，移除模糊关键词
        
        Args:
            query: 原始搜索查询
            
        Returns:
            清理后的搜索查询
        """
        vague_keywords = ["未来简事", "简事"]
        cleaned = query
        for keyword in vague_keywords:
            cleaned = cleaned.replace(keyword, "").replace(keyword.lower(), "")
        
        # 清理多余空格
        cleaned = " ".join(cleaned.split())
        return cleaned.strip() if cleaned.strip() else query
    
    def _enhance_search_query_with_date(self, processed_response: Dict[str, str], time_horizon: str) -> Dict[str, str]:
        """
        增强搜索查询，确保包含正确的日期信息
        
        Args:
            processed_response: 处理后的响应
            time_horizon: 时间范围
            
        Returns:
            增强后的响应
        """
        search_query = processed_response.get('search_query', '')
        if not search_query:
            return processed_response
        
        # 获取当前年份
        current_year = datetime.now().year
        
        # 计算未来年份
        now = datetime.now()
        if "个月" in time_horizon:
            months = int(time_horizon.replace("个月", ""))
            try:
                from dateutil.relativedelta import relativedelta
                future_date = now + relativedelta(months=months)
                future_year = future_date.year
            except ImportError:
                # 如果没有dateutil，使用简单的月份计算
                future_year = now.year
                future_month = now.month + months
                while future_month > 12:
                    future_year += 1
                    future_month -= 12
        elif "年" in time_horizon:
            years = int(time_horizon.replace("年", ""))
            future_year = current_year + years
        else:
            future_year = current_year + 1
        
        # 检查查询中是否包含过时的年份（2024年及以前）
        import re
        year_pattern = r'20\d{2}年?'
        years_in_query = re.findall(year_pattern, search_query)
        
        # 如果查询中包含2024年及以前的年份，替换为当前年份或未来年份
        needs_update = False
        for year_str in years_in_query:
            year_num = int(re.search(r'\d{4}', year_str).group())
            if year_num < current_year:
                needs_update = True
                # 替换为未来年份
                search_query = search_query.replace(year_str, f"{future_year}年")
        
        # 如果查询中没有明确的年份，添加未来年份
        if not years_in_query and self.time_horizon:
            # 在查询末尾或适当位置添加年份信息
            if "年" not in search_query and "月" not in search_query:
                search_query = f"{search_query} {future_year}年"
        
        processed_response['search_query'] = search_query
        return processed_response
