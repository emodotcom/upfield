import { useEffect, useState } from "react";
import type { Monitor, MonitorCreate } from "../types";
import { fetchMonitors, createMonitor, deleteMonitor, triggerCheck, updateMonitor } from "@/api/client";
import { MonitorCard } from "@/components/MonitorCard";
import { AddMonitorModal } from "@/components/AddMonitorModal";
import { SettingsModal } from "@/components/SettingsModal";
import { Activity, Radio, AlertCircle, CheckCircle2, Moon, Sun, LogOut } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/theme-provider";

export function Dashboard() {
  const { theme, setTheme } = useTheme();
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const handleLogout = () => {
    localStorage.removeItem("upfield_token");
    window.location.href = "/login";
  };

  const loadMonitors = async () => {
    try {
      const data = await fetchMonitors();
      setMonitors(data);
      setError("");
    } catch (err) {
      setError("Failed to load monitors. Is the backend running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMonitors();
    const interval = setInterval(loadMonitors, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleAddMonitor = async (payload: any) => {
    try {
      await createMonitor(payload);
      await loadMonitors();
    } catch (err) {
      console.error("Failed to add monitor", err);
      alert("Failed to add monitor");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this monitor?")) return;
    try {
      await deleteMonitor(id);
      await loadMonitors();
    } catch (err) {
      console.error("Failed to delete", err);
    }
  };

  const handleEdit = async (id: number, payload: Partial<MonitorCreate>) => {
    try {
      await updateMonitor(id, payload);
      await loadMonitors();
    } catch (err) {
      console.error("Failed to update monitor", err);
      alert("Failed to update monitor");
    }
  };

  const handleTriggerCheck = async (id: number) => {
    try {
      await triggerCheck(id);
      setTimeout(loadMonitors, 1000);
    } catch (err) {
      console.error("Failed to trigger check", err);
    }
  };

  const upCount = monitors.filter((m) => m.current_status === "up").length;
  const downCount = monitors.filter((m) => m.current_status === "down").length;

  return (
    <div className="container mx-auto py-10 px-4 max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-3">
          <div className="bg-primary/10 text-primary p-2.5 rounded-xl">
            <Activity className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Upfield</h1>
            <p className="text-muted-foreground text-sm mt-1">Uptime & Health Monitoring</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <SettingsModal />
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            className="rounded-full"
            title="Toggle Theme"
          >
            {theme === "light" ? <Moon className="h-5 w-5 text-slate-700" /> : <Sun className="h-5 w-5 text-slate-300" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className="rounded-full text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
            title="Logout"
          >
            <LogOut className="h-5 w-5" />
          </Button>
          <AddMonitorModal onAdd={handleAddMonitor} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card className="rounded-xl border border-slate-200/60 dark:border-slate-800/60 shadow-sm border-t-[3px] border-t-blue-500">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 text-blue-500 rounded-full">
              <Radio className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Monitors</p>
              <h2 className="text-3xl font-bold">{monitors.length}</h2>
            </div>
          </CardContent>
        </Card>
        <Card className="rounded-xl border border-slate-200/60 dark:border-slate-800/60 shadow-sm border-t-[3px] border-t-green-500">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-green-500/10 text-green-600 rounded-full">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Operational</p>
              <h2 className="text-3xl font-bold">{upCount}</h2>
            </div>
          </CardContent>
        </Card>
        <Card className="rounded-xl border border-slate-200/60 dark:border-slate-800/60 shadow-sm border-t-[3px] border-t-destructive">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-destructive/10 text-destructive rounded-full">
              <AlertCircle className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Down</p>
              <h2 className="text-3xl font-bold">{downCount}</h2>
            </div>
          </CardContent>
        </Card>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive p-4 rounded-lg mb-8 flex items-center gap-3">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      )}

      {loading && monitors.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground">
          <Activity className="h-8 w-8 animate-pulse mx-auto mb-4 opacity-50" />
          Loading your monitors...
        </div>
      ) : monitors.length === 0 ? (
        <div className="text-center py-24 border-2 border-dashed rounded-xl bg-muted/10">
          <Radio className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No monitors yet</h3>
          <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
            You haven't added any URLs to monitor. Click the button below or in the top right to get started.
          </p>
          <AddMonitorModal onAdd={handleAddMonitor} />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {monitors.map((monitor) => (
            <MonitorCard
              key={monitor.id}
              monitor={monitor}
              onDelete={handleDelete}
              onCheck={handleTriggerCheck}
              onEdit={handleEdit}
            />
          ))}
        </div>
      )}
    </div>
  );
}
