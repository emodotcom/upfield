import React, { useState, useEffect } from "react";
import type { Monitor, MonitorCreate } from "../types";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Pencil } from "lucide-react";

interface EditMonitorModalProps {
  monitor: Monitor;
  onEdit: (id: number, payload: Partial<MonitorCreate>) => void;
}

export function EditMonitorModal({ monitor, onEdit }: EditMonitorModalProps) {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: monitor.name,
    url: monitor.url,
    interval_minutes: monitor.interval_minutes,
    notify_email: monitor.notify_email || "",
    telegram_chat_id: monitor.telegram_chat_id || "",
  });

  // Reset form when modal opens in case monitor data changed
  useEffect(() => {
    if (open) {
      setFormData({
        name: monitor.name,
        url: monitor.url,
        interval_minutes: monitor.interval_minutes,
        notify_email: monitor.notify_email || "",
        telegram_chat_id: monitor.telegram_chat_id || "",
      });
    }
  }, [open, monitor]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onEdit(monitor.id, {
      name: formData.name,
      url: formData.url,
      interval_minutes: formData.interval_minutes,
      notify_email: formData.notify_email || undefined,
      telegram_chat_id: formData.telegram_chat_id || undefined,
    });
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-primary">
          <Pencil className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Monitor</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label htmlFor={`edit-name-${monitor.id}`}>Name</Label>
            <Input
              id={`edit-name-${monitor.id}`}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor={`edit-url-${monitor.id}`}>URL</Label>
            <Input
              id={`edit-url-${monitor.id}`}
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor={`edit-interval-${monitor.id}`}>Check Interval (minutes)</Label>
            <Input
              id={`edit-interval-${monitor.id}`}
              type="number"
              min="1"
              value={formData.interval_minutes}
              onChange={(e) => setFormData({ ...formData, interval_minutes: parseInt(e.target.value) || 5 })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor={`edit-email-${monitor.id}`}>Alert Email (Optional)</Label>
            <Input
              id={`edit-email-${monitor.id}`}
              type="email"
              value={formData.notify_email}
              onChange={(e) => setFormData({ ...formData, notify_email: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor={`edit-telegram-${monitor.id}`}>Telegram Chat ID (Optional)</Label>
            <Input
              id={`edit-telegram-${monitor.id}`}
              value={formData.telegram_chat_id}
              onChange={(e) => setFormData({ ...formData, telegram_chat_id: e.target.value })}
            />
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Save Changes</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
