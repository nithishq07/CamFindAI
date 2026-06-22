import { useState, useEffect } from 'react';
import { Camera as CameraIcon, Plus, Play, Square, Trash2, Activity } from 'lucide-react';
import { apiClient } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import clsx from 'clsx';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  location: z.string().optional(),
  source_type: z.enum(['WEBCAM', 'IP_CAMERA', 'RTSP']),
  stream_url: z.string().min(1, "Stream URL is required")
});

type FormData = z.infer<typeof schema>;

interface CameraHealth {
  timestamp: string;
  fps: number;
  status: string;
}

interface Camera {
  id: number;
  name: string;
  location: string;
  source_type: string;
  stream_url: string;
  status: string;
  fps: number;
  health: CameraHealth[];
}

export function CameraManagement() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', location: '', source_type: 'WEBCAM', stream_url: '' }
  });
  
  const watchedSourceType = watch('source_type');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchCameras = async () => {
    try {
      const res = await apiClient.get('/cameras');
      const camerasWithHealth = await Promise.all(
        res.data.map(async (cam: Camera) => {
          try {
            const healthRes = await apiClient.get(`/cameras/${cam.id}/health-history?range=1h`);
            return { ...cam, health: healthRes.data };
          } catch {
            return { ...cam, health: [] };
          }
        })
      );
      setCameras(camerasWithHealth);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAdd = async (data: FormData) => {
    try {
      await apiClient.post('/cameras', data);
      setIsFormOpen(false);
      reset();
      fetchCameras();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure?")) return;
    try {
      await apiClient.delete(`/cameras/${id}`);
      fetchCameras();
    } catch (e) {
      console.error(e);
    }
  };

  const handleStart = async (id: number) => {
    try {
      await apiClient.post(`/cameras/${id}/start`);
      fetchCameras();
    } catch (e) {
      console.error(e);
    }
  };

  const handleStop = async (id: number) => {
    try {
      await apiClient.post(`/cameras/${id}/stop`);
      fetchCameras();
    } catch (e) {
      console.error(e);
    }
  };

  const handleTest = async (id: number) => {
    setTesting(true);
    setTestResult('Testing connection...');
    try {
      const res = await apiClient.post(`/cameras/${id}/test`);
      setTestResult(`Status: ${res.data.status.toUpperCase()}, FPS: ${res.data.fps.toFixed(1)}`);
    } catch (e) {
      setTestResult("Test failed. Could not reach stream.");
    }
    setTesting(false);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white font-space">Camera Sources</h1>
          <p className="text-muted-foreground mt-1">Manage active RTSP, IP, and Webcam feeds.</p>
        </div>
        {isAdmin && (
          <button 
            onClick={() => setIsFormOpen(!isFormOpen)}
            className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Camera
          </button>
        )}
      </div>

      {isFormOpen && (
        <div className="glass-panel p-6 border border-white/10 rounded-xl">
          <h2 className="text-xl font-semibold text-white mb-4">Add New Camera</h2>
          <form onSubmit={handleSubmit(handleAdd)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">Camera Name</label>
                <input 
                  {...register('name')}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white"
                  placeholder="e.g. Lobby Cam 1"
                />
                {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
              </div>
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">Location</label>
                <input 
                  {...register('location')}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white"
                  placeholder="e.g. Main Entrance"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">Source Type</label>
                <select 
                  {...register('source_type')}
                  className="w-full bg-[#121212] border border-white/10 rounded-lg px-4 py-2.5 text-white"
                >
                  <option value="WEBCAM">Webcam</option>
                  <option value="IP_CAMERA">IP Camera</option>
                  <option value="RTSP">RTSP Stream</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm text-muted-foreground">Stream URL / ID</label>
                <input 
                  {...register('stream_url')}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white"
                  placeholder={watchedSourceType === 'WEBCAM' ? "0" : "rtsp://..."}
                />
                {errors.stream_url && <p className="text-red-500 text-xs mt-1">{errors.stream_url.message}</p>}
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button 
                type="button" 
                onClick={() => setIsFormOpen(false)}
                className="px-4 py-2 rounded-lg text-muted-foreground hover:text-white"
              >
                Cancel
              </button>
              <button 
                type="submit"
                className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Save Camera
              </button>
            </div>
          </form>
        </div>
      )}

      {testResult && (
        <div className="glass-panel p-4 rounded-lg border border-primary/30 text-primary-light">
          {testResult}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cameras.map(cam => (
          <div key={cam.id} className="glass-panel rounded-xl overflow-hidden border border-white/5 flex flex-col">
            <div className="p-5 border-b border-white/5 flex-1">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white/5 rounded-lg">
                    <CameraIcon className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <div>
                    <h3 className="text-white font-medium">{cam.name}</h3>
                    <p className="text-xs text-muted-foreground">{cam.location || 'No Location'}</p>
                  </div>
                </div>
                <div className={clsx(
                  "px-2 py-1 rounded text-xs font-medium",
                  cam.status === 'online' ? "bg-green-500/10 text-green-400" :
                  cam.status === 'starting' ? "bg-yellow-500/10 text-yellow-400" :
                  "bg-white/10 text-muted-foreground"
                )}>
                  {cam.status.toUpperCase()}
                </div>
              </div>

              <div className="space-y-2 mt-4 text-sm font-mono text-muted-foreground">
                <div className="flex justify-between">
                  <span>Type</span>
                  <span className="text-white">{cam.source_type}</span>
                </div>
                <div className="flex justify-between">
                  <span>Source</span>
                  <span className="text-white truncate max-w-[150px]">{cam.stream_url}</span>
                </div>
                
                {/* Health Sparkline */}
                <div className="mt-4 pt-4 border-t border-white/5">
                  <div className="flex justify-between items-end mb-1 text-xs">
                    <span>Uptime (1h)</span>
                    <span className="text-white">
                      {cam.health?.length > 0 ? `${cam.health[cam.health.length-1].fps.toFixed(1)} FPS` : '--'}
                    </span>
                  </div>
                  <div className="flex gap-[1px] h-6 items-end mt-2">
                    {(cam.health || []).slice(-30).map((h, i) => (
                      <div 
                        key={i} 
                        className={clsx(
                          "flex-1 rounded-t-sm",
                          h.status === 'online' ? "bg-green-500/80" : 
                          h.status === 'starting' ? "bg-yellow-500/80" : "bg-red-500/50"
                        )}
                        style={{ height: `${Math.max(10, Math.min(100, (h.fps / 30) * 100))}%` }}
                        title={`${new Date(h.timestamp).toLocaleTimeString()}: ${h.fps.toFixed(1)} FPS`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            {isAdmin && (
              <div className="p-3 bg-white/5 flex items-center justify-between gap-2">
                <button 
                  onClick={() => handleTest(cam.id)}
                  disabled={testing}
                  className="flex-1 py-2 text-xs font-medium text-white bg-white/5 hover:bg-white/10 rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Activity className="w-3.5 h-3.5" />
                  Test
                </button>

                {cam.status === 'offline' ? (
                  <button 
                    onClick={() => handleStart(cam.id)}
                    className="flex-1 py-2 text-xs font-medium text-white bg-green-500/20 hover:bg-green-500/30 rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Play className="w-3.5 h-3.5" />
                    Start
                  </button>
                ) : (
                  <button 
                    onClick={() => handleStop(cam.id)}
                    className="flex-1 py-2 text-xs font-medium text-white bg-red-500/20 hover:bg-red-500/30 rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Square className="w-3.5 h-3.5" />
                    Stop
                  </button>
                )}

                <button 
                  onClick={() => handleDelete(cam.id)}
                  className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors ml-1"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
