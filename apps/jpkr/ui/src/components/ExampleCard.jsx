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
            className={`example-card ${isMain ? 'main-example' : 'similar-example'} ${example.audio_url ? 'clickable' : ''}`}
            onClick={handleExampleClick}
        >
            <div className="example-header">
                <span className="example-tags">{example.tags || '태그 없음'}</span>
                {example.audio_url && (
                    <span className="audio-indicator">🔊</span>
                )}
            </div>
            {example.image_url && (
                <div className="example-image">
                    <img src={example.image_url} alt="Example Image" />
                </div>
            )}
            <div className="example-content">
                <div className="example-text">
                    <span className="label">일본어 텍스트:</span>
                    <span className="value jp-text">{example.jp_text}</span>
                </div>
                <div className="example-meaning">
                    <span className="label">한국어 의미:</span>
                    <span className="value kr-meaning">{example.kr_mean}</span>
                </div>
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
        </div>
    );
};

export default ExampleCard;
