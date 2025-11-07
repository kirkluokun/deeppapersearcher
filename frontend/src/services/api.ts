/**
 * API 服务
 * 封装后端 API 调用
 */

import axios from 'axios';

const API_BASE_URL = '/api';

export interface Paper {
  title: string;
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
  engines?: string[];  // 搜索引擎列表：["arxiv", "semantic_scholar"]
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
