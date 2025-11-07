/**
 * 主应用组件
 */

import React, { useState, useRef } from 'react';
import SearchForm from './components/SearchForm';
import PaperList from './components/PaperList';
import CopyButton from './components/CopyButton';
import ProgressBar from './components/ProgressBar';
import { searchPapersWithProgress, Paper, ProgressEvent } from './services/api';

function App() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [currentPaper, setCurrentPaper] = useState<{ current: number; total: number; title: string } | null>(null);
  const abortRef = useRef<(() => void) | null>(null);

  const handleSearch = (keywords: string, question: string) => {
    setLoading(true);
    setError(null);
    setPapers([]);
    setSelectedIds(new Set());
    setProgress(0);
    setProgressMessage('开始搜索...');
    setCurrentPaper(null);

    const cancel = searchPapersWithProgress(
      { keywords, question },
      (event: ProgressEvent) => {
        console.log('Progress event received:', event); // 调试日志
        
        // 确保状态更新使用函数式更新，避免闭包问题
        if (event.type === 'status') {
          setProgressMessage(event.message || '');
          if (event.progress !== undefined && event.progress !== null) {
            console.log('Status: Setting progress to:', event.progress); // 调试日志
            setProgress(() => event.progress!);
          }
        } else if (event.type === 'progress') {
          const progressValue = typeof event.progress === 'number' ? event.progress : 0;
          console.log('Progress: Setting progress to:', progressValue, 'from event:', event); // 调试日志
          setProgress(() => progressValue);
          // 同时更新消息，显示当前处理的论文
          if (event.paper_title) {
            setProgressMessage(() => `正在处理: ${event.paper_title}...`);
          }
          if (event.current !== undefined && event.total !== undefined) {
            setCurrentPaper({
              current: event.current,
              total: event.total,
              title: event.paper_title || '',
            });
          }
        } else if (event.type === 'complete') {
          console.log('Complete event received, papers:', event.papers?.length);
          setProgress(() => 100);
          setProgressMessage('完成！');
          if (event.papers) {
            setPapers(event.papers);
          }
          setLoading(false);
          setCurrentPaper(null);
        } else if (event.type === 'error') {
          setError(event.message || '搜索失败');
          setLoading(false);
          setCurrentPaper(null);
        }
      }
    );

    abortRef.current = cancel;
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
        <h1 style={styles.title}>arXiv 论文检索系统</h1>
        <p style={styles.subtitle}>基于 Gemini 2.0 Flash 的智能论文筛选</p>
      </header>

      <main style={styles.main}>
        <SearchForm onSearch={handleSearch} loading={loading} />

        {error && (
          <div style={styles.error}>
            <strong>错误:</strong> {error}
          </div>
        )}

        {loading && (
          <ProgressBar
            progress={progress}
            message={progressMessage || '处理中...'}
            current={currentPaper?.current}
            total={currentPaper?.total}
            paperTitle={currentPaper?.title}
          />
        )}

        {!loading && papers.length > 0 && (
          <>
            <CopyButton papers={papers} selectedIds={selectedIds} />
            <PaperList
              papers={papers}
              selectedIds={selectedIds}
              onToggleSelect={handleToggleSelect}
              onSelectAll={handleSelectAll}
              onDeselectAll={handleDeselectAll}
            />
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
};

export default App;
