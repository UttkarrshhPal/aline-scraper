import axios from "axios";

// Use import.meta.env for Vite projects
export const API_BASE_URL = import.meta.env.BACKEND_URL || "http://localhost:8000";

export async function scrapeBlogGuide(data: Record<string, unknown>) {
  return axios.post(`${API_BASE_URL}/scrape`, data);
}

export async function getScrapeStatus(jobId: string) {
  return axios.get(`${API_BASE_URL}/scrape/${jobId}/status`);
}

export async function getScrapeResults(jobId: string) {
  return axios.get(`${API_BASE_URL}/scrape/${jobId}/results`);
}

export async function scrapePdf(formData: FormData) {
  return axios.post(`${API_BASE_URL}/scrape/pdf`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
