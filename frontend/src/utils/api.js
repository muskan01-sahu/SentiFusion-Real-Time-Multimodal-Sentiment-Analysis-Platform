import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 180000,
  headers: { "Content-Type": "application/json" },
});

export const analyzeTweet = async (tweetUrl, includeReplies = false) => {
  const { data } = await api.post("/analyze", {
    tweet_url: tweetUrl,
    include_replies: includeReplies,
  });
  return data;
};

export const getHistory = async (limit = 20, offset = 0) => {
  const { data } = await api.get(`/history?limit=${limit}&offset=${offset}`);
  return data;
};

export const getAnalysis = async (id) => {
  const { data } = await api.get(`/history/${id}`);
  return data;
};

export const deleteAnalysis = async (id) => {
  const { data } = await api.delete(`/history/${id}`);
  return data;
};

export default api;
