import React, { useState } from 'react';
import { analyzeText } from '../api/api';
import EditableTable from '../components/EditableTable';
import './WordAnalysis.css';

const columns = [
    {
      key: 'surface',
      label: '단어'
    },  
    {
      key: 'word',
      label: '기본형'
    },
    {
      key: 'jp_pronunciation',
      label: '일본어 발음'
    },
    {
      key: 'kr_pronunciation',
      label: '한국어 발음'
    },
    {
      key: 'kr_meaning',
      label: '한국어 뜻'
    },
    {
      key: 'level',
      label: '레벨'
    },
    {
      key: 'num_examples',
      label: '예문 수'
    }
  ];


const WordAnalysis = () => {
  const [inputText, setInputText] = useState('');
  const [words, setWords] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [message, setMessage] = useState('');
  const [tooltip, setTooltip] = useState({ show: false, data: null, position: { x: 0, y: 0 } });

  // 실제 단어 분석 API 호출
  const analyzeMorphology = async (text) => {
    try {
      const response = await analyzeText(text);
      return response.data;
    } catch (error) {
      console.error('API 호출 오류:', error);
      throw error;
    }
  };

  // 단어 분석 실행
  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      setMessage('텍스트를 입력해주세요.');
      return;
    }

    setIsAnalyzing(true);
    setMessage('');
    setWords([]);

    try {
      const result = await analyzeMorphology(inputText);
      setWords(result);
      setMessage('단어 분석이 완료되었습니다.');
    } catch (error) {
      console.error('단어 분석 오류:', error);
      setMessage('단어 분석 중 오류가 발생했습니다.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 텍스트 초기화
  const handleClear = () => {
    setInputText('');
    setWords([]);
    setMessage('');
  };

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

  // 강조 표시된 텍스트 렌더링
  const renderHighlightedText = () => {
    if (!words || !inputText) return null;

    // 모든 단어의 위치를 찾아서 정렬
    const wordPositions = [];
    words.forEach((word, wordIndex) => {
      let searchIndex = 0;
      while (true) {
        const foundIndex = inputText.indexOf(word.surface, searchIndex);
        if (foundIndex === -1) break;
        
        wordPositions.push({
          start: foundIndex,
          end: foundIndex + word.surface.length,
          word: word,
          wordIndex: wordIndex
        });
        
        searchIndex = foundIndex + 1;
      }
    });
    // 위치 순서대로 정렬
    wordPositions.sort((a, b) => a.start - b.start);

    const elements = [];
    let lastIndex = 0;

    wordPositions.forEach((position, index) => {
      // 단어 이전 텍스트 추가
      if (position.start > lastIndex) {
        let s_total = inputText.slice(lastIndex, position.start);
        let s_list = s_total.split("\n");
        s_list.forEach((s, i) => {
          elements.push(
            <span key={`text-${index}-${i}`}>
              {s}
            </span>
          );
          if (i < s_list.length - 1) {
            elements.push(
              <span key={`text-${index}-${i}-br`}>
                <br />
              </span>
            );
          }
        });
      }

      // 단어 강조 표시
      elements.push(
        <span
          key={`morpheme-${index}`}
          className={`morpheme morpheme-${position.word.level}`}
          onMouseEnter={(e) => handleMouseEnter(position.word, e)}
          onMouseLeave={handleMouseLeave}
        >
          {position.word.surface}
        </span>
      );

      lastIndex = position.end;
    });

    // 마지막 단어 이후 텍스트 추가
    if (lastIndex < inputText.length) {
      let s_total = inputText.slice(lastIndex);
      let s_list = s_total.split("\n");
      s_list.forEach((s, i) => {
        elements.push(
          <span key={`text-end-${i}`}>
            {s}
          </span>
        );
        if (i < s_list.length - 1) {
          elements.push(
            <span key={`text-end-${i}-br`}>
              <br />
            </span>
          );
        }
      });
    }

    return elements;
  };

  return (
    <div className="morphological-analysis-container">
      <div className="page-header">
        <h1>일본어 단어 분석</h1>
        <p>일본어 텍스트를 입력하면 단어를 추출하여 강조 표시합니다.</p>
      </div>

      <div className="input-section">
        <div className="input-header">
          <h2>텍스트 입력</h2>
          <div className="input-actions">
            <button 
              onClick={handleClear} 
              className="clear-btn"
              disabled={!inputText.trim()}
            >
              초기화
            </button>
          </div>
        </div>

        <div className="text-input-container">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="일본어 텍스트를 입력하세요..."
            className="text-input"
            rows={8}
            disabled={isAnalyzing}
          />
        </div>

        <div className="analyze-section">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !inputText.trim()}
            className="analyze-btn"
          >
            {isAnalyzing ? '분석 중...' : '단어 분석'}
          </button>
        </div>

                 {message && (
           <div className={`message ${message.includes('완료') ? 'success' : 'error'}`}>
             {message}
           </div>
         )}
       </div>
        <div className="highlighted-text">
            {renderHighlightedText()}
        </div>
        
        {words.length > 0 && (
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
        {/*
        <EditableTable
          columns={columns}
          data={words}          
          showAddRow={false}
          showPasteButton={false}
          showCopyButton={true}
          showDeleteButton={false}
        />
        */}

        {/* 단어별 예문 섹션 */}
        {words.length > 0 && (
          <div className="examples-section">
            <h2>단어별 예문</h2>
            <div className="examples-container">
              {words.map((word, wordIndex) => (
                word.examples && (
                  <div key={`word-${wordIndex}`} className="word-examples">
                    <div className="word-header">
                      <h3 className="word-title">
                        <span className="word-surface">{word.surface}</span>
                        <span className="word-level">({word.level})</span>
                      </h3>
                      <span className="word-pronunciation">{word.jp_pronunciation}</span>
                      <span className="word-pronunciation">{word.kr_pronunciation}</span>
                      <span className="word-meaning">{word.kr_meaning}</span>
                    </div>
                    <div className="examples-list">
                      {word.examples.map((example, exampleIndex) => (
                        <div key={`example-${wordIndex}-${exampleIndex}`} className="example-item">
                          <div className="example-japanese">
                            {example.jp_text}
                          </div>
                          <div className="example-korean">
                            {example.kr_meaning}
                          </div>
                          {example.tags && example.tags.trim() && (
                            <div className="example-tags">
                              {example.tags.split(',').map((tag, tagIndex) => (
                                <span key={`tag-${wordIndex}-${exampleIndex}-${tagIndex}`} className="tag">
                                  {tag.trim()}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )
              ))}
            </div>
          </div>
        )}

     </div>
  );
};

export default WordAnalysis;
