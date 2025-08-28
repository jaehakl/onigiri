import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeText, createUserText, getUserText, updateUserText } from '../api/api';
import './WordAnalysis.css';
import WordsHighlighter from '../components/WordsHighlighter';
import SaveTextModal from '../components/SaveTextModal';
import LoadTextModal from '../components/LoadTextModal';
import YouTubeEmbed from '../components/YouTubeEmbed';
import WordExamples from '../components/WordExamples';
import { to_hiragana } from '../service/hangul-to-hiragana';
import { sample_text } from '../service/sample-text';

const WordAnalysis = () => {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  const [analyzedText, setAnalyzedText] = useState('');
  const [words, setWords] = useState({});
  const [words_set, setWordsSet] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [message, setMessage] = useState('');
  
  // 모달 상태
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [isLoadModalOpen, setIsLoadModalOpen] = useState(false);
  
  // 현재 텍스트 정보
  const [currentTextInfo, setCurrentTextInfo] = useState({
    id: '',
    title: '',
    tags: '',
    youtube_url: '',
    audio_url: ''
  });
  
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

  useEffect(() => {
    if (analyzedText) {
      handleAnalyze(analyzedText);
    }
  }, [analyzedText]);

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
  const handleAnalyze = async (text) => {
    if (!text.trim()) {
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
    setCurrentTextInfo({
      id: '',
      title: '',
      tags: '',
      youtube_url: '',
      audio_url: ''
    });
  };

  // 텍스트 저장 핸들러
  const handleSaveText = async (textData) => {
    setIsSaveModalOpen(false);
  };

  // 텍스트 불러오기 핸들러
  const handleLoadText = async (textData) => {
    const response = await getUserText(textData.id);
    const user_text = response.data;
    const text_info = {}
    text_info.id = String(user_text.id);
    text_info.title = user_text.title;
    text_info.tags = user_text.tags;
    text_info.youtube_url = user_text.youtube_url;
    text_info.audio_url = user_text.audio_url;
    setCurrentTextInfo(text_info);
    setInputText(user_text.text);
    setAnalyzedText(user_text.text);
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
      <div className="input-section">
        <div className="input-header">
          {currentTextInfo.id && (
            <h2>{currentTextInfo.title}</h2>
          )}
          {!currentTextInfo.id && (
            <h2>テキスト入力</h2>
          )}
          <div className="input-actions">
            <button 
              onClick={handleClear} 
              className="clear-btn"
              disabled={!inputText.trim()}
            >
              초기화
            </button>
            <button 
              onClick={async () => {
                try {
                  const clipboardText = await navigator.clipboard.readText();
                  if (clipboardText && clipboardText.trim()) {
                    setInputText(clipboardText);
                    navigator.clipboard.writeText('');
                  } else {
                    setInputText(sample_text(0));
                  }
                } catch (error) {
                  console.error('클립보드 읽기 오류:', error);
                }
              }}
              className="clear-btn"
            >
              붙여넣기
            </button>
            <button 
              onClick={()=>setInputText(to_hiragana(inputText))} 
              className="clear-btn"
              disabled={!inputText.trim()}
            >
              가 / が (Tab)
            </button>
          </div>
        </div>

        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Tab') {
              e.preventDefault(); // Tab 키의 기본 동작 차단
              setInputText(to_hiragana(inputText)); // 한글로 변환
            }
          }}
          placeholder={sample_text(0)}
          className="text-input"
          rows={8}
          disabled={isAnalyzing}
        />

        <div className="analyze-section">
          <div className="button-group">
            <button
              onClick={()=>handleAnalyze(inputText)}
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
            <button
              onClick={() => setIsSaveModalOpen(true)}
              disabled={!inputText.trim()}
              className="save-btn"
            >
              저장
            </button>
            <button
              onClick={() => setIsLoadModalOpen(true)}
              className="load-btn"
            >
              불러오기
            </button>
          </div>
          
          {/* YouTube 임베드 */}
          {currentTextInfo.youtube_url && (
            <div className="youtube-section">
              <YouTubeEmbed url={currentTextInfo.youtube_url} size="100%"/>
            </div>
          )}
        </div>

        {message && (
          <div className={`message ${message.includes('완료') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>
      {words && Object.keys(words).length > 0 && (
        <WordsHighlighter words={words} />
      )}
      
        
      {/* 단어별 예문 섹션 */}
      <WordExamples wordsSet={words_set} />

      {/* 모달들 */}
      <SaveTextModal
        isOpen={isSaveModalOpen}
        onClose={() => setIsSaveModalOpen(false)}
        defaultTextData={currentTextInfo}
        onSave={handleSaveText}
        text={inputText}
      />
      
      <LoadTextModal
        isOpen={isLoadModalOpen}
        onClose={() => setIsLoadModalOpen(false)}
        onLoadText={handleLoadText}
      />
    </div>
  );
};

export default WordAnalysis;

