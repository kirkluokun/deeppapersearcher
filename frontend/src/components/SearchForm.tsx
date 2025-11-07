/**
 * 搜索表单组件
 */

import React, { useState } from 'react';

interface SearchFormProps {
  onSearch: (keywords: string, question: string, engines: string[]) => void;
  loading: boolean;
}

export default function SearchForm({ onSearch, loading }: SearchFormProps) {
  const [keywords, setKeywords] = useState('');
  const [question, setQuestion] = useState('');
  const [engines, setEngines] = useState<string[]>(['arxiv']);  // 默认选择 arxiv

  const handleEngineChange = (engine: string) => {
    setEngines(prev => {
      if (prev.includes(engine)) {
        // 至少保留一个引擎
        if (prev.length > 1) {
          return prev.filter(e => e !== engine);
        }
        return prev;
      } else {
        return [...prev, engine];
      }
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (keywords.trim() && question.trim() && engines.length > 0) {
      onSearch(keywords.trim(), question.trim(), engines);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
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
      
      <div style={styles.inputGroup}>
        <label style={styles.label}>选择搜索引擎:</label>
        <div style={styles.checkboxGroup}>
          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={engines.includes('arxiv')}
              onChange={() => handleEngineChange('arxiv')}
              disabled={loading}
              style={styles.checkbox}
            />
            arXiv
          </label>
          <label style={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={engines.includes('semantic_scholar')}
              onChange={() => handleEngineChange('semantic_scholar')}
              disabled={loading}
              style={styles.checkbox}
            />
            Semantic Scholar
          </label>
        </div>
      </div>
      
      <button
        type="submit"
        disabled={loading || !keywords.trim() || !question.trim() || engines.length === 0}
        style={{
          ...styles.button,
          ...(loading || !keywords.trim() || !question.trim() || engines.length === 0 ? styles.buttonDisabled : {}),
        }}
      >
        {loading ? '搜索中...' : '搜索论文'}
      </button>
    </form>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
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
  },
  textarea: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
  },
  checkboxGroup: {
    display: 'flex',
    gap: '20px',
    flexWrap: 'wrap',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer',
    fontSize: '14px',
  },
  checkbox: {
    marginRight: '8px',
    width: '18px',
    height: '18px',
    cursor: 'pointer',
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
};
