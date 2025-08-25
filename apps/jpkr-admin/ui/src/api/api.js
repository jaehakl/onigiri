import axios from 'axios';
const API_URL = 'http://localhost:8000';

// === Words CRUD ===
export const createWordsBatch = (wordsData) => axios.post(`${API_URL}/words/create/batch`, wordsData);
export const readWordsBatch = (wordIds) => axios.post(`${API_URL}/words/read/batch`, wordIds);
export const updateWordsBatch = (wordsData) => axios.post(`${API_URL}/words/update/batch`, wordsData);
export const deleteWordsBatch = (wordIds) => axios.post(`${API_URL}/words/delete/batch`, wordIds);
export const getAllWords = (limit = null, offset = null) => axios.post(`${API_URL}/words/all`, { limit, offset });
export const searchWordsByWord = (searchTerm) => axios.get(`${API_URL}/words/search/${searchTerm}`);

