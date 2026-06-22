import { useState, useEffect, useRef } from 'react';
import { WS_BASE_URL } from '../api/client';

export function useLiveFeed(cameraId: number) {
  const [frame, setFrame] = useState<string | null>(null);
  const [activeTracks, setActiveTracks] = useState<number>(0);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE_URL}/cameras/${cameraId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.frame) setFrame(data.frame);
        if (data.persons) setActiveTracks(data.persons.length);
        else if (data.active_tracks !== undefined) setActiveTracks(data.active_tracks);
      } catch (e) {
        console.error('Failed to parse frame message', e);
      }
    };

    return () => {
      ws.close();
    };
  }, [cameraId]);

  return { frame, activeTracks };
}

export function useAlertsWebSocket() {
  const [liveAlerts, setLiveAlerts] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE_URL}/alerts`);

    ws.onmessage = (event) => {
      try {
        const alert = JSON.parse(event.data);
        setLiveAlerts((prev) => [alert, ...prev].slice(0, 50));
      } catch (e) {
        console.error('Failed to parse alert message', e);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  return liveAlerts;
}
