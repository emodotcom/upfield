import axios from "axios";
import type { Monitor, MonitorCreate, Check, MonitorStats, AppSettings } from "../types";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// Interceptor to attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("upfield_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle 401 Unauthorized globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("upfield_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (data: any) => {
    const response = await api.post("/auth/login", data);
    return response.data;
  },
  verify2FA: async (data: any) => {
    const response = await api.post("/auth/verify-2fa", data);
    return response.data;
  },
  setup2FA: async () => {
    const response = await api.get("/auth/setup-2fa");
    return response.data;
  },
  enable2FA: async (code: string) => {
    const response = await api.post("/auth/enable-2fa", { code });
    return response.data;
  },
  changePassword: async (data: any) => {
    const response = await api.put("/auth/change-password", data);
    return response.data;
  }
};

export async function fetchMonitors(): Promise<Monitor[]> {
  const { data } = await api.get("/monitors/");
  return data;
}

export async function fetchMonitor(id: number): Promise<Monitor> {
  const { data } = await api.get(`/monitors/${id}`);
  return data;
}

export async function createMonitor(payload: MonitorCreate): Promise<Monitor> {
  const { data } = await api.post("/monitors/", payload);
  return data;
}

export async function updateMonitor(
  id: number,
  payload: Partial<MonitorCreate>
): Promise<Monitor> {
  const { data } = await api.put(`/monitors/${id}`, payload);
  return data;
}

export async function deleteMonitor(id: number): Promise<void> {
  await api.delete(`/monitors/${id}`);
}

export async function triggerCheck(id: number): Promise<void> {
  await api.post(`/monitors/${id}/check`);
}

export async function fetchChecks(
  id: number,
  limit = 100
): Promise<Check[]> {
  const { data } = await api.get(`/monitors/${id}/checks`, {
    params: { limit },
  });
  return data;
}

export async function fetchStats(
  id: number,
  days = 1
): Promise<MonitorStats> {
  const { data } = await api.get(`/monitors/${id}/stats`, {
    params: { days },
  });
  return data;
}

export async function fetchGlobalSettings(): Promise<AppSettings> {
  const { data } = await api.get("/settings/");
  return data;
}

export async function updateGlobalSettings(payload: Partial<AppSettings>): Promise<AppSettings> {
  const { data } = await api.put("/settings/", payload);
  return data;
}
