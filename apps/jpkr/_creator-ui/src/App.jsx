import React, { useState, useEffect } from 'react';
import { Container, Content, Sidebar, Button, Form, Input } from 'rsuite';
import { useLocation, matchPath, useNavigate, Routes, Route } from 'react-router-dom';

// Admin Pages
import DuplicatedWords from './pages/admin/duplicated-words'; 
import FilterWords from './pages/admin/filter-words';
import FilterExamples from './pages/admin/filter-examples';

// Test Pages
import { useUser } from './contexts/UserContext';
import './App.css';
import 'rsuite/dist/rsuite.min.css';

function App() {
  const { user } = useUser();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const menuItems = [
    {
      key: 'filter-words',
      label: '단어 목록',
      path: '/'
    },
    {
      key: 'filter-examples',
      label: '예문 목록',
      path: '/filter-examples'
    },
    {
      key: 'duplicated-words',
      label: '중복 단어 찾기',
      path: '/duplicated-words'
    }
  ];
  

  const handleMenuSelect = (key) => {
    const menuItem = menuItems.find(item => item.key === key);
    if (menuItem) {
      navigate(menuItem.path);
      setIsMobileMenuOpen(false); // 모바일 메뉴 선택 시 닫기
    }
  };

  const getActiveKey = () => {
    const currentPath = location.pathname;
    const activeItem = menuItems.find(item => 
      item.path !== '/' && (currentPath === item.path || currentPath.startsWith(item.path))
    );
    return activeItem ? activeItem.key : 'duplicated-words';
  };

  const renderMenuButtons = () => (
    <div className="menu-container">
      {menuItems.map(item => (
        <Button
          key={item.key}
          appearance={getActiveKey() === item.key ? 'primary' : 'ghost'}
          block
          onClick={() => handleMenuSelect(item.key)}
          className="menu-button"
        >
          {item.label}
        </Button>
      ))}


    </div>
  );

  return (
    <>
      {/* 모바일 헤더 */}
      <div className="mobile">
        <div className="mobile-header">
          <img 
            src="/onigiri.jpg" 
            alt="Onigiri" 
            className="mobile-logo" 
            onClick={() => navigate('/')}
          />
          <button 
            className="mobile-menu-toggle"
            onClick={() => setIsMobileMenuOpen(true)}
          >
            ☰
          </button>
        </div>

        {/* 모바일 메뉴 오버레이 */}
        <div 
          className={`mobile-menu-overlay ${isMobileMenuOpen ? 'open' : ''}`}
          onClick={() => setIsMobileMenuOpen(false)}
        />

        {/* 모바일 메뉴 패널 */}
        <div className={`mobile-menu-panel ${isMobileMenuOpen ? 'open' : ''}`}>
          <div className="mobile-menu-header">
            <img 
              src="/onigiri.jpg" 
              alt="Onigiri" 
              className="mobile-logo" 
              onClick={() => navigate('/')}
            />
            <button 
              className="mobile-menu-close"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              ✕
            </button>
          </div>
          <div className="sidebar-content">
            {renderMenuButtons()}
          </div>
        </div>
        </div>

      <Container className="app-container">
        <Sidebar className="sidebar">
          <div className="sidebar-content">
            <img 
              src="/onigiri.jpg" 
              alt="Onigiri" 
              className="logo-image" 
              onClick={() => navigate('/')}
            />
            {renderMenuButtons()}
          </div>
        </Sidebar>
        <Content className="content-area">
          <Routes>
            <Route path="/" element={<FilterWords />} />
            <Route path="/filter-examples" element={<FilterExamples />} />
            <Route path="/duplicated-words" element={<DuplicatedWords />} />
          </Routes>
        </Content>
      </Container>
    </>
  );
}

export default App;





