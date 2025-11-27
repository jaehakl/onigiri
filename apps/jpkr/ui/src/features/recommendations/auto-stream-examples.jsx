import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Button, Loader, Message, Tag } from 'rsuite';
import { Reload, PlayOutline, PauseOutline } from '@rsuite/icons';
import ExampleCard from '../../components/ExampleCard';
import { getExamplesForUser } from '../../api/api';
import './AutoStreamExamples.css';

const playableOnly = (data) => (data || []).filter((item) => item?.audio_url);
const MAX_QUEUE = 100;

const AutoStreamExamples = () => {
  const [playQueue, setPlayQueue] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [tagInput, setTagInput] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [status, setStatus] = useState('');
  const audioRef = useRef(null);

  const fetchBatch = useCallback(
    async (options = { append: false }) => {
      const append = options.append;
      append ? setLoadingMore(true) : setLoading(true);
      setError(null);
      try {
        const response = await getExamplesForUser(selectedTags);
        const data = response?.data || [];
        const playable = playableOnly(data);

        if (append) {
          let trimmedCount = 0;
          setPlayQueue((prev) => {
            const combined = [...prev, ...playable];
            trimmedCount = Math.max(0, combined.length - MAX_QUEUE);
            return trimmedCount ? combined.slice(trimmedCount) : combined;
          });
          setCurrentIndex((prev) => {
            if (prev === null && playable.length > 0) return 0;
            if (prev === null) return null;
            return Math.max(0, prev - trimmedCount);
          });
        } else {
          const trimmed = playable.length > MAX_QUEUE ? playable.slice(-MAX_QUEUE) : playable;
          setPlayQueue(trimmed);
          setCurrentIndex(playable.length ? 0 : null);
          setIsPlaying(false);
        }

        if (!playable.length) {
          setStatus('No audio in this batch. Please refresh.');
        } else {
          setStatus('');
        }
      } catch (err) {
        console.error('Failed to load examples', err);
        setError('Failed to load examples.');
      } finally {
        append ? setLoadingMore(false) : setLoading(false);
      }
    },
    [selectedTags]
  );

  useEffect(() => {
    fetchBatch({ append: false });
  }, [selectedTags, fetchBatch]);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const advanceToNext = useCallback(() => {
    setCurrentIndex((prev) => {
      if (prev === null) return null;
      const next = prev + 1;
      if (next >= playQueue.length) {
        setIsPlaying(false);
        return prev;
      }
      return next;
    });
  }, [playQueue.length]);

  useEffect(() => {
    if (!isPlaying) return;
    const current = currentIndex !== null ? playQueue[currentIndex] : null;
    if (!current) {
      setIsPlaying(false);
      return;
    }

    if (audioRef.current) {
      audioRef.current.pause();
    }

    const audio = new Audio(current.audio_url);
    audioRef.current = audio;

    const handleAutoNext = () => {
      advanceToNext();
    };

    audio.addEventListener('ended', handleAutoNext);
    audio.addEventListener('error', handleAutoNext);

    audio
      .play()
      .then(() => setStatus(''))
      .catch((err) => {
        console.error('Audio playback failed', err);
        setStatus('Playback failed: moving to next example.');
        advanceToNext();
      });

    return () => {
      audio.pause();
      audio.removeEventListener('ended', handleAutoNext);
      audio.removeEventListener('error', handleAutoNext);
    };
  }, [advanceToNext, currentIndex, isPlaying, playQueue]);

  useEffect(() => {
    if (!isPlaying) return;
    if (
      playQueue.length &&
      currentIndex !== null &&
      playQueue.length - currentIndex <= 2 &&
      !loadingMore
    ) {
      fetchBatch({ append: true });
    }
  }, [currentIndex, fetchBatch, isPlaying, loadingMore, playQueue.length]);

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

  const startPlayback = () => {
    if (!playQueue.length) {
      setStatus('No playable audio yet.');
      return;
    }
    setIsPlaying(true);
    if (currentIndex === null && playQueue.length) {
      setCurrentIndex(0);
    }
  };

  const pausePlayback = () => {
    setIsPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
    }
  };

  const handleNext = () => {
    advanceToNext();
  };

  const handlePrev = () => {
    setCurrentIndex((prev) => {
      if (prev === null) return null;
      return Math.max(0, prev - 1);
    });
  };

  const currentExample =
    currentIndex !== null && playQueue[currentIndex] ? playQueue[currentIndex] : null;

  return (
    <div className="auto-stream-page">
      <div className="auto-stream-header">
        <h2 className="auto-stream-title">문장 스트리밍</h2>
        <div className="auto-stream-actions">
          <Button appearance="primary" onClick={isPlaying ? pausePlayback : startPlayback}>
            {isPlaying ? <PauseOutline /> : <PlayOutline />} {isPlaying ? '일시정지' : '재생'}
          </Button>
          <Button appearance="ghost" onClick={handlePrev} disabled={currentIndex === null || currentIndex === 0}>
            이전
          </Button>
          <Button appearance="ghost" onClick={handleNext} disabled={currentIndex === null}>
            다음
          </Button>
          <span className="auto-stream-status">
            대기열 {playQueue.length}
            {loadingMore && <Loader size="xs" content="+" className="inline-loader" />}
          </span>
          <Button appearance="ghost" onClick={() => fetchBatch({ append: false })} loading={loading}>
            <Reload /> 새로고침
          </Button>
        </div>
      </div>

      <div className="auto-stream-tags">
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
          className="auto-stream-tag-input"
        />
        <Button size="sm" onClick={handleAddTag} disabled={!tagInput.trim()}>
          태그 추가
        </Button>
        <div className="auto-stream-tag-list">
          {selectedTags.map((tag) => (
            <Tag key={tag} closable onClose={() => handleRemoveTag(tag)}>
              {tag}
            </Tag>
          ))}
          {selectedTags.length === 0 && <span className="auto-stream-tag-placeholder">전체 태그 포함</span>}
        </div>
      </div>

      {error && (
        <Message type="error" showIcon>
          {error}
        </Message>
      )}

      {loading ? (
        <div className="centered">
          <Loader size="lg" content="불러오는 중" />
        </div>
      ) : currentExample ? (
          <ExampleCard example={currentExample} isMain={false} />
      ) : (
        <div className="centered">재생할 오디오가 없습니다.</div>
      )}
      {status && <div className="player-hint">{status}</div>}
    </div>
  );
};

export default AutoStreamExamples;
