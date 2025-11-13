/**
 * 论文列表组件
 * 显示论文标题和摘要，每行带复选框
 */

import React, { useState } from 'react';
import { Paper } from '../services/api';

interface PaperListProps {
  papers: Paper[];
  selectedIds: Set<string>;
  onToggleSelect: (arxivId: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
}

// 单篇论文组件
function PaperItem({ 
  paper, 
  isSelected, 
  onToggleSelect 
}: { 
  paper: Paper; 
  isSelected: boolean; 
  onToggleSelect: () => void;
}) {
  const [showEnglish, setShowEnglish] = useState(false);
  const hasEnglish = paper.abstract && paper.abstract_zh && paper.abstract !== paper.abstract_zh;
  
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
          
          {paper.relevance_summary && (
            <div style={styles.relevanceSummary}>
              <strong>相关性评估:</strong> {paper.relevance_summary}
            </div>
          )}
          
          {paper.keywords && (
            <div style={styles.keywords}>
              <strong>关键词:</strong> {paper.keywords}
            </div>
          )}
          
          <div style={styles.abstractSection}>
            <p style={styles.abstractLabel}>摘要:</p>
            {paper.abstract && paper.abstract !== "(Semantic Scholar 数据源中未提供摘要)" ? (
              <p style={styles.abstractZh}>
                {paper.abstract_zh || paper.abstract}
              </p>
            ) : (
              <p style={styles.noAbstract}>
                (Semantic Scholar 数据源中未提供摘要)
              </p>
            )}
          </div>
          
          {hasEnglish && (
            <div style={styles.abstractSection}>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowEnglish(!showEnglish);
                }}
                style={styles.toggleButton}
              >
                {showEnglish ? '▼' : '▶'} 原文摘要（{paper.abstract.length > 100 ? '点击展开' : '点击查看'}）
              </button>
              {showEnglish && (
                <div style={styles.abstractEnContainer}>
                  <p style={styles.abstractEn}>{paper.abstract}</p>
                </div>
              )}
            </div>
          )}
          
          <div style={styles.meta}>
            <span style={styles.metaItem}>ID: {paper.arxiv_id}</span>
            {paper.published && (
              <span style={styles.metaItem}>发布时间: {paper.published}</span>
            )}
            {paper.authors.length > 0 && (
              <span style={styles.metaItem}>
                作者: {paper.authors.join(', ')}
              </span>
            )}
            {paper.source && (
              <span style={styles.metaItem}>
                来源: {
                  paper.source === 'arxiv' ? 'arXiv' :
                  paper.source === 'semantic_scholar' ? 'Semantic Scholar' :
                  paper.source === 'pubmed' ? 'PubMed' :
                  paper.source
                }
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
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#007bff';
                  e.currentTarget.style.color = '#fff';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = '#007bff';
                }}
                onClick={(e) => e.stopPropagation()}
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
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#007bff';
                  e.currentTarget.style.color = '#fff';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = '#007bff';
                }}
                onClick={(e) => e.stopPropagation()}
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

export default function PaperList({
  papers,
  selectedIds,
  onToggleSelect,
  onSelectAll,
  onDeselectAll,
}: PaperListProps) {
  const allSelected = papers.length > 0 && papers.every((p) => selectedIds.has(p.arxiv_id));
  const someSelected = papers.some((p) => selectedIds.has(p.arxiv_id));

  return (
    <div style={styles.container}>
      {papers.length === 0 ? (
        <div style={styles.empty}>暂无论文</div>
      ) : (
        <>
          <div style={styles.header}>
            <div style={styles.headerLeft}>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(input) => {
                    if (input) input.indeterminate = someSelected && !allSelected;
                  }}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onSelectAll();
                    } else {
                      onDeselectAll();
                    }
                  }}
                  style={styles.checkbox}
                />
                全选
              </label>
              <span style={styles.count}>
                已选择 {selectedIds.size} / {papers.length} 篇
              </span>
            </div>
          </div>

          <div style={styles.list}>
            {papers.map((paper) => (
              <PaperItem
                key={paper.arxiv_id}
                paper={paper}
                isSelected={selectedIds.has(paper.arxiv_id)}
                onToggleSelect={() => onToggleSelect(paper.arxiv_id)}
              />
            ))}
          </div>
        </>
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    padding: '15px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  checkbox: {
    marginRight: '8px',
    width: '18px',
    height: '18px',
    cursor: 'pointer',
  },
  count: {
    color: '#666',
    fontSize: '14px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  paperItem: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  paperCheckbox: {
    display: 'flex',
    padding: '15px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  paperCheckboxHover: {
    backgroundColor: '#f5f5f5',
  },
  paperContent: {
    flex: 1,
    marginLeft: '10px',
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
  relevanceSummary: {
    fontSize: '16px',
    color: '#28a745',
    marginBottom: '12px',
    padding: '10px',
    backgroundColor: '#f0fff4',
    borderRadius: '4px',
    borderLeft: '4px solid #28a745',
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
  toggleButton: {
    fontSize: '14px',
    color: '#666',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: '5px 0',
    marginBottom: '8px',
    textAlign: 'left',
  },
  abstractEnContainer: {
    marginTop: '8px',
    padding: '12px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
    borderLeft: '3px solid #ddd',
  },
  abstractEn: {
    fontSize: '15px',
    color: '#666',
    lineHeight: '1.6',
    marginBottom: '0',
    fontStyle: 'italic',
  },
  meta: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '15px',
    fontSize: '12px',
    color: '#999',
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
  noAbstract: {
    fontSize: '14px',
    color: '#999',
    fontStyle: 'italic',
    marginBottom: '0',
  },
  links: {
    display: 'flex',
    gap: '15px',
    marginTop: '15px',
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
};
