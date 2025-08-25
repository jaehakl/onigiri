import axios from 'axios';
const API_URL = 'http://localhost:8000';

// === Words CRUD ===
export const createWordsBatch = (wordsData) => axios.post(`${API_URL}/words/create/batch`, wordsData);
export const readWordsBatch = (wordIds) => axios.post(`${API_URL}/words/read/batch`, wordIds);
export const updateWordsBatch = (wordsData) => axios.post(`${API_URL}/words/update/batch`, wordsData);
export const deleteWordsBatch = (wordIds) => axios.post(`${API_URL}/words/delete/batch`, wordIds);
export const getAllWords = (limit = null, offset = null) => axios.post(`${API_URL}/words/all`, { limit, offset });
export const searchWordsByWord = (searchTerm) => axios.get(`${API_URL}/words/search/${encodeURIComponent(searchTerm)}`);

// === Examples CRUD ===
export const createExamplesBatch = (examplesData) => axios.post(`${API_URL}/examples/create/batch`, examplesData);
export const readExamplesBatch = (exampleIds) => axios.post(`${API_URL}/examples/read/batch`, exampleIds);
export const updateExamplesBatch = (examplesData) => axios.post(`${API_URL}/examples/update/batch`, examplesData);
export const deleteExamplesBatch = (exampleIds) => axios.post(`${API_URL}/examples/delete/batch`, exampleIds);
export const getAllExamples = (limit = null, offset = null) => axios.post(`${API_URL}/examples/all`, { limit, offset });
export const searchExamplesByText = (searchTerm) => axios.get(`${API_URL}/examples/search/${encodeURIComponent(searchTerm)}`);
export const getExamplesByWordId = (wordId) => axios.get(`${API_URL}/examples/word/${wordId}`);

// === Text Analysis ===
export const analyzeText = (text) => axios.post(`${API_URL}/text/analyze`, { text });

