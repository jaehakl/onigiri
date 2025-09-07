import React, { useState, useEffect } from 'react';
import { getSimilarExamples } from '../api/api.js';
import ExampleCard from './ExampleCard';
import './ExampleDetailModal.css';

const ExampleDetailModal = ({ isOpen, onClose, exampleId }) => {
    const [exampleData, setExampleData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (isOpen && exampleId) {
            fetchExampleData();
        }
    }, [isOpen, exampleId]);

    const fetchExampleData = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getSimilarExamples(exampleId);
            if (response.data.error) {
                setError(response.data.error);
            } else {
                setExampleData(response.data);
            }
        } catch (err) {
            setError('예문 정보를 불러오는데 실패했습니다.');
            console.error('Error fetching example data:', err);
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
        setExampleData(null);
        setError(null);
        onClose();
    };



    if (!isOpen) return null;

    return (
        <div className="example-detail-modal-overlay" onClick={handleBackdropClick}>
            <div className="example-detail-modal">
                <div className="modal-header">
                    <h2>예문 상세 정보</h2>
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

                    {exampleData && (
                        <>
                            {/* 메인 예문 정보 */}
                            <div className="main-example-section">
                                <h3>예문 정보</h3>
                                <ExampleCard example={exampleData.example} isMain={true} />
                            </div>

                            {/* 유사 예문 목록 */}
                            <div className="similar-examples-section">
                                <h3>유사 예문 ({exampleData.similar_examples.length}개)</h3>
                                {exampleData.similar_examples.length > 0 ? (
                                    <div className="similar-examples-grid">
                                        {exampleData.similar_examples.map((similarExample, index) => (
                                            <ExampleCard 
                                                key={similarExample.id} 
                                                example={similarExample} 
                                                isMain={false} 
                                            />
                                        ))}
                                    </div>
                                ) : (
                                    <div className="no-similar-examples">
                                        유사 예문이 없습니다.
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

export default ExampleDetailModal;
