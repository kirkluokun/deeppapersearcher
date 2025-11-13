/**
 * 最新论文列表组件
 * 显示最新论文，支持摘要精炼功能
 */

import React, { useState } from 'react';
import { Paper } from '../services/api';
import RefineButton from './RefineButton';

interface LatestPaperListProps {
  papers: Paper[];
  selectedIds: Set<string>;
  onToggleSelect: (arxivId: string) => void;
}

// 单篇论文组件
function LatestPaperItem({ 
  paper, 
  isSelected, 
  onToggleSelect 
}: { 
  paper: Paper;
  isSelected: boolean;
  onToggleSelect: () => void;
}) {
  const [refinedAbstract, setRefinedAbstract] = useState<string | null>(null);

  return (
    <div style={styles.paperItem}>
      <label style={styles.paperCheckbox}>
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onToggleSelect}
          style={styles.checkbox}
        />
        <div style={styles.paperContent}>
          <h3 style={styles.title}>
            {paper.title}
            {paper.title_zh && paper.title_zh !== paper.title && (
              <span style={styles.titleZh}>（{paper.title_zh}）</span>
            )}
          </h3>
          
          {paper.keywords && (
            <div style={styles.keywords}>
              <strong>关键词:</strong> {paper.keywords}
            </div>
          )}
          
          <div style={styles.abstractSection}>
            <p style={styles.abstractLabel}>摘要:</p>
            <div>
              <p style={styles.abstractZh}>
                {paper.abstract_zh || paper.abstract}
              </p>
              {refinedAbstract && (
                <>
                  <div style={styles.divider}></div>
                  <div style={styles.refinedSection}>
                    <p style={styles.refinedLabel}>✨ 精炼摘要:</p>
                    <p style={styles.refinedContent}>{refinedAbstract}</p>
                  </div>
                </>
              )}
              {!refinedAbstract && (
                <RefineButton
                  paper={paper}
                  onRefined={(refined) => setRefinedAbstract(refined)}
                />
              )}
            </div>
          </div>
          
          <div style={styles.meta}>
            <span style={styles.metaItem}>ID: {paper.arxiv_id}</span>
            {paper.published && (
              <span style={styles.metaItem}>发布时间: {paper.published}</span>
            )}
            {paper.authors.length > 0 && (
              <span style={styles.metaItem}>
                作者: {paper.authors.slice(0, 3).join(', ')}
                {paper.authors.length > 3 && ` 等 ${paper.authors.length} 人`}
              </span>
            )}
          </div>
          
          <div style={styles.links}>
            {paper.url && (
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                style={styles.link}
              >
                📄 查看论文页面
              </a>
            )}
            {paper.pdf_url && (
              <a
                href={paper.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                style={styles.link}
              >
                📥 下载 PDF
              </a>
            )}
          </div>
        </div>
      </label>
    </div>
  );
}

export default function LatestPaperList({ 
  papers, 
  selectedIds, 
  onToggleSelect 
}: LatestPaperListProps) {
  return (
    <div style={styles.container}>
      {papers.length === 0 ? (
        <div style={styles.empty}>暂无论文</div>
      ) : (
        <div style={styles.list}>
          {papers.map((paper) => (
            <LatestPaperItem 
              key={paper.arxiv_id} 
              paper={paper}
              isSelected={selectedIds.has(paper.arxiv_id)}
              onToggleSelect={() => onToggleSelect(paper.arxiv_id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  paperItem: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    padding: '20px',
  },
  paperCheckbox: {
    display: 'flex',
    alignItems: 'flex-start',
    cursor: 'pointer',
    gap: '10px',
  },
  checkbox: {
    marginTop: '4px',
    width: '18px',
    height: '18px',
    cursor: 'pointer',
    flexShrink: 0,
  },
  paperContent: {
    flex: 1,
    width: '100%',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '12px',
    color: '#333',
  },
  titleZh: {
    fontSize: '18px',
    fontWeight: 'normal',
    color: '#666',
    marginLeft: '8px',
  },
  keywords: {
    fontSize: '15px',
    color: '#007bff',
    marginBottom: '15px',
    padding: '10px',
    backgroundColor: '#f0f7ff',
    borderRadius: '4px',
  },
  abstractSection: {
    marginBottom: '15px',
  },
  abstractLabel: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#555',
    marginBottom: '8px',
  },
  abstractZh: {
    fontSize: '16px',
    color: '#333',
    lineHeight: '1.8',
    marginBottom: '0',
  },
  meta: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '15px',
    fontSize: '12px',
    color: '#999',
    marginBottom: '15px',
  },
  metaItem: {
    display: 'inline-block',
  },
  empty: {
    textAlign: 'center',
    padding: '40px',
    color: '#999',
    fontSize: '16px',
  },
  links: {
    display: 'flex',
    gap: '15px',
    flexWrap: 'wrap',
  },
  link: {
    color: '#007bff',
    textDecoration: 'none',
    fontSize: '14px',
    padding: '6px 12px',
    border: '1px solid #007bff',
    borderRadius: '4px',
    transition: 'all 0.2s',
    display: 'inline-block',
  },
  divider: {
    height: '1px',
    backgroundColor: '#e0e0e0',
    margin: '15px 0',
  },
  refinedSection: {
    marginTop: '15px',
    padding: '15px',
    backgroundColor: '#e7f3ff',
    borderRadius: '6px',
    borderLeft: '4px solid #007bff',
  },
  refinedLabel: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#0056b3',
    marginBottom: '10px',
  },
  refinedContent: {
    fontSize: '15px',
    color: '#333',
    lineHeight: '1.8',
    marginBottom: '0',
  },
};

