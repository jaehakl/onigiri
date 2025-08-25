import React, { useState, useEffect } from 'react';
import { Container, Content, Sidebar, Button, Form, Input } from 'rsuite';
import { useLocation, matchPath, useNavigate, Routes, Route } from 'react-router-dom';
import WordsRegister from './pages/words-register';
import WordsTable from './pages/words-table';
import WordsSearch from './pages/words-search';
import WordAnalysis from './pages/word-analysis';
import ExamplesRegister from './pages/examples-register';
import ExamplesTable from './pages/examples-table';

import 'rsuite/dist/rsuite.min.css';

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: 'words-register',
      label: '단어 등록',
      path: '/words-register'
    },
    {
      key: 'words-search',
      label: '단어 검색',
      path: '/words-search'
    },
    {
      key: 'words-table',
      label: '단어 관리',
      path: '/words-table'
    },
    {
      key: 'examples-register',
      label: '예문 등록',
      path: '/examples-register'
    },
    {
      key: 'examples-table',
      label: '예문 관리',
      path: '/examples-table'
    },
    {
      key: 'word-analysis',
      label: '단어 분석',
      path: '/word-analysis'
    }
  ];

  const handleMenuSelect = (key) => {
    const menuItem = menuItems.find(item => item.key === key);
    if (menuItem) {
      navigate(menuItem.path);
    }
  };

  const getActiveKey = () => {
    const currentPath = location.pathname;
    const activeItem = menuItems.find(item => 
      currentPath === item.path || currentPath.startsWith(item.path)
    );
    return activeItem ? activeItem.key : 'words-register';
  };

  return (
    <>
      <Container style={{ marginTop: '20px' }}>
        <Sidebar width={250} style={{ background: '#f8f9fa' }}>
          <div style={{ padding: '20px' }}>
            <h3 style={{ margin: '0 0 20px 0', color: '#2c3e50' }}>일본어 관리자</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {menuItems.map(item => (
                <Button
                  key={item.key}
                  appearance={getActiveKey() === item.key ? 'primary' : 'ghost'}
                  block
                  onClick={() => handleMenuSelect(item.key)}
                  style={{ 
                    textAlign: 'left',
                    justifyContent: 'flex-start',
                    padding: '12px 16px'
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </div>
          </div>
        </Sidebar>
        <Content style={{ padding: '0 20px' }}>
          <Routes>
            <Route path="/" element={<WordsRegister />} />
            <Route path="/words-register" element={<WordsRegister />} />
            <Route path="/words-search" element={<WordsSearch />} />
            <Route path="/words-table" element={<WordsTable />} />
            <Route path="/examples-register" element={<ExamplesRegister />} />
            <Route path="/examples-table" element={<ExamplesTable />} />
            <Route path="/word-analysis" element={<WordAnalysis />} />
          </Routes>
        </Content>
      </Container>
    </>
  );
}

export default App;





