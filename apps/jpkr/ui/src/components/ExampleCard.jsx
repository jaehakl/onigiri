import React, { useRef, useState } from 'react';
import WordsHighlighter from './WordsHighlighter';
import './ExampleCard.css';
import { deleteExamplesBatch } from '../api/api';
import { useUser } from '../contexts/UserContext';

const ExampleCard = ({ example, isMain = false }) => {
    const { user } = useUser();
    const audioRef = useRef(null);
    const [showMeaning, setShowMeaning] = useState(false);
    const [notification, setNotification] = useState(null);
    const [deleted, setDeleted] = useState(false);

    const playAudio = (audioUrl) => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
        }
        
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        audio.play().catch(err => {
            console.error('오디오 재생 실패:', err);
        });
    };

    const handleImageClick = (e) => {
        e.stopPropagation();
        if (example.audio_url) {
            playAudio(example.audio_url);
        }
    };

    const toggleMeaning = (e) => {
        e.stopPropagation();
        setShowMeaning(!showMeaning);
    };

    const handleDelete = async (e) => {
        e.stopPropagation();
        
        try {
            await deleteExamplesBatch([example.id]);
            setNotification({ type: 'success', message: '예제가 성공적으로 삭제되었습니다.' });

            setDeleted(true);
            // 3초 후 알림 자동 제거
            setTimeout(() => {
                setNotification(null);
            }, 3000);
        } catch (error) {
            console.error('삭제 실패:', error);
            setNotification({ type: 'error', message: '삭제에 실패했습니다. 다시 시도해주세요.' });
            
            // 5초 후 알림 자동 제거
            setTimeout(() => {
                setNotification(null);
            }, 5000);
        }
    };

    return (
        <div 
            className={`example-card ${isMain ? 'main-example' : 'similar-example'}`}
            style={{ position: 'relative' }}
        >
            {!deleted && (
            <>
            {notification && (
                <div className={`notification ${notification.type}`}>
                    {notification.message}
                </div>
            )}
            <div className="example-header">
                <span className="example-tags">{example.tags || '태그 없음'}</span>
                <div className="header-icons">
                    <span 
                        className="meaning-toggle" 
                        onClick={toggleMeaning}
                        title="한국어 뜻 보기/숨기기"
                    >
                        {showMeaning ? '👁️' : '👁️‍🗨️'}
                    </span>
                    {user && user.roles && user.roles.includes('admin') && (
                        <span className="example-card-delete-icon" 
                            onClick={handleDelete}
                            title="삭제"
                        >🗑️</span>
                    )}
                </div>
            </div>
            <div className="example-content">
                {example.words ? (
                    <WordsHighlighter words={example.words} />
                ) : (
                    <div className="example-text">
                        <span className="value jp-text">{example.jp_text}</span>
                    </div>
                )}
            {example.image_url && (
                <div className="example-image" onClick={handleImageClick}>
                    <img src={example.image_url} alt="Example Image" />
                </div>
            )}

                {showMeaning && (
                    <div className="example-meaning">
                        <span className="value kr-meaning">{example.kr_mean}</span>
                    </div>
                )}
            </div>
            <div className="example-stats">
                {isMain && (
                    <>
                        <div className="stat">
                            <span className="stat-label">단어 수:</span>
                            <span className="stat-value">{example.num_words}</span>
                        </div>
                    </>
                )}
            </div>
            </>
            )}
        </div>
    );
};

export default ExampleCard;
