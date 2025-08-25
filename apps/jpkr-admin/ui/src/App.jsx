import React, { useState, useEffect } from 'react';
import { Container, Content, Sidebar, Button, Form, Input } from 'rsuite';
import { useLocation, matchPath, useNavigate, Routes, Route } from 'react-router-dom';
import WordsRegister from './pages/words-register';
import WordsTable from './pages/words-table';

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
      key: 'words-table',
      label: '단어 관리',
      path: '/words-table'
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
            <Route path="/words-table" element={<WordsTable />} />
          </Routes>
        </Content>
      </Container>
    </>
  );
}

export default App;





