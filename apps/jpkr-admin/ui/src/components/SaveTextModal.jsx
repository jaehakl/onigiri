import React, { useState, useEffect } from 'react';
import './SaveTextModal.css';

const SaveTextModal = ({ isOpen, onClose, defaultTextData, onSave, text }) => {
  const [id, setId] = useState('');
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState('');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [audioUrl, setAudioUrl] = useState('');

  useEffect(() => {
    if (defaultTextData) {
      setId(defaultTextData.id);
      setTitle(defaultTextData.title);
      setTags(defaultTextData.tags);
      setYoutubeUrl(defaultTextData.youtube_url);
      setAudioUrl(defaultTextData.audio_url);
    }
  }, [defaultTextData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('제목을 입력해주세요.');
      return;
    }

    const textData = {
      id: id,
      title: title.trim(),
      text: text,
      tags: tags.trim(),
      youtube_url: youtubeUrl.trim(),
      audio_url: audioUrl.trim(),
    };

    onSave(textData);
    
    // 폼 초기화
    setTitle('');
    setTags('');
    setYoutubeUrl('');
    setAudioUrl('');
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>텍스트 저장</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">제목 *</label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="텍스트 제목을 입력하세요"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="tags">태그</label>
            <input
              type="text"
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="쉼표로 구분하여 태그를 입력하세요"
            />
          </div>

          <div className="form-group">
            <label htmlFor="youtubeUrl">YouTube URL</label>
            <input
              type="url"
              id="youtubeUrl"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="audioUrl">오디오 URL</label>
            <input
              type="url"
              id="audioUrl"
              value={audioUrl}
              onChange={(e) => setAudioUrl(e.target.value)}
              placeholder="https://example.com/audio.mp3"
            />
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="cancel-btn">
              취소
            </button>
            {id ? (
              <button type="submit" className="save-btn">
                수정
              </button>
            ) : (
              <button type="submit" className="save-btn">
                저장
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default SaveTextModal;
