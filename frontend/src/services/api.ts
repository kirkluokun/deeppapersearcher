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
  authors: string[];
  published: string | null;
}

export interface ProgressEvent {
  type: 'status' | 'progress' | 'complete' | 'error';
  message?: string;
  progress?: number;
  current?: number;
  total?: number;
  paper_title?: string;
  papers?: Paper[];
  total?: number;
}

export interface SearchRequest {
  keywords: string;
  question: string;
}

export interface SearchResponse {
  papers: Paper[];
  total: number;
}

/**
 * 搜索论文（使用 SSE 获取进度）
 */
export function searchPapersWithProgress(
  request: SearchRequest,
  onProgress: (event: ProgressEvent) => void
): () => void {
  // 使用 fetch 和 ReadableStream 处理 SSE（EventSource 不支持 POST）
  const abortController = new AbortController();
  
  fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal: abortController.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('Response body is not readable');
      }
      
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          // 处理最后剩余的数据
          if (buffer.trim()) {
            const lines = buffer.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const jsonStr = line.slice(6).trim();
                  if (jsonStr) {
                    const data = JSON.parse(jsonStr);
                    console.log('SSE Event received (final):', data);
                    onProgress(data);
                  }
                } catch (e) {
                  console.error('Failed to parse final SSE data:', e, 'Line:', line);
                }
              }
            }
          }
          break;
        }
        
        buffer += decoder.decode(value, { stream: true });
        
        // SSE格式：data: {...}\n\n
        // 按双换行符分割事件
        const events = buffer.split('\n\n');
        // 保留最后一个不完整的事件
        buffer = events.pop() || '';
        
        for (const event of events) {
          if (!event.trim()) continue;
          
          // 查找 data: 行
          const lines = event.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6).trim();
                if (jsonStr) {
                  const data = JSON.parse(jsonStr);
                  console.log('SSE Event received:', data); // 调试日志
                  onProgress(data);
                }
              } catch (e) {
                console.error('Failed to parse SSE data:', e, 'Line:', line);
              }
            }
          }
        }
      }
    })
    .catch((error) => {
      if (error.name !== 'AbortError') {
        onProgress({ type: 'error', message: error.message });
      }
    });
  
  // 返回取消函数
  return () => {
    abortController.abort();
  };
}
