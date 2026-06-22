import { useState, useEffect } from 'react';
import { Clock, MapPin } from 'lucide-react';
import { apiClient } from '../api/client';
import clsx from 'clsx';

export function Timeline() {
  const [identities, setIdentities] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [cameras, setCameras] = useState<any>({});
  
  const [filterCamera, setFilterCamera] = useState<string>('');
  const [filterZone, setFilterZone] = useState<string>('');
  const [filterFrom, setFilterFrom] = useState<string>('');
  const [filterTo, setFilterTo] = useState<string>('');

  useEffect(() => {
    fetchIdentities();
    fetchCameras();
    const int1 = setInterval(fetchIdentities, 5000);
    return () => clearInterval(int1);
  }, []);

  useEffect(() => {
    if (selectedId) {
      fetchTimeline(selectedId);
      const int2 = setInterval(() => fetchTimeline(selectedId), 2000);
      return () => clearInterval(int2);
    }
  }, [selectedId, filterCamera, filterZone, filterFrom, filterTo]);

  const fetchIdentities = async () => {
    try {
      const res = await apiClient.get('/identities');
      const items = res.data.items || [];
      setIdentities(items);
      if (!selectedId && items.length > 0) {
        setSelectedId(items[0].global_id);
      }
    } catch (e) { console.error(e); }
  };

  const fetchCameras = async () => {
    try {
      const res = await apiClient.get('/cameras');
      const camMap: any = {};
      res.data.forEach((c: any) => { camMap[c.id] = c; });
      setCameras(camMap);
    } catch (e) { console.error(e); }
  };

  const fetchTimeline = async (id: string) => {
    try {
      const params = new URLSearchParams();
      if (filterCamera) params.append('camera_id', filterCamera);
      if (filterZone) params.append('zone_id', filterZone);
      if (filterFrom) params.append('from_ts', new Date(filterFrom).toISOString());
      if (filterTo) params.append('to_ts', new Date(filterTo).toISOString());
      
      const res = await apiClient.get(`/identities/${id}/timeline?${params.toString()}`);
      // Condense timeline by removing back-to-back duplicate camera sightings
      const condensed = [];
      let lastCam = null;
      // Points are returned descending
      for (const pt of [...res.data].reverse()) {
        if (pt.camera_id !== lastCam) {
          condensed.push(pt);
          lastCam = pt.camera_id;
        } else {
          // update the last point to show duration or just update time
          condensed[condensed.length - 1].end_ts = pt.frame_ts;
        }
      }
      setTimeline(condensed.reverse());
    } catch (e) { console.error(e); }
  };

  return (
    <div className="h-full flex flex-col space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Cross-Camera Timeline</h2>
        <p className="text-muted-foreground mt-1">Track specific identities as they move between cameras.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        <div className="glass-panel border border-white/5 rounded-xl flex flex-col overflow-hidden">
          <div className="p-4 border-b border-white/5 bg-white/5">
            <h3 className="font-semibold text-white">Tracked Identities</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {identities.map(id => (
              <button
                key={id.global_id}
                onClick={() => setSelectedId(id.global_id)}
                className={clsx(
                  "w-full text-left px-4 py-3 rounded-lg transition-all flex items-center justify-between",
                  selectedId === id.global_id 
                    ? "bg-primary/20 text-primary-light border border-primary/30" 
                    : "text-muted-foreground hover:bg-white/5 hover:text-white"
                )}
              >
                <span className="font-mono">{id.global_id}</span>
                <span className="text-xs">{new Date(id.last_seen).toLocaleTimeString()}</span>
              </button>
            ))}
            {identities.length === 0 && (
              <p className="text-sm text-center text-muted-foreground mt-10">No identities tracked yet.</p>
            )}
          </div>
        </div>

        <div className="lg:col-span-3 glass-panel border border-white/5 rounded-xl flex flex-col overflow-hidden relative">
          <div className="p-6 border-b border-white/5 bg-gradient-to-r from-primary/10 to-transparent">
            <h3 className="text-xl font-bold font-mono text-white">
              {selectedId || 'Select an Identity'}
            </h3>
            <p className="text-sm text-muted-foreground mt-1 mb-4">Trajectory History</p>
            
            <div className="flex flex-wrap gap-4">
              <input 
                type="number" placeholder="Camera ID" 
                className="bg-black/50 border border-white/10 rounded px-3 py-1.5 text-sm text-white"
                value={filterCamera} onChange={e => setFilterCamera(e.target.value)} 
              />
              <input 
                type="number" placeholder="Zone ID" 
                className="bg-black/50 border border-white/10 rounded px-3 py-1.5 text-sm text-white"
                value={filterZone} onChange={e => setFilterZone(e.target.value)} 
              />
              <input 
                type="datetime-local" 
                className="bg-black/50 border border-white/10 rounded px-3 py-1.5 text-sm text-white"
                value={filterFrom} onChange={e => setFilterFrom(e.target.value)} 
              />
              <input 
                type="datetime-local" 
                className="bg-black/50 border border-white/10 rounded px-3 py-1.5 text-sm text-white"
                value={filterTo} onChange={e => setFilterTo(e.target.value)} 
              />
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-8">
            <div className="relative border-l border-white/10 ml-4 space-y-8 pb-10">
              {timeline.map((event, idx) => {
                const cam = cameras[event.camera_id];
                return (
                  <div key={idx} className="relative pl-8">
                    <div className="absolute -left-3 top-1 w-6 h-6 rounded-full bg-[#121212] border-2 border-primary flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-primary-light animate-pulse" />
                    </div>
                    <div className="flex flex-col">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-mono text-muted-foreground flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5" />
                          {new Date(event.frame_ts).toLocaleTimeString()}
                          {event.end_ts && ` - ${new Date(event.end_ts).toLocaleTimeString()}`}
                        </span>
                      </div>
                      <div className="mt-2 glass-panel p-4 rounded-lg border border-white/5 inline-block w-fit">
                        <div className="flex items-center gap-3">
                          <MapPin className="w-5 h-5 text-primary" />
                          <div>
                            <p className="text-white font-medium">{cam?.location || `Camera ${event.camera_id}`}</p>
                            <p className="text-xs text-muted-foreground">{cam?.name}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {timeline.length === 0 && selectedId && (
                <div className="text-muted-foreground pl-8 pt-4">Gathering timeline data...</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
