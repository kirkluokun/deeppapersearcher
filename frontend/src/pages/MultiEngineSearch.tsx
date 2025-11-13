/**
 * 多引擎搜索页面
 * 支持 arXiv、Semantic Scholar、PubMed 多个搜索引擎
 */

import React, { useState } from 'react';
import SearchForm from '../components/SearchForm';
import PaperList from '../components/PaperList';
import CopyButton from '../components/CopyButton';
import { searchPapers, Paper } from '../services/api';

export default function MultiEngineSearch() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (keywords: string, question: string, engines: string[]) => {
    setLoading(true);
    setError(null);
    setPapers([]);
    setSelectedIds(new Set());

    try {
      const response = await searchPapers({ keywords, question, engines });
      setPapers(response.papers);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '搜索失败');
    } finally {
      setLoading(false);
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
          <div style={styles.loading}>
            正在搜索和处理论文，请稍候...
          </div>
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

