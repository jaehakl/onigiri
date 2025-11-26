import React, { useState, useEffect } from 'react';
import { to_hiragana } from '../service/hangul-to-hiragana';
import './WordInputModal.css';
import { useUser } from '../contexts/UserContext';

const WordInputModal = ({ word, isOpen, onClose, onSubmit, onDelete }) => {
  const { user } = useUser();
  const [wordForm, setWordForm] = useState({
    lemma_id: '',
    lemma: '',
    jp_pron: '',
    kr_pron: '',
    kr_mean: '',
    level: 'N1',
    tags: '',
    reading_mastered: false,
    reading: 0,
    listening: 0,
    speaking: 0,
  });
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [fileTags, setFileTags] = useState([]);

  // word prop이 변경될 때마다 폼 데이터 초기화
  useEffect(() => {
    if (word) {
      const formData = {
        lemma_id: word.lemma_id || '',
        lemma: word.lemma || '',
        jp_pron: word.jp_pron || '',
        kr_pron: word.kr_pron || '',
        kr_mean: word.kr_mean || '',
        level: word.level || 'N1',
        reading_mastered: false,
        reading: 0,
        listening: 0,
        speaking: 0,
      };
      if (word.user_word_skills) {
        word.user_word_skills.forEach(skill => {
          if (skill.reading > 80) {
            formData.reading_mastered = true;
          }
          formData.reading = skill.reading || 0;
          formData.listening = skill.listening || 0;
          formData.speaking = skill.speaking || 0;
        });
      }
      setWordForm(formData);
    }
  }, [word]);

  // 폼 입력 처리
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    if (name === 'kr_pron') {
      const kana = to_hiragana(value);
      setWordForm(prev => ({
        ...prev,
        'jp_pron': kana,
        'kr_pron': value
      }));
    } else if (name === 'reading_mastered') {
      setWordForm(prev => ({
        ...prev,
        [name]: !prev.reading_mastered
      }));
    } else if (['reading', 'listening', 'speaking'].includes(name)) {
      const parsed = parseInt(value || '0', 10);
      const numeric = Math.max(0, Math.min(100, Number.isNaN(parsed) ? 0 : parsed));
      setWordForm(prev => ({
        ...prev,
        [name]: numeric
      }));
    } else {
      setWordForm(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  // 파일 선택 처리
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
    
    // 파일별로 태그 초기화
    const initialTags = files.map(file => ({
      lemma_id: wordForm.lemma_id,
      lemma: wordForm.lemma,
    }));
    setFileTags(initialTags);
  };

  // 파일 태그 변경 처리
  const handleFileTagChange = (index, value) => {
    const newFileTags = [...fileTags];
    newFileTags[index] = { ...newFileTags[index], lemma_id: wordForm.lemma_id, lemma: wordForm.lemma };
    setFileTags(newFileTags);
  };

  // 폼 제출 처리
  const handleSubmit = () => {
    if (!wordForm.lemma.trim()) {
      alert('단어를 입력해주세요.');
      return;
    }

    const payload = {
      ...wordForm,
      reading_mastered: wordForm.reading_mastered || wordForm.reading >= 80,
    };

    // FormData 생성
    const fd = new FormData();
    fd.append("data_json", JSON.stringify([payload]));
    
    // 파일 메타데이터 추가
    const fileMetaData = selectedFiles.map((file, index) => ({
      lemma_id: wordForm.lemma_id,
      lemma: wordForm.lemma,
      tags: fileTags[index]?.tags || wordForm.tags
    }));
    fd.append("file_meta_json", JSON.stringify(fileMetaData));
    
    // 파일들 추가
    selectedFiles.forEach(file => {
      fd.append("files", file);
    });

    onSubmit(fd);
    handleClose();
  };

  // 삭제 처리
  const handleDelete = () => {
    if (window.confirm('정말로 이 단어를 삭제하시겠습니까?')) {
      onDelete(word.word_id);
      handleClose();
    }
  };

  // 모달 닫기
  const handleClose = () => {
    setWordForm({
      lemma_id: '',
      lemma: '',
      jp_pron: '',
      kr_pron: '',
      kr_mean: '',
      level: 'N1',
      tags: '',
      reading_mastered: false,
      reading: 0,
      listening: 0,
      speaking: 0,
    });
    setSelectedFiles([]);
    setFileTags([]);
    onClose();
  };

  if (!isOpen) return null;

  return (    
    <div className="word-input-modal-overlay">
      <div className="word-input-modal-content">
        <div className="word-input-modal-body">
          <div className="word-input-modal-form-row">
            <div className="word-input-modal-form-group">
              <h2 className="word-input-modal-word">{wordForm.lemma}</h2>
            </div>
            <div className="word-input-modal-form-group">
              <label>일본어 발음:</label>
              <input
                type="text"
                name="jp_pron"
                value={wordForm.jp_pron}
                onChange={handleFormChange}
                placeholder="일본어 발음을 입력하세요"
              />
            </div>
          </div>
          <div className="word-input-modal-form-row">
          <div className="word-input-modal-form-group">
             <label>한국어 뜻:</label>
              <input
                type="text"
                name="kr_mean"
                value={wordForm.kr_mean}
                onChange={handleFormChange}
                placeholder="한국어 뜻을 입력하세요"
              />
            </div>

            <div className="word-input-modal-form-group">
              <label>한국어 발음:</label>
              <input
                type="text"
                name="kr_pron"
                value={wordForm.kr_pron}
                onChange={handleFormChange}
                placeholder="한국어 발음을 입력하세요"
              />
            </div>
          </div>
          <div className="word-input-modal-form-row">
            <div className="word-input-modal-form-group">
              <label>Reading</label>
              <input
                type="number"
                name="reading"
                min="0"
                max="100"
                value={wordForm.reading}
                onChange={handleFormChange}
                placeholder="0~100"
              />
            </div>
            <div className="word-input-modal-form-group">
              <label>Listening</label>
              <input
                type="number"
                name="listening"
                min="0"
                max="100"
                value={wordForm.listening}
                onChange={handleFormChange}
                placeholder="0~100"
              />
            </div>
            <div className="word-input-modal-form-group">
              <label>Speaking</label>
              <input
                type="number"
                name="speaking"
                min="0"
                max="100"
                value={wordForm.speaking}
                onChange={handleFormChange}
                placeholder="0~100"
              />
            </div>
          </div>
        </div>
        <div className="word-input-modal-footer">
          <div className="word-input-modal-footer-left">
            {word?.user_id === user?.id && (
              <button onClick={handleDelete} className="word-input-modal-delete-btn">
                삭제
              </button>
            )}

            {!(user && user.roles.includes('user')) && (
              <h5>로그인 후 저장 가능합니다.</h5>
            )}
          </div>
          <div className="word-input-modal-footer-right">
            <button onClick={handleClose} className="word-input-modal-cancel-btn">
              취소
            </button>
            {user && user.roles.includes('user') && (
            <button onClick={handleSubmit} className="word-input-modal-add-btn">
              {word?.user_id === user?.id ? '수정' : '추가'}
            </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WordInputModal;
