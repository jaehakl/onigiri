import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeText } from '../api/api';
import './WordAnalysis.css';
import WordsHighlighter from '../components/WordsHighlighter';

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
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  const [words, setWords] = useState({});
  const [words_set, setWordsSet] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [message, setMessage] = useState('');
  
  useEffect(() => {
    let words_set = {};
    for (let i_line in words) {
      for (let i_word in words[i_line]) {
        if (words[i_line][i_word].word_id) {
          words_set[words[i_line][i_word].word_id] = words[i_line][i_word];
        }
      }
    }
    setWordsSet(words_set);
  }, [words]);

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
    setWords({});

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
    setWords({});
    setMessage('');
  };

  // 단어 공부하기 버튼 클릭 핸들러
  const handleStudy = () => {
    if (Object.keys(words_set).length === 0) {
      setMessage('분석된 단어가 없습니다. 먼저 텍스트를 분석해주세요.');
      return;
    }
    
    // 퀴즈 페이지로 이동하면서 단어 데이터 전달
    navigate('/quiz', { 
      state: { 
        words: Object.values(words_set),
        sourceText: inputText 
      } 
    });
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
          <button
            onClick={handleStudy}
            disabled={Object.keys(words_set).length === 0}
            className="study-btn"
          >
            단어 공부하기
          </button>
        </div>

                 {message && (
           <div className={`message ${message.includes('완료') ? 'success' : 'error'}`}>
             {message}
           </div>
         )}
       </div>
       <WordsHighlighter words={words} />
        
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
        
       

        {/* 단어별 예문 섹션 */}
        {Object.keys(words_set).length > 0 && (
          <div className="examples-section">
            <h2>단어별 예문</h2>
            <div className="examples-container">
              {Object.values(words_set).map((word, wordIndex) => (
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
