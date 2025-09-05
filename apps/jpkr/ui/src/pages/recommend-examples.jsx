import React, { useState, useEffect } from 'react';
import { Button, Card, Loader, Message, Panel, Grid, Row, Col } from 'rsuite';
import { getExamplesForUser } from '../api/api';
import ExampleCard from '../components/ExampleCard';
import './RecommendExamples.css';

const RecommendExamples = () => {
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadExamples = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getExamplesForUser();
      setExamples(response.data || []);
    } catch (err) {
      console.error('예시 로드 실패:', err);
      setError('예시를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExamples();
  }, []);

  const renderExampleCard = (example) => (
    <div key={example.id} className="example-card-wrapper">
      <ExampleCard example={example} isMain={false} />
    </div>
  );

  if (loading) {
    return (
      <div className="loading-container">
        <Loader size="lg" content="예시를 불러오는 중..." />
      </div>
    );
  }

  if (error) {
    return (
      <Message type="error" showIcon>
        {error}
        <Button onClick={loadExamples} style={{ marginLeft: 10 }}>
          다시 시도
        </Button>
      </Message>
    );
  }

  return (
    <div className="recommend-examples-page">
      <Panel header="추천 예시" className="page-header">
        <div className="header-actions">
          <Button 
            appearance="primary" 
            onClick={loadExamples}
            loading={loading}
          >
            새로고침
          </Button>
        </div>
      </Panel>

      <div className="examples-content">
        {examples.length === 0 ? (
          <Message type="info" showIcon>
            추천할 예시가 없습니다.
          </Message>
        ) : (
          <>
            <div className="examples-count">
              총 {examples.length}개의 추천 예시
            </div>
            <div className="examples-grid">
              {examples.map(renderExampleCard)}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RecommendExamples;
