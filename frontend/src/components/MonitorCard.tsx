import type { Monitor } from "../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Activity, Clock, Trash2, ExternalLink, Globe } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface MonitorCardProps {
  monitor: Monitor;
  onDelete: (id: number) => void;
  onCheck: (id: number) => void;
}

export function MonitorCard({ monitor, onDelete, onCheck }: MonitorCardProps) {
  const isUp = monitor.current_status === "up";
  const isDown = monitor.current_status === "down";

  return (
    <Card className="hover:shadow-md transition-all duration-200 border-muted">
      <CardHeader className="pb-2 border-b bg-muted/20">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-md ${isUp ? 'bg-green-500/10 text-green-600' : isDown ? 'bg-destructive/10 text-destructive' : 'bg-muted text-muted-foreground'}`}>
              <Globe className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-semibold">{monitor.name}</CardTitle>
              <a href={monitor.url} target="_blank" rel="noreferrer" className="text-xs text-muted-foreground hover:text-primary hover:underline flex items-center gap-1 mt-0.5">
                {monitor.url} <ExternalLink className="h-2.5 w-2.5" />
              </a>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isUp && (
              <span className="flex items-center gap-2 text-sm font-medium text-green-600">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                </span>
                Operational
              </span>
            )}
            {isDown && (
              <span className="flex items-center gap-2 text-sm font-medium text-destructive">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-destructive"></span>
                </span>
                Down
              </span>
            )}
            {!isUp && !isDown && (
              <span className="text-sm font-medium text-muted-foreground">Unknown</span>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-4">
        <div className="flex justify-between items-center">
          <div className="flex gap-6">
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground flex items-center gap-1 mb-1">
                <Clock className="h-3.5 w-3.5" /> Interval
              </span>
              <span className="text-sm font-medium">{monitor.interval_minutes} minutes</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground flex items-center gap-1 mb-1">
                <Activity className="h-3.5 w-3.5" /> Last Checked
              </span>
              <span className="text-sm font-medium">
                {monitor.last_checked_at
                  ? formatDistanceToNow(new Date(monitor.last_checked_at), { addSuffix: true })
                  : "Never"}
              </span>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button variant="secondary" size="sm" onClick={() => onCheck(monitor.id)}>
              Ping
            </Button>
            <Button variant="ghost" size="sm" onClick={() => onDelete(monitor.id)} className="text-destructive hover:bg-destructive/10">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
