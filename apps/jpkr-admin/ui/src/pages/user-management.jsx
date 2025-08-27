import React, { useState, useEffect } from 'react';
import { getAllUsersAdmin, getUserSummaryAdmin } from '../api/api';
import './UserManagement.css';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userSummary, setUserSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMoreUsers, setHasMoreUsers] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const usersPerPage = 20;

  useEffect(() => {
    if (currentPage === 1) {
      fetchUsers(true);
    } else {
      fetchUsers(false);
    }
  }, [currentPage]);

  const fetchUsers = async (isFirstLoad = true) => {
    try {
      if (isFirstLoad) {
        setLoading(true);
      } else {
        setIsLoadingMore(true);
      }
      
      const offset = (currentPage - 1) * usersPerPage;
      const response = await getAllUsersAdmin(usersPerPage, offset);
      
      if (response.data && Array.isArray(response.data)) {
        if (isFirstLoad) {
          setUsers(response.data);
        } else {
          setUsers(prevUsers => [...prevUsers, ...response.data]);
        }
        // 현재 페이지에서 가져온 사용자 수가 페이지당 사용자 수보다 적으면 더 이상 사용자가 없음
        setHasMoreUsers(response.data.length === usersPerPage);
      }
    } catch (err) {
      setError('사용자 목록을 가져오는데 실패했습니다.');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  };

  const handleUserClick = async (userId) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await getUserSummaryAdmin(userId);
      
      if (response.data) {
        setUserSummary(response.data);
        setSelectedUser(users.find(user => user.id === userId));
      }
    } catch (err) {
      setError('사용자 요약 정보를 가져오는데 실패했습니다.');
      console.error('Error fetching user summary:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToList = () => {
    setSelectedUser(null);
    setUserSummary(null);
    setError(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const canGoNext = hasMoreUsers;

  if (selectedUser && userSummary) {
    return (
      <div className="user-management">
        <div className="user-management-header">
          <button className="back-button" onClick={handleBackToList}>
            ← 목록으로 돌아가기
          </button>
          <h1>사용자 상세 정보</h1>
        </div>

        <div className="user-detail-container">
          <div className="user-basic-info">
            <div className="user-avatar">
              {userSummary.display_name ? userSummary.display_name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="user-info">
              <h2>{userSummary.display_name || '이름 없음'}</h2>
              <p className="user-email">{userSummary.email || '이메일 없음'}</p>
              <p className="user-status">
                상태: <span className={userSummary.is_active ? 'active' : 'inactive'}>
                  {userSummary.is_active ? '활성' : '비활성'}
                </span>
              </p>
              <p className="user-created">가입일: {formatDate(userSummary.created_at)}</p>
            </div>
          </div>

          <div className="user-stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📚</div>
              <div className="stat-content">
                <h3>총 단어 수</h3>
                <div className="stat-number">{userSummary.stats.total_words}</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">💬</div>
              <div className="stat-content">
                <h3>총 예문 수</h3>
                <div className="stat-number">{userSummary.stats.total_examples}</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">🖼️</div>
              <div className="stat-content">
                <h3>총 이미지 수</h3>
                <div className="stat-number">{userSummary.stats.total_images}</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">📝</div>
              <div className="stat-content">
                <h3>총 텍스트 수</h3>
                <div className="stat-number">{userSummary.stats.total_texts}</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">⭐</div>
              <div className="stat-content">
                <h3>즐겨찾기 단어</h3>
                <div className="stat-number">{userSummary.stats.favorite_words}</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <h3>활동 점수</h3>
                <div className="stat-number">
                  {userSummary.stats.total_words + userSummary.stats.total_examples + userSummary.stats.total_texts}
                </div>
              </div>
            </div>
          </div>

          <div className="user-activity-chart">
            <h3>학습 진행도</h3>
            <div className="progress-bars">
              <div className="progress-item">
                <label>단어 학습</label>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${Math.min((userSummary.stats.total_words / 100) * 100, 100)}%` }}
                  ></div>
                </div>
                <span className="progress-text">{userSummary.stats.total_words}/100</span>
              </div>

              <div className="progress-item">
                <label>예문 학습</label>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${Math.min((userSummary.stats.total_examples / 50) * 100, 100)}%` }}
                  ></div>
                </div>
                <span className="progress-text">{userSummary.stats.total_examples}/50</span>
              </div>

              <div className="progress-item">
                <label>텍스트 학습</label>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${Math.min((userSummary.stats.total_texts / 20) * 100, 100)}%` }}
                  ></div>
                </div>
                <span className="progress-text">{userSummary.stats.total_texts}/20</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management">
      <div className="user-management-header">
        <h1>사용자 관리</h1>
        <p className="header-description">시스템에 등록된 모든 사용자를 관리합니다.</p>
        {users.length > 0 && (
          <div className="user-count-info">
            <span>총 {users.length}명의 사용자가 등록되어 있습니다.</span>
            {currentPage > 1 && (
              <span className="page-info"> (페이지 {currentPage})</span>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>데이터를 불러오는 중...</p>
        </div>
      ) : (
        <>
          <div className="users-table-container">
            <table className="users-table">
              <thead>
                <tr>
                  <th>사용자 ID</th>
                  <th>이메일</th>
                  <th>표시명</th>
                  <th>상태</th>
                  <th>가입일</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="user-row">
                    <td className="user-id">{user.id.substring(0, 8)}...</td>
                    <td className="user-email">{user.email || 'N/A'}</td>
                    <td className="user-display-name">{user.display_name || 'N/A'}</td>
                    <td className="user-status">
                      <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                        {user.is_active ? '활성' : '비활성'}
                      </span>
                    </td>
                    <td className="user-created">{formatDate(user.created_at)}</td>
                    <td className="user-actions">
                      <button 
                        className="view-button"
                        onClick={() => handleUserClick(user.id)}
                      >
                        상세보기
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {hasMoreUsers && (
            <div className="load-more-container">
              <button 
                className="load-more-button"
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={isLoadingMore}
              >
                {isLoadingMore ? '로딩 중...' : '더 보기'}
              </button>
            </div>
          )}
          
          {currentPage > 1 && (
            <div className="pagination">
              <button 
                className="page-button"
                onClick={() => setCurrentPage(1)}
              >
                처음으로
              </button>
            </div>
          )}

          {users.length === 0 && !loading && (
            <div className="no-users">
              <p>등록된 사용자가 없습니다.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default UserManagement;
