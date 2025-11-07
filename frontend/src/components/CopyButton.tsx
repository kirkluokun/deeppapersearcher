/**
 * 复制按钮组件
 * 批量复制选中论文的链接
 */

import React, { useState } from 'react';
import { Paper } from '../services/api';

interface CopyButtonProps {
  papers: Paper[];
  selectedIds: Set<string>;
}

export default function CopyButton({ papers, selectedIds }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (selectedIds.size === 0) {
      alert('请先选择要复制的论文');
      return;
    }

    // 收集选中论文的链接
    const selectedPapers = papers.filter((p) => selectedIds.has(p.arxiv_id));
    const urls = selectedPapers.map((p) => p.url).join('\n');

    try {
      await navigator.clipboard.writeText(urls);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('复制失败:', error);
      alert('复制失败，请手动复制');
    }
  };

  if (selectedIds.size === 0) {
    return null;
  }

  return (
    <div style={styles.container}>
      <button
        onClick={handleCopy}
        style={{
          ...styles.button,
          ...(copied ? styles.buttonCopied : {}),
        }}
      >
        {copied ? '✓ 已复制' : `复制链接 (${selectedIds.size} 篇)`}
      </button>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '1200px',
    margin: '20px auto',
    padding: '0 20px',
    display: 'flex',
    justifyContent: 'flex-end',
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  buttonCopied: {
    backgroundColor: '#218838',
  },
};
