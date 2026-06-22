import { useEffect, useState } from 'react';
import { fetchIdentities } from '../api/client';
import type { Identity } from '../api/client';
import { Users, Search, Filter } from 'lucide-react';

export function Identities() {
  const [identities, setIdentities] = useState<Identity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIdentities().then(data => {
      setIdentities(data);
      setLoading(false);
    }).catch(e => {
      console.error(e);
      setLoading(false);
    });
  }, []);

  return (
    <div className="h-full flex flex-col space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Identity Database</h2>
          <p className="text-muted-foreground mt-1">Cross-camera re-identification profiles.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 bg-white/5 hover:bg-white/10 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-white/5">
            <Filter className="w-4 h-4" /> Filter
          </button>
          <button className="flex items-center gap-2 bg-white text-black hover:bg-white/90 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Search className="w-4 h-4" /> Image Search
          </button>
        </div>
      </div>

      <div className="glass-panel rounded-xl border border-white/5 overflow-hidden flex-1 flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-white/5 border-b border-white/5">
              <tr>
                <th className="px-6 py-4 font-medium">Profile</th>
                <th className="px-6 py-4 font-medium">Global ID</th>
                <th className="px-6 py-4 font-medium">First Seen</th>
                <th className="px-6 py-4 font-medium">Cameras Spotted</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading ? (
                <tr><td colSpan={4} className="px-6 py-8 text-center text-muted-foreground">Loading identities...</td></tr>
              ) : identities.length === 0 ? (
                <tr><td colSpan={4} className="px-6 py-8 text-center text-muted-foreground">No identities tracked yet.</td></tr>
              ) : (
                identities.map((id) => (
                  <tr key={id.global_id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4">
                      <div className="w-10 h-10 rounded-md bg-white/10 flex items-center justify-center overflow-hidden border border-white/10">
                        {id.thumbnail ? (
                          <img src={`data:image/jpeg;base64,${id.thumbnail}`} className="w-full h-full object-cover" alt="Profile" />
                        ) : (
                          <Users className="w-5 h-5 text-muted-foreground" />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-white/90">{id.global_id}</td>
                    <td className="px-6 py-4 text-muted-foreground">{new Date(id.first_seen).toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1">
                        {id.camera_ids?.map(cam => (
                          <span key={cam} className="px-2 py-1 text-xs bg-white/10 rounded">CAM-{cam}</span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
