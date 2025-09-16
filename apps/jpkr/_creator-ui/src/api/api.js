import axios from 'axios';
export const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
axios.defaults.withCredentials = true;
console.log(API_URL);


// === Test API ===
export const getSimilarWords = (wordId) => axios.get(`${API_URL}/test/get-similar-words/${wordId}`);
export const getSimilarExamples = (exampleId) => axios.get(`${API_URL}/test/get-similar-examples/${exampleId}`);

// === Admin API ===
export const getDuplicatedWords = () => axios.get(`${API_URL}/admin/words/get-duplicated`);
export const mergeDuplicatedWords = (wordIds, newWordData) => axios.post(`${API_URL}/admin/words/merge-duplicated`, { word_ids: wordIds, new_word_data: newWordData });

export const genWordEmbeddings = (wordIds) => axios.post(`${API_URL}/admin/words/gen-embeddings`, wordIds);
export const genExampleEmbeddings = (exampleIds) => axios.post(`${API_URL}/admin/examples/gen-embeddings`, exampleIds);
export const genExampleAudio = (exampleIds) => axios.post(`${API_URL}/admin/examples/gen-audio`, exampleIds);
export const genExampleImage = (exampleIds) => axios.post(`${API_URL}/admin/examples/gen-image`, exampleIds);
export const genExampleWords = (exampleIds) => axios.post(`${API_URL}/admin/examples/gen-words`, exampleIds);

export const updateWordsBatch = (wordsData) => axios.post(`${API_URL}/admin/words/update/batch`, wordsData);
export const updateExamplesBatch = (examplesData) => axios.post(`${API_URL}/admin/examples/update/batch`, examplesData);
export const deleteWordsBatch = (wordIds) => axios.post(`${API_URL}/admin/words/delete/batch`, wordIds);
export const deleteExamplesBatch = (exampleIds) => axios.post(`${API_URL}/admin/examples/delete/batch`, exampleIds);
export const filterWords = (wordFilterData) => axios.post(`${API_URL}/admin/words/filter`, wordFilterData);
export const filterExamples = (exampleFilterData) => {
  console.log(exampleFilterData);
  console.log(API_URL);
  console.log(`${API_URL}/admin/examples/filter`);
  return axios.post(`${API_URL}/admin/examples/filter`, exampleFilterData)};
