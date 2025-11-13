/**
 * 最新论文浏览页面
 * 显示指定分类的最新论文，支持分页加载和摘要精炼
 */

import React, { useState } from 'react';
import CategorySelector from '../components/CategorySelector';
import LatestPaperList from '../components/LatestPaperList';
import CopyButton from '../components/CopyButton';
import HistoryPanel from '../components/HistoryPanel';
import { getLatestPapers, Paper, HistoryRecord } from '../services/api';

// 时间范围选项
const DAY_OPTIONS = [
  { value: 1, label: '最近1天' },
  { value: 3, label: '最近3天' },
  { value: 7, label: '最近7天' },
  { value: 30, label: '最近30天' },
];

export default function LatestPapers() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>('cs'); // 默认选择 cs
  const [selectedDays, setSelectedDays] = useState<number>(7); // 默认7天
  const [offset, setOffset] = useState(0); // 当前偏移量
  const [hasMore, setHasMore] = useState(false); // 是否还有更多论文
  const [showHistory, setShowHistory] = useState(false);

  const limit = 20; // 每次加载20篇

  // 加载最新论文
  const loadLatestPapers = async (resetOffset: boolean = false) => {
    if (!selectedCategory) {
      setError('请选择分类');
      return;
    }

    const currentOffset = resetOffset ? 0 : offset;
    setLoading(true);
    setError(null);

    try {
      const response = await getLatestPapers({
        category: selectedCategory,
        days: selectedDays,
        offset: currentOffset,
        limit: limit,
      });

      if (resetOffset) {
        setPapers(response.papers);
        setOffset(response.papers.length);
        setSelectedIds(new Set()); // 重置选中状态
      } else {
        setPapers((prev) => [...prev, ...response.papers]);
        setOffset((prev) => prev + response.papers.length);
      }

      // 如果返回的论文数量等于 limit，可能还有更多
      setHasMore(response.papers.length === limit);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  // 移除自动加载逻辑，改为手动点击按钮加载

  // 加载更多
  const handleLoadMore = () => {
    loadLatestPapers(false);
  };

  const handleSelectHistory = (record: HistoryRecord) => {
    if (record.type === 'latest_papers') {
      // 如果历史记录包含完整的论文数据，直接使用
      if (record.papers && record.papers.length > 0) {
        setPapers(record.papers);
        // 恢复搜索参数（用于后续加载更多）
        if (record.params.category) {
          setSelectedCategory(record.params.category);
        }
        if (record.params.days) {
          setSelectedDays(record.params.days);
        }
        // 恢复 offset（用于继续加载）
        if (record.params.offset !== undefined) {
          setOffset(record.params.offset);
        }
        setShowHistory(false);
        return;
      }
      
      // 否则恢复搜索参数并重新加载
      if (record.params.category) {
        setSelectedCategory(record.params.category);
        if (record.params.days) {
          setSelectedDays(record.params.days);
        }
        setShowHistory(false);
        // 延迟执行加载，确保状态更新完成
        setTimeout(() => {
          loadLatestPapers(true);
        }, 100);
      }
    }
  };

  const handleToggleSelect = (arxivId: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(arxivId)) {
      newSelected.delete(arxivId);
    } else {
      newSelected.add(arxivId);
    }
    setSelectedIds(newSelected);
  };

  const handleSelectAll = () => {
    setSelectedIds(new Set(papers.map((p) => p.arxiv_id)));
  };

  const handleDeselectAll = () => {
    setSelectedIds(new Set());
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.title}>最新论文浏览</h1>
        <p style={styles.subtitle}>浏览指定领域的最新研究成果</p>
      </header>

      <main style={styles.main}>
        <div style={styles.headerActions}>
          <button
            onClick={() => setShowHistory(!showHistory)}
            style={styles.historyButton}
          >
            {showHistory ? '隐藏历史记录' : '📜 历史记录'}
          </button>
        </div>

        {showHistory && (
          <div style={styles.historyContainer}>
            <HistoryPanel
              type="latest_papers"
              onSelectRecord={handleSelectHistory}
              limit={20}
            />
          </div>
        )}

        <div style={styles.controls}>
          <CategorySelector
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            disabled={loading}
          />

          <div style={styles.inputGroup}>
            <label style={styles.label}>时间范围:</label>
            <div style={styles.dayOptions}>
              {DAY_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  style={{
                    ...styles.dayOption,
                    ...(selectedDays === option.value ? styles.dayOptionSelected : {}),
                  }}
                >
                  <input
                    type="radio"
                    name="days"
                    value={option.value}
                    checked={selectedDays === option.value}
                    onChange={() => setSelectedDays(option.value)}
                    disabled={loading}
                    style={styles.radio}
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={() => loadLatestPapers(true)}
            disabled={loading || !selectedCategory}
            style={{
              ...styles.submitButton,
              ...(loading || !selectedCategory ? styles.buttonDisabled : {}),
            }}
          >
            {loading ? '加载中...' : '给我简报'}
          </button>
        </div>

        {error && (
          <div style={styles.error}>
            <strong>错误:</strong> {error}
          </div>
        )}

        {loading && papers.length === 0 && (
          <div style={styles.loading}>
            正在加载最新论文，请稍候...
          </div>
        )}

        {!loading && papers.length === 0 && !selectedCategory && (
          <div style={styles.empty}>
            请选择分类并点击"给我简报"按钮获取最新论文
          </div>
        )}

        {!loading && papers.length === 0 && selectedCategory && (
          <div style={styles.empty}>
            未找到论文，请尝试调整时间范围或分类
          </div>
        )}

        {papers.length > 0 && (
          <>
            <div style={styles.selectActions}>
              <button
                onClick={handleSelectAll}
                style={styles.selectButton}
              >
                全选
              </button>
              <button
                onClick={handleDeselectAll}
                style={styles.selectButton}
              >
                取消全选
              </button>
            </div>

            <CopyButton papers={papers} selectedIds={selectedIds} />
            
            <LatestPaperList 
              papers={papers}
              selectedIds={selectedIds}
              onToggleSelect={handleToggleSelect}
            />
            
            {hasMore && (
              <div style={styles.loadMoreContainer}>
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  style={{
                    ...styles.loadMoreButton,
                    ...(loading ? styles.buttonDisabled : {}),
                  }}
                >
                  {loading ? '加载中...' : `加载更多（已加载 ${papers.length} 篇）`}
                </button>
              </div>
            )}

            {!hasMore && papers.length > 0 && (
              <div style={styles.noMore}>
                已显示全部 {papers.length} 篇论文
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: '30px 20px',
    textAlign: 'center',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginBottom: '30px',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '10px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#666',
  },
  main: {
    paddingBottom: '40px',
  },
  controls: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginBottom: '20px',
  },
  inputGroup: {
    marginTop: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '12px',
    fontWeight: 'bold',
    color: '#333',
    fontSize: '14px',
  },
  dayOptions: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
  },
  dayOption: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px 16px',
    borderRadius: '6px',
    border: '2px solid #e0e0e0',
    backgroundColor: '#fff',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  dayOptionSelected: {
    border: '2px solid #000',
    backgroundColor: '#fff',
  },
  radio: {
    marginRight: '8px',
    width: '18px',
    height: '18px',
    cursor: 'pointer',
  },
  loading: {
    maxWidth: '800px',
    margin: '20px auto',
    padding: '20px',
    textAlign: 'center',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  error: {
    maxWidth: '800px',
    margin: '20px auto',
    padding: '15px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '4px',
    border: '1px solid #f5c6cb',
  },
  empty: {
    maxWidth: '800px',
    margin: '20px auto',
    padding: '40px',
    textAlign: 'center',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    color: '#999',
    fontSize: '16px',
  },
  loadMoreContainer: {
    maxWidth: '1200px',
    margin: '30px auto',
    textAlign: 'center',
  },
  loadMoreButton: {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
  noMore: {
    maxWidth: '1200px',
    margin: '20px auto',
    padding: '15px',
    textAlign: 'center',
    color: '#666',
    fontSize: '14px',
  },
  submitButton: {
    width: '100%',
    marginTop: '20px',
    padding: '12px',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  headerActions: {
    maxWidth: '800px',
    margin: '0 auto 20px',
    display: 'flex',
    justifyContent: 'flex-end',
  },
  historyButton: {
    padding: '8px 16px',
    backgroundColor: '#6c757d',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  historyContainer: {
    maxWidth: '800px',
    margin: '0 auto 20px',
  },
  selectActions: {
    maxWidth: '1200px',
    margin: '0 auto 20px',
    padding: '0 20px',
    display: 'flex',
    gap: '10px',
  },
  selectButton: {
    padding: '8px 16px',
    backgroundColor: '#6c757d',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
};

