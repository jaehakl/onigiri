import { useEffect, useState } from "react";
import { API_URL, fetchMe, startGoogleLogin, logout, getUserSummaryUser } from "../api/api";
import './AuthUserProfile.css';
import { useNavigate } from "react-router-dom";

function AuthUserProfile({onFetchMe=null}) {
  const [me, setMe] = useState(null);
  const [userSummary, setUserSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      const data = await fetchMe();
      setMe(data);
      setLoading(false);
      if (onFetchMe) {
        onFetchMe(data);
      }      
      // 사용자 정보가 있으면 상세 정보도 가져오기
      if (data) {
        fetchUserSummary();
      }
    })();
  }, []);

  const fetchUserSummary = async () => {
    try {
      setProfileLoading(true);
      setProfileError(null);
      
      const response = await getUserSummaryUser();
      
      if (response.data) {
        setUserSummary(response.data);
      }
    } catch (err) {
      setProfileError('사용자 정보를 가져오는데 실패했습니다.');
      console.error('Error fetching user summary:', err);
    } finally {
      setProfileLoading(false);
    }
  };

  if (loading) return <div className="sidebar-loading">Loading…</div>;

  return (
    <div className="sidebar-user-profile">
      {!me ? (
        <div className="login-section">
          <p className="login-text">로그인이 필요합니다</p>
          <button className="login-button" onClick={startGoogleLogin}>
            Google로 로그인
          </button>
        </div>
      ) : (
        <>
          {/* 컴팩트한 사용자 프로필 */}
          <div className="user-profile-compact">
            <div className="user-header">
              <div className="user-avatar-small">
                {me.display_name ? me.display_name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="user-details">
                <h4 className="user-name">{me.display_name || '이름 없음'}</h4>
                <p className="user-email-compact">{me.email || '이메일 없음'}</p>
              </div>
            </div>

            {/* 간단한 통계 */}
            {!profileLoading && !profileError && userSummary && (
              <div className="stats-compact">
                <div className="stat-compact">
                  <span className="stat-icon-small">📚</span>
                  <span className="stat-number-small">{userSummary.stats.total_words}</span>
                </div>
                <div className="stat-compact">
                  <span className="stat-icon-small">💬</span>
                  <span className="stat-number-small">{userSummary.stats.total_examples}</span>
                </div>
                <div className="stat-compact">
                  <span className="stat-icon-small">📝</span>
                  <span className="stat-number-small">{userSummary.stats.total_texts}</span>
                </div>
                <div className="stat-compact">
                  <span className="stat-icon-small">⭐</span>
                  <span className="stat-number-small">{userSummary.stats.favorite_words}</span>
                </div>
              </div>
            )}

            {/* 액션 버튼들 */}
            <div className="profile-actions">
              <button 
                className="action-button primary"
                onClick={() => navigate(`/user-detail/me`)}
              >
                프로필 수정
              </button>
              <button 
                className="action-button secondary"
                onClick={async () => { 
                  await logout(); 
                  setMe(null); 
                  setUserSummary(null); 
                }}
              >
                로그아웃
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default AuthUserProfile;
