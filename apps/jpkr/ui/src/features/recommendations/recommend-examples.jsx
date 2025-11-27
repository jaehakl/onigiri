import React, { useEffect, useState } from 'react';
import { Button, Loader, Message } from 'rsuite';
import { Reload } from '@rsuite/icons';
import { getExamplesForUser } from '../../api/api';
import ExampleCard from '../../components/ExampleCard';
import './RecommendExamples.css';

const RecommendExamples = () => {
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tagInput, setTagInput] = useState('');
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

  const handleAddTag = () => {
    const trimmed = tagInput.trim();
    if (!trimmed) return;
    if (!selectedTags.includes(trimmed)) {
      setSelectedTags([...selectedTags, trimmed]);
    }
    setTagInput('');
  };

  const handleRemoveTag = (tag) => {
    setSelectedTags(selectedTags.filter((t) => t !== tag));
  };

  return (
    <div className="recommend-examples-page">
      <div className="recommend-examples-header">
        <h2 className="recommend-examples-title">문장 학습</h2>
        <Button
          appearance="ghost"
          onClick={loadExamples}
          loading={loading}
          className="recommend-examples-refresh-btn"
          size="sm"
        >
          <Reload /> 새로고침
        </Button>
      </div>

      <div className="recommend-examples-tags">
        <div className="recommend-examples-tag-input-row">
          <input
            type="text"
            placeholder="태그를 입력하고 Enter"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddTag();
              }
            }}
            className="recommend-examples-tag-input"
          />
          <Button size="sm" onClick={handleAddTag} disabled={!tagInput.trim()}>
            태그 추가
          </Button>
          {selectedTags.length > 0 && (
            <span className="recommend-examples-tag-hint">
              선택: {selectedTags.join(', ')}
            </span>
          )}
        </div>
        <div className="recommend-examples-tag-list">
          {selectedTags.map((tag) => (
            <span key={tag} className="recommend-examples-tag-pill active">
              {tag}
              <button
                onClick={() => handleRemoveTag(tag)}
                className="tag-remove-btn"
                aria-label={`${tag} 삭제`}
              >
                ×
              </button>
            </span>
          ))}
          {selectedTags.length === 0 && (
            <span className="recommend-examples-tag-placeholder">
              태그를 비워두면 전체에서 추천합니다.
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <div className="recommend-examples-loading-container">
          <Loader size="lg" content="불러오는 중" />
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
          추천할 문장이 없습니다.
        </Message>
      ) : (
        <div className="recommend-examples-grid">
          {examples.map((example) => (
            <div key={example.id} className="recommend-examples-card-wrapper">
              <ExampleCard example={example} isMain={false} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecommendExamples;
