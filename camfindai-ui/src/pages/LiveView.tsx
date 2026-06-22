import { useState, useEffect } from 'react';
import { useLiveFeed } from '../hooks/useWebSocket';
import { apiClient } from '../api/client';
import { Camera, Users, AlertTriangle, Activity } from 'lucide-react';

export function LiveView() {
  const [cameras, setCameras] = useState<any[]>([]);

  useEffect(() => {
    // Fetch online cameras
    apiClient.get('/cameras').then(res => {
      setCameras(res.data.filter((c: any) => c.status === 'online'));
    }).catch(console.error);
  }, []);

  return (
    <div className="h-full flex flex-col space-y-6 animate-in fade-in duration-500 overflow-y-auto pb-10">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Live Operations</h2>
        <p className="text-muted-foreground mt-1">Real-time surveillance and tracking feeds.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard icon={Camera} label="Active Cameras" value={cameras.length.toString()} trend="Online" />
        <StatCard icon={Users} label="Current Tracks" value="-" trend="Live" />
        <StatCard icon={AlertTriangle} label="Active Alerts" value="0" trend="Clear" />
        <StatCard icon={Activity} label="System Load" value="24%" trend="Normal" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 auto-rows-max">
        {cameras.length === 0 ? (
          <div className="col-span-full flex flex-col items-center justify-center py-20 text-muted-foreground glass-panel border border-white/5 rounded-xl">
             <Camera className="w-12 h-12 mb-4 opacity-20" />
             <p className="text-sm font-medium">No cameras currently online.</p>
             <p className="text-xs opacity-50 mt-1">Go to the Cameras tab to start a stream.</p>
          </div>
        ) : (
          cameras.map(cam => (
            <CameraFeed key={cam.id} camera={cam} />
          ))
        )}
      </div>
    </div>
  );
}

function CameraFeed({ camera }: { camera: any }) {
  const { frame, activeTracks } = useLiveFeed(camera.id);

  return (
    <div className="glass-panel rounded-xl overflow-hidden flex flex-col border border-white/5 shadow-xl relative aspect-video">
      <div className="p-3 border-b border-white/5 flex items-center justify-between bg-black/40 absolute top-0 w-full z-10 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.6)]" />
          <h3 className="font-semibold text-sm text-white drop-shadow-md">CAM-{camera.id} {camera.name}</h3>
        </div>
        <div className="text-xs font-mono text-green-400 drop-shadow-md bg-black/40 px-2 py-0.5 rounded">
          {activeTracks} TRACKS
        </div>
      </div>
      
      <div className="flex-1 bg-black relative flex items-center justify-center overflow-hidden">
        {frame ? (
          <img 
            src={frame} 
            alt="Live Feed" 
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="flex flex-col items-center text-muted-foreground">
            <Camera className="w-8 h-8 mb-4 opacity-20" />
            <p className="text-xs font-medium">Waiting for video stream...</p>
          </div>
        )}
      </div>
    </div>
  );
}
            


function StatCard({ icon: Icon, label, value, trend }: any) {
  return (
    <div className="glass-panel p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors group">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">{label}</p>
        <div className="p-2 bg-white/5 rounded-lg group-hover:bg-white/10 transition-colors">
          <Icon className="w-4 h-4 text-white" />
        </div>
      </div>
      <div className="mt-4 flex items-baseline justify-between">
        <h4 className="text-3xl font-bold tracking-tight">{value}</h4>
        <span className="text-xs font-medium text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full">
          {trend}
        </span>
      </div>
    </div>
  );
}
