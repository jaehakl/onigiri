import React, { useEffect, useState } from 'react';
import { Button, Loader, Message, Panel } from 'rsuite';
import { Reload } from '@rsuite/icons';
import { getExamplesForUser } from '../../api/api';
import ExampleCard from '../../components/ExampleCard';
import './RecommendExamples.css';

const TAG_OPTIONS = [
  '건강',
  '취미',
  '여행',
  '음식',
  '비즈니스',
  '감정',
  '학교',
  '가족',
  '쇼핑',
  '기타',
];

const RecommendExamples = () => {
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTags, setSelectedTags] = useState([]);

  const loadExamples = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getExamplesForUser(selectedTags);
      setExamples(response.data || []);
    } catch (err) {
      console.error('문장 로드 실패:', err);
      setError('문장을 불러오는 데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExamples();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTags]);

  const toggleTag = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const renderExampleCard = (example) => (
    <div key={example.id} className="recommend-examples-card-wrapper">
      <ExampleCard example={example} isMain={false} />
    </div>
  );

  return (
    <div className="recommend-examples-page">
      <Panel
        header={
          <div className="recommend-examples-header-content">
            <span className="recommend-examples-header-title">문장 학습</span>
            <Button
              appearance="ghost"
              onClick={loadExamples}
              loading={loading}
              className="recommend-examples-refresh-btn"
              size="sm"
            >
              <Reload />
            </Button>
          </div>
        }
        className="recommend-examples-page-header"
      />

      <div className="recommend-examples-tags">
        <div className="recommend-examples-tag-list">
          {TAG_OPTIONS.map((tag) => {
            const active = selectedTags.includes(tag);
            return (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={`recommend-examples-tag-pill ${active ? 'active' : ''}`}
                aria-pressed={active}
              >
                {tag}
              </button>
            );
          })}
          <span className="recommend-examples-tag-hint">
            원하는 태그를 선택/해제하면 자동으로 추천이 갱신됩니다.
          </span>
        </div>
      </div>

      {loading ? (
        <div className="recommend-examples-loading-container">
          <Loader size="lg" content="문장을 불러오는 중.." />
        </div>
      ) : error ? (
        <Message type="error" showIcon>
          {error}
          <Button onClick={loadExamples} style={{ marginLeft: 10 }}>
            다시 시도
          </Button>
        </Message>
      ) : examples.length === 0 ? (
        <Message type="info" showIcon>
          추천된 문장이 없습니다.
        </Message>
      ) : (
        <div className="recommend-examples-grid">
          {examples.map(renderExampleCard)}
        </div>
      )}
    </div>
  );
};

export default RecommendExamples;
