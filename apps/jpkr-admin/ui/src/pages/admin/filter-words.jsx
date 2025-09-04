import React, { useState, useEffect } from 'react';
import EditableTable from '../../components/EditableTable';
import WordDetailModal from '../../components/WordDetailModal';
import { filterWords, updateWordsBatch, deleteWordsBatch, genWordEmbeddings } from '../../api/api';
import './FilterWords.css';

const FilterWords = () => {
  const [filterData, setFilterData] = useState({
    levels: [],
    min_examples: '',
    max_examples: '',
    has_embedding: null,
    limit: 100,
    offset: 0
  });
  
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  
  // 모달 상태 관리
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedWordId, setSelectedWordId] = useState(null);

  // JLPT 레벨 옵션
  const levelOptions = ['N5', 'N4', 'N3', 'N2', 'N1'];

  // 테이블 컬럼 정의
  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'lemma_id', label: '원형 ID' },
    { key: 'lemma', label: '원형' },
    { key: 'jp_pron', label: '일본어 발음' },
    { key: 'kr_pron', label: '한국어 발음' },
    { key: 'kr_mean', label: '의미' },
    { key: 'level', label: '레벨' },
    { key: 'num_examples', label: '예문 수' },
    { key: 'has_embedding', label: '임베딩 보유' }
  ];

  // 필터 조건 변경 핸들러
  const handleFilterChange = (field, value) => {
    setFilterData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 레벨 선택/해제 핸들러
  const handleLevelToggle = (level) => {
    setFilterData(prev => ({
      ...prev,
      levels: prev.levels.includes(level)
        ? prev.levels.filter(l => l !== level)
        : [...prev.levels, level]
    }));
  };

  // 필터링 실행
  const handleFilter = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 필터 데이터 정리
      
      const cleanFilterData = {
        ...filterData,
        levels: filterData.levels.length > 0 ? filterData.levels : null,
        min_examples: filterData.min_examples ? parseInt(filterData.min_examples) : null,
        max_examples: filterData.max_examples ? parseInt(filterData.max_examples) : null,
        limit: filterData.limit || 100,
        offset: filterData.offset || 0
      };

      const response = await filterWords(cleanFilterData);
      setWords(response.data.words || []);
      setTotalCount(response.data.total_count || 0);
    } catch (err) {
      setError('필터링 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
      setWords([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  // 페이지네이션 핸들러
  const handlePageChange = (newOffset) => {
    setFilterData(prev => ({
      ...prev,
      offset: newOffset
    }));
  };

  // 필터 초기화
  const handleReset = () => {
    setFilterData({
      levels: [],
      min_examples: '',
      max_examples: '',
      has_embedding: null,
      limit: 100,
      offset: 0
    });
    setWords([]);
    setTotalCount(0);
    setError(null);
  };

  // 단어 수정 핸들러
  const handleUpdateWords = async (wordsToUpdate) => {
    if (!wordsToUpdate || wordsToUpdate.length === 0) {
      alert('수정할 단어가 없습니다.');
      return;
    }

    try {
      setLoading(true);
      const wordDataList = wordsToUpdate.map(word => ({
        id: word.id,
        lemma_id: word.lemma_id,
        lemma: word.lemma,
        jp_pron: word.jp_pron,
        kr_pron: word.kr_pron,
        kr_mean: word.kr_mean,
        level: word.level,
      }));
      await updateWordsBatch(wordDataList);
      alert(`${wordsToUpdate.length}개의 단어가 성공적으로 수정되었습니다.`);
      // 수정 후 현재 필터 조건으로 다시 검색
      await handleFilter();
    } catch (err) {
      setError('단어 수정 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // 단어 삭제 핸들러
  const handleDeleteWords = async (wordIds) => {
    if (!wordIds || wordIds.length === 0) {
      alert('삭제할 단어가 없습니다.');
      return;
    }

    const confirmMessage = `선택된 ${wordIds.length}개의 단어를 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`;
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(true);
      await deleteWordsBatch(wordIds);
      alert(`${wordIds.length}개의 단어가 성공적으로 삭제되었습니다.`);
      // 삭제 후 현재 필터 조건으로 다시 검색
      await handleFilter();
    } catch (err) {
      setError('단어 삭제 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // 셀 클릭 핸들러
  const handleCellClick = (row, columnKey) => {
    if (columnKey === 'id') {
      setSelectedWordId(row.id);
      setIsModalOpen(true);
    }
  };

  // 모달 닫기 핸들러
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedWordId(null);
  };

  // 임베딩 생성 핸들러
  const handleGenerateEmbeddings = async () => {
    if (!words || words.length === 0) {
      alert('임베딩을 생성할 단어가 없습니다.');
      return;
    }

    const wordIds = words.map(word => word.id);
    const confirmMessage = `현재 표시된 ${wordIds.length}개의 단어에 대해 임베딩을 생성하시겠습니까?\n이 작업은 시간이 오래 걸릴 수 있습니다.`;
    
    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await genWordEmbeddings(wordIds);
      alert(`${wordIds.length}개의 단어에 대한 임베딩이 성공적으로 생성되었습니다.`);
      // 임베딩 생성 후 현재 필터 조건으로 다시 검색하여 상태 업데이트
      await handleFilter();
    } catch (err) {
      setError('임베딩 생성 중 오류가 발생했습니다: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // offset이 변경될 때마다 필터링 재실행
  useEffect(() => {
    if (filterData.offset > 0 || words.length > 0) {
      handleFilter();
    }
  }, [filterData.offset]);

  return (
    <div className="filter-words-container">
      <h1>단어 필터링</h1>
      
      {/* 필터 조건 입력 폼 */}
      <div className="filter-form">
        <div className="filter-section">
          <h3>레벨 선택</h3>
          <div className="level-checkboxes">
            {levelOptions.map(level => (
              <label key={level} className="level-checkbox">
                <input
                  type="checkbox"
                  checked={filterData.levels.includes(level)}
                  onChange={() => handleLevelToggle(level)}
                />
                {level}
              </label>
            ))}
          </div>
        </div>

        <div className="filter-section">
          <h3>예문 수</h3>
          <div className="range-inputs">
            <input
              type="number"
              placeholder="최소"
              value={filterData.min_examples}
              onChange={(e) => handleFilterChange('min_examples', e.target.value)}
              min="0"
            />
            <span>~</span>
            <input
              type="number"
              placeholder="최대"
              value={filterData.max_examples}
              onChange={(e) => handleFilterChange('max_examples', e.target.value)}
              min="0"
            />
          </div>
        </div>

        <div className="filter-section">
          <h3>Embedding 보유 여부</h3>
          <select
            value={filterData.has_embedding === null ? '' : filterData.has_embedding.toString()}
            onChange={(e) => handleFilterChange('has_embedding', e.target.value === '' ? null : e.target.value === 'true')}
          >
            <option value="">상관없음</option>
            <option value="true">보유</option>
            <option value="false">미보유</option>
          </select>
        </div>

        <div className="filter-section">
          <h3>결과 수 제한</h3>
          <input
            type="number"
            value={filterData.limit}
            onChange={(e) => handleFilterChange('limit', parseInt(e.target.value) || 100)}
            min="1"
            max="1000"
          />
        </div>

        <div className="filter-actions">
          <button onClick={handleFilter} disabled={loading} className="filter-btn">
            {loading ? '필터링 중...' : '필터링 실행'}
          </button>
          <button onClick={handleReset} className="reset-btn">
            초기화
          </button>
        </div>
      </div>

      {/* 결과 정보 */}
      {totalCount > 0 && (
        <div className="result-info">
          <p>총 {totalCount}개의 단어가 검색되었습니다. (현재 {words.length}개 표시)</p>
        </div>
      )}

      {/* 에러 메시지 */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 결과 테이블 */}
      {words.length > 0 && (
        <div className="results-section">
          {/* 임베딩 생성 버튼 */}
          <div className="embedding-actions">
            <button 
              onClick={handleGenerateEmbeddings} 
              disabled={loading} 
              className="generate-embeddings-btn"
            >
              {loading ? '임베딩 생성 중...' : `현재 ${words.length}개 단어 임베딩 생성`}
            </button>
          </div>
          
          <EditableTable
            columns={columns}
            data={words}
            onDataChange={setWords}
            onUpdate={handleUpdateWords}
            onDelete={handleDeleteWords}
            onCellClick={handleCellClick}
            showAddRow={false}
            showPasteButton={false}
            showCopyButton={true}
            showDeleteButton={true}
            addRowText=""
            deleteRowText="삭제"
          />
          
          {/* 페이지네이션 */}
          <div className="pagination">
            <button
              onClick={() => handlePageChange(Math.max(0, filterData.offset - filterData.limit))}
              disabled={filterData.offset === 0}
            >
              이전
            </button>
            <span>
              페이지 {Math.floor(filterData.offset / filterData.limit) + 1} 
              ({(filterData.offset + 1)}-{Math.min(filterData.offset + filterData.limit, totalCount)} / {totalCount})
            </span>
            <button
              onClick={() => handlePageChange(filterData.offset + filterData.limit)}
              disabled={filterData.offset + filterData.limit >= totalCount}
            >
              다음
            </button>
          </div>
        </div>
      )}

      {/* 결과가 없을 때 */}
      {!loading && words.length === 0 && totalCount === 0 && !error && (
        <div className="no-results">
          <p>필터 조건을 설정하고 "필터링 실행" 버튼을 클릭하세요.</p>
        </div>
      )}

      {/* 단어 상세 모달 */}
      <WordDetailModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        wordId={selectedWordId}
      />
    </div>
  );
};

export default FilterWords;
