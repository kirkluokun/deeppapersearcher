/**
 * 主应用组件
 * 配置路由和导航
 */

import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import MultiEngineSearch from './pages/MultiEngineSearch';
import ArxivSearch from './pages/ArxivSearch';

function App() {
  return (
    <BrowserRouter>
      <div style={styles.app}>
        <nav style={styles.nav}>
          <div style={styles.navContainer}>
            <NavLink
              to="/"
              style={({ isActive }) => ({
                ...styles.navLink,
                ...(isActive ? styles.navLinkActive : {}),
              })}
            >
              多引擎搜索
            </NavLink>
            <NavLink
              to="/arxiv"
              style={({ isActive }) => ({
                ...styles.navLink,
                ...(isActive ? styles.navLinkActive : {}),
              })}
            >
              arXiv 专用搜索
            </NavLink>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<MultiEngineSearch />} />
          <Route path="/arxiv" element={<ArxivSearch />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  nav: {
    backgroundColor: '#fff',
    borderBottom: '1px solid #ddd',
    padding: '0 20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  },
  navContainer: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    gap: '20px',
    padding: '15px 0',
  },
  navLink: {
    padding: '8px 16px',
    textDecoration: 'none',
    color: '#666',
    fontSize: '16px',
    fontWeight: '500',
    borderRadius: '4px',
    transition: 'all 0.2s',
  },
  navLinkActive: {
    color: '#007bff',
    backgroundColor: '#e7f3ff',
    fontWeight: '600',
  },
};

export default App;
