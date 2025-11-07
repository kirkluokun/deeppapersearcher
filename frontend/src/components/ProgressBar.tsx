/**
 * 进度条组件
 */

import React from 'react';

interface ProgressBarProps {
  progress: number;  // 0-100
  message: string;
  current?: number;
  total?: number;
  paperTitle?: string;
}

export default function ProgressBar({ progress, message, current, total, paperTitle }: ProgressBarProps) {
  // 确保进度值在有效范围内
  const validProgress = Math.max(0, Math.min(100, progress || 0));
  
  return (
    <div style={styles.container}>
      <div style={styles.message}>{message}</div>
      {paperTitle && (
        <div style={styles.paperTitle}>正在处理: {paperTitle}</div>
      )}
      {current !== undefined && total !== undefined && (
        <div style={styles.count}>
          {current} / {total}
        </div>
      )}
      <div style={styles.progressBar}>
        <div
          style={{
            ...styles.progressFill,
            width: `${validProgress}%`,
          }}
        />
      </div>
      <div style={styles.percentage}>{validProgress}%</div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '800px',
    margin: '20px auto',
    padding: '25px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  message: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '15px',
    textAlign: 'center',
  },
  paperTitle: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '10px',
    textAlign: 'center',
  },
  count: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '15px',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  progressBar: {
    width: '100%',
    height: '30px',
    backgroundColor: '#e0e0e0',
    borderRadius: '15px',
    overflow: 'hidden',
    marginBottom: '10px',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007bff',
    transition: 'width 0.3s ease',
    borderRadius: '15px',
  },
  percentage: {
    fontSize: '16px',
    color: '#666',
    textAlign: 'center',
    fontWeight: 'bold',
  },
};

