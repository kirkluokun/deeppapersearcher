/**
 * 摘要精炼按钮组件
 * 点击后调用 API 精炼摘要，使其通俗易懂
 */

import React, { useState } from 'react';
import { refineAbstract, Paper } from '../services/api';

interface RefineButtonProps {
  paper: Paper;
  onRefined?: (refinedAbstract: string) => void;  // 精炼完成后的回调
}

export default function RefineButton({ paper, onRefined }: RefineButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRefine = async () => {
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      const response = await refineAbstract({
        arxiv_id: paper.arxiv_id,
        abstract: paper.abstract_zh || paper.abstract,
        title: paper.title,
      });
      
      if (onRefined) {
        onRefined(response.refined_abstract);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '精炼失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <button
        onClick={handleRefine}
        disabled={loading}
        style={{
          ...styles.button,
          ...(loading ? styles.buttonLoading : {}),
        }}
      >
        {loading ? '精炼中...' : '✨ 精炼摘要（通俗易懂）'}
      </button>
      {error && (
        <div style={styles.error}>
          {error}
        </div>
      )}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    marginTop: '10px',
  },
  button: {
    padding: '8px 16px',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  buttonLoading: {
    backgroundColor: '#6c757d',
    cursor: 'not-allowed',
  },
  error: {
    marginTop: '8px',
    padding: '8px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '4px',
    fontSize: '12px',
  },
};

