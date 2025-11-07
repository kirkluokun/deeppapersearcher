/**
 * 搜索表单组件
 */

import React, { useState } from 'react';

interface SearchFormProps {
  onSearch: (keywords: string, question: string) => void;
  loading: boolean;
}

export default function SearchForm({ onSearch, loading }: SearchFormProps) {
  const [keywords, setKeywords] = useState('');
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (keywords.trim() && question.trim()) {
      onSearch(keywords.trim(), question.trim());
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
