import React, { useRef } from 'react';
import './ExampleCard.css';

const ExampleCard = ({ example, isMain = false }) => {
    const audioRef = useRef(null);

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

    const handleExampleClick = () => {
        if (example.audio_url) {
            playAudio(example.audio_url);
        }
    };

    return (
        <div 
            className={`example-card ${isMain ? 'example-card-main-example' : 'example-card-similar-example'} ${example.audio_url ? 'clickable' : ''}`}
            onClick={handleExampleClick}
        >
            <div className="example-card-header">
                <span className="example-card-id">ID: {example.id}</span>
                <span className="example-card-tags">{example.tags || '태그 없음'}</span>
                {example.audio_url && (
                    <span className="example-card-audio-indicator">🔊</span>
                )}
            </div>
            <div className="example-card-content">
                <div className="example-card-text">
                    <span className="label">일본어 텍스트:</span>
                    <span className="value example-card-jp-text">{example.jp_text}</span>
                </div>
                <div className="example-card-meaning">
                    <span className="label">한국어 의미:</span>
                    <span className="value example-card-kr-meaning">{example.kr_meaning}</span>
                </div>
            </div>
            <div className="example-card-stats">
                {isMain && (
                    <>
                        <div className="example-card-stat">
                            <span className="example-card-stat-label">단어 수:</span>
                            <span className="example-card-stat-value">{example.num_words}</span>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ExampleCard;
