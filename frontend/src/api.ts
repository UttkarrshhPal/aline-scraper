import axios from "axios";

export const API_BASE_URL = process.env.BACKEND_URL || "http://localhost:8000";

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
