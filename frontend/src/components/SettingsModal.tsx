import React, { useState, useEffect } from "react";
import type { AppSettings } from "../types";
import { fetchGlobalSettings, updateGlobalSettings } from "@/api/client";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings } from "lucide-react";
import { Setup2FAModal } from "./Setup2FAModal";

export function SettingsModal() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<AppSettings>>({
    telegram_bot_token: "",
    telegram_chat_id: "",
    smtp_host: "smtp.gmail.com",
    smtp_port: 587,
    smtp_user: "",
    smtp_pass: "",
    alert_email: "",
  });

  const loadSettings = async () => {
    try {
      const data = await fetchGlobalSettings();
      setFormData({
        telegram_bot_token: data.telegram_bot_token || "",
        telegram_chat_id: data.telegram_chat_id || "",
        smtp_host: data.smtp_host || "smtp.gmail.com",
        smtp_port: data.smtp_port || 587,
        smtp_user: data.smtp_user || "",
        smtp_pass: data.smtp_pass || "",
        alert_email: data.alert_email || "",
      });
    } catch (err) {
      console.error("Failed to load settings", err);
    }
  };

  useEffect(() => {
    if (open) {
      loadSettings();
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updateGlobalSettings(formData);
      setOpen(false);
    } catch (err) {
      console.error("Failed to save settings", err);
      alert("Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="rounded-full">
          <Settings className="h-5 w-5" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px] max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Global Notification Settings</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
          
          <div className="space-y-4">
            <h3 className="text-sm font-medium border-b pb-2">Telegram Integration</h3>
            <div className="space-y-2">
              <Label htmlFor="telegram_bot_token">Bot Token</Label>
              <Input
                id="telegram_bot_token"
                type="password"
                placeholder="123456789:ABCdefGHIjklMNOpqrSTUvwxyz"
                value={formData.telegram_bot_token}
                onChange={(e) => setFormData({ ...formData, telegram_bot_token: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="telegram_chat_id">Global Chat ID (Fallback)</Label>
              <Input
                id="telegram_chat_id"
                placeholder="-100123456789"
                value={formData.telegram_chat_id}
                onChange={(e) => setFormData({ ...formData, telegram_chat_id: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-medium border-b pb-2">Email (SMTP) Integration</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="smtp_host">SMTP Host</Label>
                <Input
                  id="smtp_host"
                  placeholder="smtp.gmail.com"
                  value={formData.smtp_host}
                  onChange={(e) => setFormData({ ...formData, smtp_host: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp_port">SMTP Port</Label>
                <Input
                  id="smtp_port"
                  type="number"
                  value={formData.smtp_port}
                  onChange={(e) => setFormData({ ...formData, smtp_port: parseInt(e.target.value) || 587 })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="smtp_user">SMTP User (Email)</Label>
              <Input
                id="smtp_user"
                placeholder="alerts@company.com"
                value={formData.smtp_user}
                onChange={(e) => setFormData({ ...formData, smtp_user: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="smtp_pass">SMTP Password (App Password)</Label>
              <Input
                id="smtp_pass"
                type="password"
                placeholder="••••••••••••••••"
                value={formData.smtp_pass}
                onChange={(e) => setFormData({ ...formData, smtp_pass: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="alert_email">Global Target Email (Fallback)</Label>
              <Input
                id="alert_email"
                type="email"
                placeholder="oncall@company.com"
                value={formData.alert_email}
                onChange={(e) => setFormData({ ...formData, alert_email: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-medium border-b pb-2">Security</h3>
            <Setup2FAModal />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : "Save Settings"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
