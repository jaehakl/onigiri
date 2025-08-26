import axios from 'axios';
export const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
axios.defaults.withCredentials = true;

// === OAuth ===
export async function fetchMe() {
    return axios.get(`${API_URL}/auth/me`)
    .then(res => res.data)
    .catch(err => {
        return null;
    });

}  
export function startGoogleLogin() {
  const returnTo = window.location.href;
  // 백엔드로 바로 리다이렉트(백엔드가 구글로 다시 리다이렉트)
  window.location.href = `${API_URL}/auth/google/start?return_to=${encodeURIComponent(returnTo)}`;
}
export async function logout() {
  await fetch(`${API_URL}/auth/logout`, { method: "POST", credentials: "include" });
}
// === Words CRUD ===
export const createWordsBatch = (wordsData) => axios.post(`${API_URL}/words/create/batch`, wordsData);
export const updateWordsBatch = (wordsData) => axios.post(`${API_URL}/words/update/batch`, wordsData);
export const deleteWordsBatch = (wordIds) => axios.post(`${API_URL}/words/delete/batch`, wordIds);
export const getAllWords = (limit = null, offset = null) => axios.post(`${API_URL}/words/all`, { limit, offset });
export const searchWordsByWord = (searchTerm) => axios.get(`${API_URL}/words/search/${encodeURIComponent(searchTerm)}`);
export const getRandomWords = (count = 50) => axios.get(`${API_URL}/words/random/${count}`);

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

// === Quiz Records ===
//export const saveQuizRecord = (quizRecord) => axios.post(`${API_URL}/quiz/record`, quizRecord);
//export const getQuizRecords = (filters = {}) => axios.post(`${API_URL}/quiz/records`, filters);
//export const getQuizStatistics = (filters = {}) => axios.post(`${API_URL}/quiz/statistics`, filters);

