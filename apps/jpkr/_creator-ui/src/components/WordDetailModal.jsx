import React, { useState, useEffect } from 'react';
import { getSimilarWords } from '../api/api.js';
import './WordDetailModal.css';

const WordDetailModal = ({ isOpen, onClose, wordId }) => {
    const [wordData, setWordData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (isOpen && wordId) {
            fetchWordData();
        }
    }, [isOpen, wordId]);

    const fetchWordData = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getSimilarWords(wordId);
            if (response.data.error) {
                setError(response.data.error);
            } else {
                setWordData(response.data);
            }
        } catch (err) {
            setError('단어 정보를 불러오는데 실패했습니다.');
            console.error('Error fetching word data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    const handleClose = () => {
        setWordData(null);
        setError(null);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="word-detail-modal-overlay" onClick={handleBackdropClick}>
            <div className="word-detail-modal">
                <div className="modal-header">
                    <h2>단어 상세 정보</h2>
                    <button className="close-button" onClick={handleClose}>
                        ✕
                    </button>
                </div>
                
                <div className="modal-content">
                    {loading && (
                        <div className="loading">로딩 중...</div>
                    )}

                    {error && (
                        <div className="error">{error}</div>
                    )}

                    {wordData && (
                        <>
                            {/* 메인 단어 정보 */}
                            <div className="main-word-section">
                                <h3>단어 정보</h3>
                                <div className="word-card main-word">
                                    <div className="word-header">
                                        <span className="word-text">{wordData.word.lemma}</span>
                                        <span className="word-level">Level {wordData.word.level}</span>
                                    </div>
                                    <div className="word-pronunciations">
                                        <div className="pronunciation">
                                            <span className="label">일본어 발음:</span>
                                            <span className="value">{wordData.word.jp_pron}</span>
                                        </div>
                                        <div className="pronunciation">
                                            <span className="label">한국어 발음:</span>
                                            <span className="value">{wordData.word.kr_pron}</span>
                                        </div>
                                    </div>
                                    <div className="word-meaning">
                                        <span className="label">의미:</span>
                                        <span className="value">{wordData.word.kr_mean}</span>
                                    </div>
                                    <div className="word-stats">
                                        <div className="stat">
                                            <span className="stat-label">예문 수:</span>
                                            <span className="stat-value">{wordData.word.num_examples}</span>
                                        </div>
                                        <div className="stat">
                                            <span className="stat-label">임베딩:</span>
                                            <span className={`stat-value ${wordData.word.has_embedding ? 'has-embedding' : 'no-embedding'}`}>
                                                {wordData.word.has_embedding ? '있음' : '없음'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* 유사 단어 목록 */}
                            <div className="similar-words-section">
                                <h3>유사 단어 ({wordData.similar_words.length}개)</h3>
                                {wordData.similar_words.length > 0 ? (
                                    <div className="similar-words-grid">
                                        {wordData.similar_words.map((similarWord, index) => (
                                            <div key={similarWord.id} className="word-card similar-word">
                                                <div className="word-header">
                                                    <span className="word-text">{similarWord.lemma}</span>
                                                    <span className="word-level">Level {similarWord.level}</span>
                                                </div>
                                                <div className="word-pronunciations">
                                                    <div className="pronunciation">
                                                        <span className="label">일본어 발음:</span>
                                                        <span className="value">{similarWord.jp_pron}</span>
                                                    </div>
                                                    <div className="pronunciation">
                                                        <span className="label">한국어 발음:</span>
                                                        <span className="value">{similarWord.kr_pron}</span>
                                                    </div>
                                                </div>
                                                <div className="word-meaning">
                                                    <span className="label">의미:</span>
                                                    <span className="value">{similarWord.kr_mean}</span>
                                                </div>
                                                <div className="word-stats">
                                                    <div className="stat">
                                                        <span className="stat-label">예문 수:</span>
                                                        <span className="stat-value">{similarWord.num_examples}</span>
                                                    </div>
                                                    <div className="stat">
                                                        <span className="stat-label">임베딩:</span>
                                                        <span className={`stat-value ${similarWord.has_embedding ? 'has-embedding' : 'no-embedding'}`}>
                                                            {similarWord.has_embedding ? '있음' : '없음'}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="no-similar-words">
                                        유사 단어가 없습니다.
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WordDetailModal;
