/**
 * 历史记录面板组件
 * 显示搜索历史记录，支持查看详情
 */

import React, { useState, useEffect } from 'react';
import { listHistory, HistoryRecord } from '../services/api';

interface HistoryPanelProps {
  type?: 'multi_engine' | 'arxiv_search' | 'latest_papers' | null;  // 记录类型（可选，null表示所有类型）
  onSelectRecord?: (record: HistoryRecord) => void;  // 选择记录的回调
  limit?: number;  // 显示的最大数量（默认20）
}

export default function HistoryPanel({ 
  type = null, 
  onSelectRecord,
  limit = 20 
}: HistoryPanelProps) {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // 加载历史记录
  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listHistory({ type: type || undefined, limit });
      setRecords(response.records);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '加载历史记录失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [type, limit]);

  // 格式化时间
  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return timestamp;
    }
  };

  // 获取类型显示名称
  const getTypeName = (type: string) => {
    const typeMap: Record<string, string> = {
      'multi_engine': '多引擎搜索',
      'arxiv_search': 'arXiv 搜索',
      'latest_papers': '最新论文',
    };
    return typeMap[type] || type;
  };

  // 格式化参数显示
  const formatParams = (params: HistoryRecord['params']) => {
    const parts: string[] = [];
    if (params.keywords) {
      parts.push(`关键词: ${params.keywords}`);
    }
    if (params.question) {
      parts.push(`问题: ${params.question}`);
    }
    if (params.category) {
      parts.push(`分类: ${params.category}`);
    }
    if (params.days) {
      parts.push(`时间范围: 最近${params.days}天`);
    }
    if (params.engines && params.engines.length > 0) {
      parts.push(`引擎: ${params.engines.join(', ')}`);
    }
    return parts.length > 0 ? parts.join(' | ') : '无参数';
  };

  const handleToggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleSelect = (record: HistoryRecord) => {
    if (onSelectRecord) {
      onSelectRecord(record);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>历史记录</h3>
        <button onClick={loadHistory} disabled={loading} style={styles.refreshButton}>
          {loading ? '加载中...' : '🔄 刷新'}
        </button>
      </div>

      {error && (
        <div style={styles.error}>
          {error}
        </div>
      )}

      {loading && records.length === 0 && (
        <div style={styles.loading}>加载中...</div>
      )}

      {!loading && records.length === 0 && (
        <div style={styles.empty}>暂无历史记录</div>
      )}

      {records.length > 0 && (
        <div style={styles.list}>
          {records.map((record) => (
            <div key={record.id} style={styles.recordItem}>
              <div style={styles.recordHeader}>
                <div style={styles.recordInfo}>
                  <span style={styles.typeBadge}>{getTypeName(record.type)}</span>
                  <span style={styles.time}>{formatTime(record.timestamp)}</span>
                </div>
                <div style={styles.recordActions}>
                  <button
                    onClick={() => handleSelect(record)}
                    style={styles.selectButton}
                  >
                    使用
                  </button>
                  <button
                    onClick={() => handleToggleExpand(record.id)}
                    style={styles.expandButton}
                  >
                    {expandedId === record.id ? '收起' : '详情'}
                  </button>
                </div>
              </div>

              <div style={styles.recordSummary}>
                <span style={styles.resultCount}>
                  找到 {record.result_summary.papers_count} 篇论文
                </span>
              </div>

              {expandedId === record.id && (
                <div style={styles.recordDetails}>
                  <div style={styles.detailRow}>
                    <strong>参数:</strong> {formatParams(record.params)}
                  </div>
                  <div style={styles.detailRow}>
                    <strong>结果:</strong> 共 {record.result_summary.total} 篇论文
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    padding: '20px',
    maxHeight: '600px',
    overflowY: 'auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#333',
    margin: 0,
  },
  refreshButton: {
    padding: '6px 12px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  error: {
    padding: '10px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '4px',
    marginBottom: '15px',
    fontSize: '14px',
  },
  loading: {
    padding: '20px',
    textAlign: 'center',
    color: '#666',
  },
  empty: {
    padding: '40px',
    textAlign: 'center',
    color: '#999',
    fontSize: '14px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  recordItem: {
    border: '1px solid #e0e0e0',
    borderRadius: '6px',
    padding: '15px',
    backgroundColor: '#f9f9f9',
    transition: 'all 0.2s',
  },
  recordHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '10px',
  },
  recordInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    flex: 1,
  },
  typeBadge: {
    display: 'inline-block',
    padding: '4px 8px',
    backgroundColor: '#007bff',
    color: '#fff',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 'bold',
    width: 'fit-content',
  },
  time: {
    fontSize: '12px',
    color: '#666',
  },
  recordActions: {
    display: 'flex',
    gap: '8px',
  },
  selectButton: {
    padding: '6px 12px',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '12px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  expandButton: {
    padding: '6px 12px',
    backgroundColor: '#6c757d',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '12px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  recordSummary: {
    fontSize: '14px',
    color: '#333',
  },
  resultCount: {
    fontWeight: '500',
  },
  recordDetails: {
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid #e0e0e0',
    fontSize: '13px',
    color: '#666',
  },
  detailRow: {
    marginBottom: '6px',
  },
};

