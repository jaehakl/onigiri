import React, { useState, useEffect } from 'react';
import EditableTable from '../../components/EditableTable';
import ExampleDetailModal from '../../components/ExampleDetailModal';
import FilterInput from '../../components/FilterInput';
import { filterExamples, updateExamplesBatch, deleteExamplesBatch, genExampleEmbeddings, genExampleAudio, genExampleImage, genExampleWords } from '../api/api';
import './FilterExamples.css';

 // 필터 설정
const FILTER_CONFIG = {
  sections: [
    {
      type: 'range',
      key: 'words',
      label: '단어 수',
      minKey: 'min_words',
      maxKey: 'max_words',
      minLabel: '최소',
      maxLabel: '최대',
      minDefault: '',
      maxDefault: ''
    },
    {
      type: 'select',
      key: 'has_en_prompt',
      label: '프롬프트 보유 여부',
      defaultValue: null
    },
    {
      type: 'select',
      key: 'has_audio',
      label: '음성 보유 여부',
      defaultValue: null
    },
    {
      type: 'select',
      key: 'has_image',
      label: '이미지 보유 여부',
      defaultValue: null
    },
    {
      type: 'select',
      key: 'has_embedding',
      label: '임베딩 보유 여부',
      defaultValue: null
    }
  ]
};

const FilterExamples = () => {
  
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState({
    filtering: false,
    embedding: false,
    audio: false,
    image: false,
    words: false
  });
  const [error, setError] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  
  // 모달 상태 관리
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedExampleId, setSelectedExampleId] = useState(null);

 

  // 테이블 컬럼 정의
  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'tags', label: '태그' },
    { key: 'jp_text', label: '일본어 텍스트' },
    { key: 'kr_mean', label: '한국어 의미' },
    { key: 'en_prompt', label: '프롬프트' },
    { key: 'num_words', label: '단어 수' },
    { key: 'has_audio', label: '음성 보유' },
    { key: 'has_image', label: '이미지 보유' },
    { key: 'has_embedding', label: '임베딩 보유' }
  ];

  // 필터링 실행
  const handleFilter = async (filterData) => {
    setLoading(prev => ({ ...prev, filtering: true }));
    setError(null);
    
    try {
      // 필터 데이터 정리
      const cleanFilterData = {
        ...filterData,
        min_words: filterData.min_words ? parseInt(filterData.min_words) : null,
        max_words: filterData.max_words ? parseInt(filterData.max_words) : null,
        has_en_prompt: filterData.has_en_prompt,
        has_embedding: filterData.has_embedding,
        has_audio: filterData.has_audio,
        has_image: filterData.has_image,
        limit: filterData.limit,
        offset: filterData.offset || 0
      };

      const response = await filterExamples(cleanFilterData);
      setExamples(response.data.examples || []);
      setTotalCount(response.data.total_count || 0);
    } catch (err) {
      setError('필터링 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
      setExamples([]);
      setTotalCount(0);
    } finally {
      setLoading(prev => ({ ...prev, filtering: false }));
    }
  };

  // 필터 초기화
  const handleReset = (defaultValues) => {
    setExamples([]);
    setTotalCount(0);
    setError(null);
  };

  // 예문 수정 핸들러
  const handleUpdateExamples = async (examplesToUpdate) => {
    if (!examplesToUpdate || examplesToUpdate.length === 0) {
      alert('수정할 예문이 없습니다.');
      return;
    }

    try {
      setLoading(prev => ({ ...prev, filtering: true }));
      const exampleDataList = examplesToUpdate.map(example => ({
        id: example.id,
        tags: example.tags,
        jp_text: example.jp_text,
        kr_mean: example.kr_mean,
        en_prompt: example.en_prompt,
      }));
      await updateExamplesBatch(exampleDataList);
      alert(`${examplesToUpdate.length}개의 예문이 성공적으로 수정되었습니다.`);
      // 수정 후 현재 필터 조건으로 다시 검색
      // TODO: 현재 필터 데이터를 다시 가져와서 검색해야 함
    } catch (err) {
      setError('예문 수정 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(prev => ({ ...prev, filtering: false }));
    }
  };

  // 예문 삭제 핸들러
  const handleDeleteExamples = async (exampleIds) => {
    if (!exampleIds || exampleIds.length === 0) {
      alert('삭제할 예문이 없습니다.');
      return;
    }

    const confirmMessage = `선택된 ${exampleIds.length}개의 예문을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`;
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, filtering: true }));
      await deleteExamplesBatch(exampleIds);
      alert(`${exampleIds.length}개의 예문이 성공적으로 삭제되었습니다.`);
      // 삭제 후 현재 필터 조건으로 다시 검색
      // TODO: 현재 필터 데이터를 다시 가져와서 검색해야 함
    } catch (err) {
      setError('예문 삭제 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(prev => ({ ...prev, filtering: false }));
    }
  };

  // 셀 클릭 핸들러
  const handleCellClick = (row, columnKey) => {
    if (columnKey === 'id') {
      setSelectedExampleId(row.id);
      setIsModalOpen(true);
    }
  };

  // 모달 닫기 핸들러
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedExampleId(null);
  };

  // 임베딩 생성 핸들러
  const handleGenerateEmbeddings = async () => {
    if (!examples || examples.length === 0) {
      alert('임베딩을 생성할 예문이 없습니다.');
      return;
    }

    const exampleIds = examples.map(example => example.id);
    const confirmMessage = `현재 표시된 ${exampleIds.length}개의 예문에 대해 임베딩을 생성하시겠습니까?\n이 작업은 시간이 오래 걸릴 수 있습니다.`;
    
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, embedding: true }));
      setError(null);
      await genExampleEmbeddings(exampleIds);
      alert(`${exampleIds.length}개의 예문에 대한 임베딩이 성공적으로 생성되었습니다.`);
      // 임베딩 생성 후 현재 필터 조건으로 다시 검색하여 상태 업데이트
      // TODO: 현재 필터 데이터를 다시 가져와서 검색해야 함
    } catch (err) {
      setError('임베딩 생성 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(prev => ({ ...prev, embedding: false }));
    }
  };

  // 오디오 생성 핸들러
  const handleGenerateAudio = async () => {
    if (!examples || examples.length === 0) {
      alert('오디오를 생성할 예문이 없습니다.');
      return;
    }

    const exampleIds = examples.map(example => example.id);
    const confirmMessage = `현재 표시된 ${exampleIds.length}개의 예문에 대해 오디오를 생성하시겠습니까?\n이 작업은 시간이 오래 걸릴 수 있습니다.`;
    
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, audio: true }));
      setError(null);
      await genExampleAudio(exampleIds);
      alert(`${exampleIds.length}개의 예문에 대한 오디오가 성공적으로 생성되었습니다.`);
      // 오디오 생성 후 현재 필터 조건으로 다시 검색하여 상태 업데이트
      // TODO: 현재 필터 데이터를 다시 가져와서 검색해야 함
    } catch (err) {
      setError('오디오 생성 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(prev => ({ ...prev, audio: false }));
    }
  };

  // 이미지 생성 핸들러
  const handleGenerateImage = async () => {
    if (!examples || examples.length === 0) {
      alert('이미지를 생성할 예문이 없습니다.');
      return;
    }

    const exampleIds = examples.map(example => example.id);
    const confirmMessage = `현재 표시된 ${exampleIds.length}개의 예문에 대해 이미지를 생성하시겠습니까?\n이 작업은 시간이 오래 걸릴 수 있습니다.`;
    
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, image: true }));
      setError(null);
      await genExampleImage(exampleIds);
      alert(`${exampleIds.length}개의 예문에 대한 이미지가 성공적으로 생성되었습니다.`);
      // 이미지 생성 후 현재 필터 조건으로 다시 검색하여 상태 업데이트
      // TODO: 현재 필터 데이터를 다시 가져와서 검색해야 함
    } catch (err) {
      setError('이미지 생성 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(prev => ({ ...prev, image: false }));
    }
  };

  // Words 생성 핸들러
  const handleGenerateWords = async () => {
    if (!examples || examples.length === 0) {
      alert('Words를 생성할 예문이 없습니다.');
      return;
    }

    const exampleIds = examples.map(example => example.id);
    const confirmMessage = `현재 표시된 ${exampleIds.length}개의 예문에 대해 Words를 생성하시겠습니까?\n이 작업은 시간이 오래 걸릴 수 있습니다.`;
    
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, words: true }));
      setError(null);
      await genExampleWords(exampleIds);
      alert(`${exampleIds.length}개의 예문에 대한 Words가 성공적으로 생성되었습니다.`);
      // Words 생성 후 현재 필터 조건으로 다시 검색하여 상태 업데이트
      // TODO: 현재 필터 데이터를 다시 가져와서 검색해야 함
    } catch (err) {
      setError('Words 생성 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(prev => ({ ...prev, words: false }));
    }
  };


  return (
    <div className="filter-words-container">
      <h1>예문 필터링</h1>
      
      {/* 필터 조건 입력 폼 */}
      <FilterInput
        filterConfig={FILTER_CONFIG}
        onSubmit={handleFilter}
        onReset={handleReset}
        loading={loading.filtering}
        totalCount={totalCount}
        showPagination={true}
        limit={100}
      />

      {/* 결과 정보 */}
      {totalCount > 0 && (
        <div className="result-info">
          <p>총 {totalCount}개의 예문이 검색되었습니다. (현재 {examples.length}개 표시)</p>
        </div>
      )}

      {/* 에러 메시지 */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 결과 테이블 */}
      {examples.length > 0 && (
        <div className="results-section">
          {/* 임베딩, 오디오, 이미지, Words 생성 버튼 */}
          <div className="embedding-actions">
            <button 
              onClick={handleGenerateEmbeddings} 
              disabled={loading.embedding || loading.filtering || loading.audio || loading.image || loading.words} 
              className="generate-embeddings-btn"
            >
              {loading.embedding ? '임베딩 생성 중...' : `현재 ${examples.length}개 예문 임베딩 생성`}
            </button>
            <button 
              onClick={handleGenerateAudio} 
              disabled={loading.audio || loading.filtering || loading.embedding || loading.image || loading.words} 
              className="generate-audio-btn"
            >
              {loading.audio ? '오디오 생성 중...' : `현재 ${examples.length}개 예문 오디오 생성`}
            </button>
            <button 
              onClick={handleGenerateImage} 
              disabled={loading.image || loading.filtering || loading.embedding || loading.audio || loading.words} 
              className="generate-image-btn"
            >
              {loading.image ? '이미지 생성 중...' : `현재 ${examples.length}개 예문 이미지 생성`}
            </button>
            <button 
              onClick={handleGenerateWords} 
              disabled={loading.words || loading.filtering || loading.embedding || loading.audio || loading.image} 
              className="generate-words-btn"
            >
              {loading.words ? 'Words 생성 중...' : `현재 ${examples.length}개 예문 Words 생성`}
            </button>
          </div>
          
          <EditableTable
            columns={columns}
            data={examples}
            onDataChange={setExamples}
            onUpdate={handleUpdateExamples}
            onDelete={handleDeleteExamples}
            onCellClick={handleCellClick}
            showAddRow={false}
            showPasteButton={false}
            showCopyButton={true}
            showDeleteButton={true}
            addRowText=""
            deleteRowText="삭제"
          />
        </div>
      )}

      {/* 결과가 없을 때 */}
      {!loading && examples.length === 0 && totalCount === 0 && !error && (
        <div className="no-results">
          <p>필터 조건을 설정하고 "필터링 실행" 버튼을 클릭하세요.</p>
        </div>
      )}

      {/* 예문 상세 모달 */}
      <ExampleDetailModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        exampleId={selectedExampleId}
      />
    </div>
  );
};

export default FilterExamples;
