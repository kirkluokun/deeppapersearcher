/**
 * arXiv 专用搜索页面
 * 提供分类选择功能和 arXiv 论文搜索
 */

import React, { useState } from 'react';
import CategorySelector from '../components/CategorySelector';
import PaperList from '../components/PaperList';
import CopyButton from '../components/CopyButton';
import { searchPapers, Paper } from '../services/api';

export default function ArxivSearch() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [keywords, setKeywords] = useState('');
  const [question, setQuestion] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>('cs'); // 默认选择 cs

  const handleSearch = async () => {
    if (!keywords.trim() || !question.trim()) {
      setError('请填写搜索关键词和问题');
      return;
    }

    setLoading(true);
    setError(null);
    setPapers([]);
    setSelectedIds(new Set());

    try {
      const response = await searchPapers({
        keywords: keywords.trim(),
        question: question.trim(),
        engines: ['arxiv'], // 只使用 arXiv 引擎
        arxiv_category: selectedCategory || null,
      });
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.title}>arXiv 论文检索</h1>
        <p style={styles.subtitle}>选择分类并搜索 arXiv 论文</p>
      </header>

      <main style={styles.main}>
        <form onSubmit={handleSubmit} style={styles.form}>
          <CategorySelector
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            disabled={loading}
          />

          <div style={styles.inputGroup}>
            <label style={styles.label}>搜索关键词:</label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="例如: machine learning, neural networks"
              style={styles.input}
              disabled={loading}
              required
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>你想了解的问题:</label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="例如: 最新的深度学习优化方法有哪些？"
              style={styles.textarea}
              disabled={loading}
              required
              rows={3}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !keywords.trim() || !question.trim()}
            style={{
              ...styles.button,
              ...(loading || !keywords.trim() || !question.trim() ? styles.buttonDisabled : {}),
            }}
          >
            {loading ? '搜索中...' : '搜索论文'}
          </button>
        </form>

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
  form: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  inputGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: 'bold',
    color: '#333',
  },
  input: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  textarea: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
    boxSizing: 'border-box',
  },
  button: {
    width: '100%',
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
  buttonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
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

