import React, { useState } from "react";
import type { MonitorCreate } from "../types";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface AddMonitorModalProps {
  onAdd: (monitor: MonitorCreate) => void;
}

export function AddMonitorModal({ onAdd }: AddMonitorModalProps) {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<MonitorCreate>({
    name: "",
    url: "https://",
    interval_minutes: 5,
    notify_email: "",
    telegram_chat_id: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAdd({
      ...formData,
      notify_email: formData.notify_email || undefined,
      telegram_chat_id: formData.telegram_chat_id || undefined,
    });
    setOpen(false);
    // Reset form
    setFormData({
      name: "",
      url: "https://",
      interval_minutes: 5,
      notify_email: "",
      telegram_chat_id: "",
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>+ Add Monitor</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Monitor</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              placeholder="e.g. Production API"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="url">URL</Label>
            <Input
              id="url"
              type="url"
              placeholder="https://api.example.com/health"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="interval">Check Interval (minutes)</Label>
            <Input
              id="interval"
              type="number"
              min="1"
              value={formData.interval_minutes}
              onChange={(e) => setFormData({ ...formData, interval_minutes: parseInt(e.target.value) || 5 })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Alert Email (Optional)</Label>
            <Input
              id="email"
              type="email"
              placeholder="alerts@company.com"
              value={formData.notify_email}
              onChange={(e) => setFormData({ ...formData, notify_email: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="telegram">Telegram Chat ID (Optional)</Label>
            <Input
              id="telegram"
              placeholder="-100123456789"
              value={formData.telegram_chat_id}
              onChange={(e) => setFormData({ ...formData, telegram_chat_id: e.target.value })}
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Save Monitor</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
