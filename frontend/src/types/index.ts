export interface Monitor {
  id: number;
  name: string;
  url: string;
  interval_minutes: number;
  is_active: boolean;
  created_at: string;
  last_checked_at: string | null;
  current_status: "up" | "down" | "unknown";
  consecutive_failures: number;
  notify_email: string | null;
  telegram_chat_id: string | null;
}

export interface MonitorCreate {
  name: string;
  url: string;
  interval_minutes: number;
  notify_email?: string;
  telegram_chat_id?: string;
}

export interface Check {
  id: number;
  monitor_id: number;
  checked_at: string;
  status_code: number | null;
  response_time_ms: number | null;
  is_up: boolean;
  error_message: string | null;
}

export interface MonitorStats {
  monitor_id: number;
  period_days: number;
  total_checks: number;
  successful_checks: number;
  uptime_percentage: number;
  avg_response_time_ms: number | null;
}
