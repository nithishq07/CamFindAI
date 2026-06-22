import { useEffect, useState } from 'react';
import { apiClient, fetchAlerts } from '../api/client';
import type { Alert as AlertType } from '../api/client';
import { useAlertsWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../contexts/AuthContext';
import { Bell, AlertTriangle, Info, CheckCircle2, CheckCircle } from 'lucide-react';
import clsx from 'clsx';
import { formatDistanceToNow } from 'date-fns';

export function Alerts() {
  const [historicalAlerts, setHistoricalAlerts] = useState<AlertType[]>([]);
  const liveAlerts = useAlertsWebSocket();
  const { user } = useAuth();
  
  const canAck = user?.role === 'admin' || user?.role === 'operator';

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = () => {
    fetchAlerts().then(setHistoricalAlerts).catch(console.error);
  };

  const handleUpdateStatus = async (id: number, status: string) => {
    try {
      await apiClient.patch(`/alerts/${id}`, { status });
      loadAlerts();
    } catch (e) {
      console.error('Failed to update alert', e);
    }
  };

  const allAlerts = [...liveAlerts, ...historicalAlerts].filter((v,i,a)=>a.findIndex(t=>(t.id === v.id))===i).sort((a,b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <div className="h-full flex flex-col space-y-6 animate-in fade-in duration-500">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Security Alerts</h2>
        <p className="text-muted-foreground mt-1">Real-time notifications for restricted zones and loitering.</p>
      </div>

      <div className="glass-panel rounded-xl border border-white/5 overflow-hidden flex-1 flex flex-col p-4 space-y-4">
        {allAlerts.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
            <Bell className="w-12 h-12 mb-4 opacity-20" />
            <p>No active alerts.</p>
          </div>
        ) : (
          allAlerts.map(alert => (
            <div key={alert.id || Math.random()} className="flex items-start gap-4 p-4 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
              <div className={clsx(
                "p-2 rounded-full",
                alert.severity === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
              )}>
                {alert.severity === 'high' ? <AlertTriangle className="w-5 h-5" /> : <Info className="w-5 h-5" />}
              </div>
              <div className="flex-1">
                <div className="flex justify-between">
                  <h4 className="font-medium text-white">{alert.alert_type}</h4>
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">{alert.message}</p>
                <div className="flex gap-2 mt-3">
                  <span className="px-2 py-1 text-[10px] uppercase font-bold bg-white/10 rounded">CAM-{alert.camera_id}</span>
                  {alert.global_id && (
                    <span className="px-2 py-1 text-[10px] uppercase font-bold bg-white/10 rounded font-mono text-white/70">
                      ID: {alert.global_id.split('-')[0]}
                    </span>
                  )}
                  <span className={clsx(
                    "px-2 py-1 text-[10px] uppercase font-bold rounded",
                    alert.status === 'open' ? 'bg-red-500/20 text-red-400' :
                    alert.status === 'acknowledged' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-green-500/20 text-green-400'
                  )}>
                    {alert.status || 'OPEN'}
                  </span>
                </div>
              </div>
              
              {canAck && (alert.status === 'open' || alert.status === 'acknowledged' || !alert.status) && (
                <div className="flex flex-col gap-2 ml-4">
                  {(alert.status === 'open' || !alert.status) && (
                    <button 
                      onClick={() => handleUpdateStatus(alert.id, 'acknowledged')}
                      className="px-3 py-1.5 text-xs font-medium bg-white/10 hover:bg-white/20 rounded flex items-center gap-1.5 transition-colors"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      Ack
                    </button>
                  )}
                  <button 
                    onClick={() => handleUpdateStatus(alert.id, 'resolved')}
                    className="px-3 py-1.5 text-xs font-medium bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded flex items-center gap-1.5 transition-colors"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Resolve
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
