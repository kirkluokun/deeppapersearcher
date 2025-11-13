/**
 * API 服务
 * 封装后端 API 调用
 */

import axios from 'axios';

const API_BASE_URL = '/api';

export interface Paper {
  title: string;
  title_zh?: string | null;  // 中文标题（可选）
  abstract: string;
  abstract_zh: string;  // 中文摘要
  keywords: string;  // 关键词（中文）
  relevance_summary: string;  // 相关性评估概述
  arxiv_id: string;
  url: string;
  pdf_url?: string | null;  // PDF 下载链接（可选）
  authors: string[];
  published: string | null;
  source: string;  // 来源：arxiv 或 semantic_scholar
}


export interface SearchRequest {
  keywords: string;
  question: string;
  engines?: string[];  // 搜索引擎列表：["arxiv", "semantic_scholar", "pubmed"]
  arxiv_category?: string | null;  // arXiv 分类（可选），如 "cs", "physics", "math" 等
}

export interface SearchResponse {
  papers: Paper[];
  total: number;
}

/**
 * 搜索论文
 */
export async function searchPapers(request: SearchRequest): Promise<SearchResponse> {
  const response = await axios.post<SearchResponse>(`${API_BASE_URL}/search`, request);
  return response.data;
}

/**
 * 获取最新论文请求
 */
export interface LatestPapersRequest {
  category: string;  // 分类代码（如 "cs", "physics", "math"）
  days?: number;  // 获取最近多少天的论文（默认7天）
  offset?: number;  // 分页偏移量（默认0）
  limit?: number;  // 返回的最大数量（默认20）
}

/**
 * 获取最新论文
 */
export async function getLatestPapers(request: LatestPapersRequest): Promise<SearchResponse> {
  const response = await axios.post<SearchResponse>(`${API_BASE_URL}/arxiv/latest`, request);
  return response.data;
}

/**
 * 精炼摘要请求
 */
export interface RefineAbstractRequest {
  arxiv_id: string;  // arXiv 论文 ID
  abstract: string;  // 原始摘要
  title?: string;  // 论文标题（可选）
}

/**
 * 精炼摘要响应
 */
export interface RefineAbstractResponse {
  refined_abstract: string;  // 精炼后的摘要
}

/**
 * 精炼摘要
 */
export async function refineAbstract(request: RefineAbstractRequest): Promise<RefineAbstractResponse> {
  const response = await axios.post<RefineAbstractResponse>(`${API_BASE_URL}/arxiv/refine-abstract`, request);
  return response.data;
}

/**
 * 历史记录接口
 */
export interface HistoryRecord {
  id: string;
  type: 'multi_engine' | 'arxiv_search' | 'latest_papers';
  timestamp: string;
  params: {
    keywords?: string;
    question?: string;
    engines?: string[];
    arxiv_category?: string | null;
    category?: string;
    days?: number;
    offset?: number;
    limit?: number;
  };
  result_summary: {
    total: number;
    papers_count: number;
  };
  papers?: Paper[];  // 完整的论文数据（可选，如果存在则直接使用）
}

/**
 * 保存历史记录请求
 */
export interface SaveHistoryRequest {
  type: 'multi_engine' | 'arxiv_search' | 'latest_papers';
  params: Record<string, any>;
  result_summary: {
    total: number;
    papers_count: number;
  };
}

/**
 * 查询历史记录请求
 */
export interface ListHistoryRequest {
  type?: 'multi_engine' | 'arxiv_search' | 'latest_papers' | null;
  limit?: number;
}

/**
 * 查询历史记录响应
 */
export interface ListHistoryResponse {
  records: HistoryRecord[];
}

/**
 * 保存历史记录
 */
export async function saveHistory(request: SaveHistoryRequest): Promise<{ id: string }> {
  const response = await axios.post<{ id: string }>(`${API_BASE_URL}/history/save`, request);
  return response.data;
}

/**
 * 查询历史记录
 */
export async function listHistory(request: ListHistoryRequest = {}): Promise<ListHistoryResponse> {
  const response = await axios.post<ListHistoryResponse>(`${API_BASE_URL}/history/list`, request);
  return response.data;
}

/**
 * 获取单个历史记录详情
 */
export async function getHistoryRecord(record_id: string): Promise<{ record: HistoryRecord }> {
  const response = await axios.get<{ record: HistoryRecord }>(`${API_BASE_URL}/history/get/${record_id}`);
  return response.data;
}
