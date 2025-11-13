"""
历史记录存储模块
保存和查询搜索历史记录
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# 历史记录文件目录
HISTORY_DIR = os.path.join(os.path.dirname(__file__), 'history')

# 每个类型最多保存的记录数
MAX_HISTORY_PER_TYPE = 100


def ensure_history_dir():
    """确保历史记录目录存在"""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
        logger.info(f"创建历史记录目录: {HISTORY_DIR}")


def get_history_file_path(record_type: str) -> str:
    """
    获取历史记录文件路径
    
    Args:
        record_type: 记录类型（multi_engine, arxiv_search, latest_papers）
        
    Returns:
        文件路径
    """
    ensure_history_dir()
    filename = f"{record_type}.json"
    return os.path.join(HISTORY_DIR, filename)


def save_history(record_type: str, params: Dict, result_summary: Dict, papers: List[Dict] = None) -> str:
    """
    保存历史记录
    
    Args:
        record_type: 记录类型（multi_engine, arxiv_search, latest_papers）
        params: 搜索参数
        result_summary: 结果摘要（包含 total, papers_count 等）
        papers: 完整的论文数据列表（可选，如果提供则保存完整数据）
        
    Returns:
        记录 ID（UUID）
    """
    try:
        file_path = get_history_file_path(record_type)
        
        # 读取现有记录
        records = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except Exception as e:
                logger.warning(f"读取历史记录文件失败: {str(e)}")
                records = []
        
        # 创建新记录
        record_id = str(uuid.uuid4())
        new_record = {
            "id": record_id,
            "type": record_type,
            "timestamp": datetime.now().isoformat(),
            "params": params,
            "result_summary": result_summary
        }
        
        # 如果提供了论文数据，保存完整数据
        if papers is not None:
            new_record["papers"] = papers
        
        # 添加到列表开头（最新的在前）
        records.insert(0, new_record)
        
        # 限制记录数量
        if len(records) > MAX_HISTORY_PER_TYPE:
            records = records[:MAX_HISTORY_PER_TYPE]
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存历史记录成功: {record_type}, ID: {record_id}")
        return record_id
        
    except Exception as e:
        logger.error(f"保存历史记录失败: {str(e)}")
        raise Exception(f"保存历史记录失败: {str(e)}")


def list_history(record_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """
    查询历史记录
    
    Args:
        record_type: 记录类型（可选，如果为 None 则查询所有类型）
        limit: 返回的最大数量（默认50）
        
    Returns:
        历史记录列表（按时间倒序）
    """
    try:
        all_records = []
        
        if record_type:
            # 查询指定类型
            file_path = get_history_file_path(record_type)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        records = json.load(f)
                        all_records.extend(records)
                except Exception as e:
                    logger.warning(f"读取历史记录文件失败: {str(e)}")
        else:
            # 查询所有类型
            for rt in ['multi_engine', 'arxiv_search', 'latest_papers']:
                file_path = get_history_file_path(rt)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            records = json.load(f)
                            all_records.extend(records)
                    except Exception as e:
                        logger.warning(f"读取历史记录文件失败 ({rt}): {str(e)}")
        
        # 按时间戳排序（最新的在前）
        all_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 限制数量
        return all_records[:limit]
        
    except Exception as e:
        logger.error(f"查询历史记录失败: {str(e)}")
        # 如果查询失败，返回空列表而不是抛出异常
        return []

