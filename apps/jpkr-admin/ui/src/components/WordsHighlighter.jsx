import React, { useState } from 'react';
import { to_hiragana } from '../service/hangul-to-hiragana';
import './WordsHighlighter.css';
import { createWordsPersonal } from '../api/api';

const WordsHighlighter = ({words}) => {
  const [tooltip, setTooltip] = useState({ show: false, data: null, position: { x: 0, y: 0 } });  
  const [showModal, setShowModal] = useState(false);
  const [selectedWord, setSelectedWord] = useState(null);
  const [tempWords, setTempWords] = useState([]);
  const [wordForm, setWordForm] = useState({});

  // 툴팁 표시
  const handleMouseEnter = (word, event) => {
    const rect = event.target.getBoundingClientRect();
    setTooltip({
      show: true,
      data: word,
      position: {
        x: rect.left + rect.width / 2,
        y: rect.top - 150
      }
    });
  };

  // 툴팁 숨김
  const handleMouseLeave = () => {
    setTooltip({ show: false, data: null, position: { x: 0, y: 0 } });
  };

  // 모달 열기
  const handleWordClick = (word) => {
    setSelectedWord(word);
    setWordForm({
      word: word.word || '',
      jp_pronunciation: word.jp_pronunciation || word.surface,
      kr_pronunciation: word.kr_pronunciation || '',
      kr_meaning: word.kr_meaning || '',
      level: word.level || 'N5',
      skill_kanji: word.user_word_skills[0].skill_kanji || 0,
      skill_word_reading: word.user_word_skills[0].skill_word_reading || 0,
      skill_word_speaking: word.user_word_skills[0].skill_word_speaking || 0,
      skill_sentence_reading: word.user_word_skills[0].skill_sentence_reading || 0,
      skill_sentence_speaking: word.user_word_skills[0].skill_sentence_speaking || 0,
      skill_sentence_listening: word.user_word_skills[0].skill_sentence_listening || 0,
      is_favorite: word.user_word_skills[0].is_favorite || false
    });
    setShowModal(true);
  };

  // 모달 닫기
  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedWord(null);
    setWordForm({
      word: '',
      jp_pronunciation: '',
      kr_pronunciation: '',
      kr_meaning: '',
      level: '',
      skill_kanji: '',
      skill_word_reading: '',
      skill_word_speaking: '',
      skill_sentence_reading: '',
      skill_sentence_speaking: '',
      skill_sentence_listening: '',
      is_favorite: false
    });
  };

  // 폼 입력 처리
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    if (name === 'kr_pronunciation') {
      const kana = to_hiragana(value);
      setWordForm(prev => ({
        ...prev,
        'jp_pronunciation': kana,
        'kr_pronunciation': value
      }));
    } else {
      setWordForm(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  // 단어 추가/수정
  const handleAddWord = () => {
    if (!wordForm.word.trim()) {
      alert('단어를 입력해주세요.');
      return;
    }

    const newWord = {
      id: selectedWord?.id || Date.now(), // 기존 ID 유지하거나 새 ID 생성
      ...wordForm,
      surface: wordForm.word,
      originalWord: selectedWord
    };

    if (selectedWord?.id) {
      // 기존 단어 수정
      setTempWords(prev => prev.map(word => 
        word.id === selectedWord.id ? newWord : word
      ));
    } else {
      // 새 단어 추가
      setTempWords(prev => [...prev, newWord]);
    }
    
    handleCloseModal();
  };

  // 임시 단어 삭제
  const handleRemoveTempWord = (wordId) => {
    setTempWords(prev => prev.filter(word => word.id !== wordId));
  };

  // 임시 단어 편집
  const handleEditTempWord = (word) => {
    setSelectedWord(word);
    setWordForm({
      word: word.word || '',
      jp_pronunciation: word.jp_pronunciation || '',
      kr_pronunciation: word.kr_pronunciation || '',
      kr_meaning: word.kr_meaning || '',
      level: word.level || 'N5',
      skill_kanji: word.skill_kanji || 0,
      skill_word_reading: word.skill_word_reading || 0
    });
    setShowModal(true);
  };

  // API로 단어 전송
  const handleSendWordsToAPI = async () => {
    if (tempWords.length === 0) {
      alert('전송할 단어가 없습니다.');
      return;
    }
    console.log(tempWords)
    try {
        
      const response = await createWordsPersonal(tempWords);
      if (response.data.success) {
        alert('단어가 성공적으로 저장되었습니다.');
        setTempWords([]); // 성공 후 임시 단어 목록 비우기
      } else {
        alert('단어 저장에 실패했습니다: ' + (response.message || '알 수 없는 오류'));
      }
    } catch (error) {
      console.error('API 호출 오류:', error);
      alert('단어 저장 중 오류가 발생했습니다.');
    }
  };

  // 강조 표시된 텍스트 렌더링
  const renderHighlightedText = () => {
    if (!words) return null;
    const elements = [];
    for (let i_line in words) {
      for (let i_word in words[i_line]) {
        if (words[i_line][i_word].word_id) {
        elements.push(
          <span
            key={`morpheme-${i_line}-${i_word}`}
            className={`morpheme morpheme-${words[i_line][i_word].level}`}
            onMouseEnter={(e) => handleMouseEnter(words[i_line][i_word], e)}
            onMouseLeave={handleMouseLeave}
            onClick={() => handleWordClick(words[i_line][i_word])}
            >
            {words[i_line][i_word].surface}
          </span>
        );
        } else {
          elements.push(
            <span
              key={`morpheme-${i_line}-${i_word}`}
              className={`morpheme-other`}
              onMouseEnter={(e) => handleMouseEnter(words[i_line][i_word], e)}
              onMouseLeave={handleMouseLeave}
              onClick={() => handleWordClick(words[i_line][i_word])}
            >
              {words[i_line][i_word].surface}
            </span>
          );
        }
      }
      elements.push(
        <span key={`text-${i_line}-br`}>
          <br />
        </span>
      );
    }
    return elements;
  };

  return (
    <div className="morphological-analysis-container">
        <div className="highlighted-text">
            {renderHighlightedText()}
        </div>
        
        {words && (
          <div className="level-legend">
            <div className="legend-items">
              <div className="legend-item">
                <span className="legend-color morpheme-N5"></span>
                <span>N5 (초급)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color morpheme-N4"></span>
                <span>N4 (초중급)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color morpheme-N3"></span>
                <span>N3 (중급)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color morpheme-N2"></span>
                <span>N2 (중고급)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color morpheme-N1"></span>
                <span>N1 (고급)</span>
              </div>
            </div>
          </div>
        )}
        
        {/* 커스텀 툴팁 */}
        {tooltip.show && tooltip.data && (
          <div 
            className="custom-tooltip"
            style={{
              left: tooltip.position.x,
              top: tooltip.position.y,
              transform: 'translateX(-50%)'
            }}
          >
            <div className="tooltip-header">
              <span className="tooltip-surface">{tooltip.data.word}</span>
              <span className="tooltip-level">{tooltip.data.level}</span>
            </div>
            <div className="tooltip-content">
              <div className="tooltip-row">
                <span className="tooltip-label">일본어 발음:</span>
                <span className="tooltip-value">{tooltip.data.jp_pronunciation || '-'}</span>
              </div>
              <div className="tooltip-row">
                <span className="tooltip-label">한국어 발음:</span>
                <span className="tooltip-value">{tooltip.data.kr_pronunciation || '-'}</span>
              </div>
              <div className="tooltip-row">
                <span className="tooltip-label">한국어 뜻:</span>
                <span className="tooltip-value">{tooltip.data.kr_meaning || '-'}</span>
              </div>
            </div>
          </div>
        )}

             {/* 임시 단어 목록 섹션 */}
       {tempWords.length > 0 && (
         <div className="temp-words-section">
           <div className="temp-words-header">
             <h2>저장할 단어 목록</h2>
             <button
               onClick={handleSendWordsToAPI}
               className="send-words-btn"
             >
               API로 전송
             </button>
           </div>
           <div className="temp-words-container">
             {tempWords.map((word) => (
               <div key={word.id} className="temp-word-item">
                 <div 
                   className="temp-word-info"
                   onClick={() => handleEditTempWord(word)}
                   style={{ cursor: 'pointer' }}
                 >
                   <span className="temp-word-surface">{word.word}</span>
                   <span className="temp-word-level">({word.level})</span>
                   <span className="temp-word-surface">{word.jp_pronunciation}</span>
                   <span className="temp-word-surface">{word.kr_pronunciation}</span>
                   <span className="temp-word-meaning">{word.kr_meaning}</span>
                   <span className="temp-word-meaning">{word.skill_kanji}</span>
                   <span className="temp-word-meaning">{word.skill_word_reading}</span>
                 </div>
                 <button
                   onClick={() => handleRemoveTempWord(word.id)}
                   className="remove-temp-word-btn"
                 >
                   삭제
                 </button>
               </div>
             ))}
           </div>
         </div>
       )}

      {/* 단어 입력 모달 */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>단어 정보 입력</h3>
              <button onClick={handleCloseModal} className="modal-close-btn">×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>단어:</label>
                <input
                  type="text"
                  name="word"
                  value={wordForm.word}
                  onChange={handleFormChange}
                  placeholder="단어를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>일본어 발음:</label>
                <input
                  type="text"
                  name="jp_pronunciation"
                  value={wordForm.jp_pronunciation}
                  onChange={handleFormChange}
                  placeholder="일본어 발음을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>한국어 발음:</label>
                <input
                  type="text"
                  name="kr_pronunciation"
                  value={wordForm.kr_pronunciation}
                  onChange={handleFormChange}
                  placeholder="한국어 발음을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>한국어 뜻:</label>
                <input
                  type="text"
                  name="kr_meaning"
                  value={wordForm.kr_meaning}
                  onChange={handleFormChange}
                  placeholder="한국어 뜻을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>레벨:</label>
                <select
                  name="level"
                  value={wordForm.level}
                  onChange={handleFormChange}
                >
                  <option value="">레벨 선택</option>
                  <option value="N5">N5</option>
                  <option value="N4">N4</option>
                  <option value="N3">N3</option>
                  <option value="N2">N2</option>
                  <option value="N1">N1</option>
                </select>
              </div>
              <div className="form-group">
                <label>한자 스킬:</label>
                <input
                  type="text"
                  name="skill_kanji"
                  value={wordForm.skill_kanji}
                  onChange={handleFormChange}
                  placeholder="한자 스킬을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>단어 읽기 스킬:</label>
                <input
                  type="text"
                  name="skill_word_reading"
                  value={wordForm.skill_word_reading}
                  onChange={handleFormChange}
                  placeholder="단어 읽기 스킬을 입력하세요"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={handleCloseModal} className="modal-cancel-btn">
                취소
              </button>
              <button onClick={handleAddWord} className="modal-add-btn">
                {selectedWord?.id ? '수정' : '추가'}
              </button>
            </div>
          </div>
        </div>
      )}

     </div>
  );
};

export default WordsHighlighter;
