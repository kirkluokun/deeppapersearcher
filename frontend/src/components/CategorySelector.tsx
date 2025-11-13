/**
 * arXiv 分类选择组件
 * 支持单选模式，显示所有8个主要分类及其中文名称
 */

import React from 'react';

// arXiv 分类定义（与后端保持一致）
export const ARXIV_CATEGORIES: Record<string, string> = {
  "physics": "物理学",
  "math": "数学",
  "cs": "计算机科学",
  "q-bio": "定量生物学",
  "q-fin": "定量金融",
  "stat": "统计学",
  "eess": "电气工程与系统科学",
  "econ": "经济学",
};

interface CategorySelectorProps {
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
  disabled?: boolean;
}

export default function CategorySelector({
  selectedCategory,
  onCategoryChange,
  disabled = false,
}: CategorySelectorProps) {
  const handleCategoryChange = (category: string) => {
    // 如果点击已选中的分类，则取消选择（设为 null）
    if (selectedCategory === category) {
      onCategoryChange(null);
    } else {
      onCategoryChange(category);
    }
  };

  return (
    <div style={styles.container}>
      <label style={styles.label}>选择 arXiv 分类:</label>
      <div style={styles.categoryGrid}>
        {Object.entries(ARXIV_CATEGORIES).map(([code, name]) => {
          const isSelected = selectedCategory === code;
          return (
            <label
              key={code}
              style={{
                ...styles.categoryItem,
                ...(isSelected ? styles.categoryItemSelected : styles.categoryItemUnselected),
                ...(disabled ? styles.categoryItemDisabled : {}),
              }}
            >
              <input
                type="radio"
                name="arxiv-category"
                value={code}
                checked={isSelected}
                onChange={() => handleCategoryChange(code)}
                disabled={disabled}
                style={styles.radio}
              />
              <span style={styles.categoryName}>{name}</span>
              <span style={styles.categoryCode}>({code})</span>
            </label>
          );
        })}
      </div>
      {selectedCategory && (
        <div style={styles.selectedInfo}>
          已选择: <strong>{ARXIV_CATEGORIES[selectedCategory]}</strong> ({selectedCategory})
        </div>
      )}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    marginBottom: '12px',
    fontWeight: 'bold',
    color: '#333',
    fontSize: '14px',
  },
  categoryGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '10px',
    marginBottom: '10px',
  },
  categoryItem: {
    display: 'flex',
    alignItems: 'center',
    padding: '10px 12px',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  categoryItemUnselected: {
    border: '2px solid #e0e0e0',
    backgroundColor: '#fff',
  },
  categoryItemSelected: {
    border: '2px solid #000',
    backgroundColor: '#fff',
  },
  categoryItemDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  radio: {
    marginRight: '8px',
    width: '18px',
    height: '18px',
    cursor: 'pointer',
  },
  categoryName: {
    flex: 1,
    fontSize: '14px',
    color: '#333',
    fontWeight: '500',
  },
  categoryCode: {
    fontSize: '12px',
    color: '#666',
    marginLeft: '8px',
  },
  selectedInfo: {
    marginTop: '8px',
    padding: '8px 12px',
    backgroundColor: '#e7f3ff',
    borderRadius: '4px',
    fontSize: '14px',
    color: '#0056b3',
  },
};

