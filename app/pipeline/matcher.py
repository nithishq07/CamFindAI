import faiss
import numpy as np
from datetime import datetime

class IdentityMatcher:
    def __init__(self, embedding_dim=512, threshold=0.72):
        self.embedding_dim = embedding_dim
        self.threshold = threshold
        
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        self.id_mapping = {}
        self.next_internal_id = 1
        
        self.gallery_embeddings = {}
        
        # State tracking for plausible transition check
        # global_id -> {"last_camera_id": int, "last_seen_ts": datetime}
        self.identity_states = {}

    def match(self, embedding, camera_id=None, frame_ts_str=None):
        """
        embedding: numpy array of shape (embedding_dim,)
        returns: global_id (str)
        """
        query = np.array([embedding], dtype=np.float32)
        
        if isinstance(frame_ts_str, datetime):
            frame_ts = frame_ts_str
        elif frame_ts_str:
            frame_ts = datetime.fromisoformat(frame_ts_str)
        else:
            frame_ts = datetime.utcnow()
        
        if self.index.ntotal == 0:
            return self._add_new_identity(query, camera_id, frame_ts)
            
        distances, indices = self.index.search(query, 1)
        best_sim = distances[0][0]
        best_idx = indices[0][0]
        
        if best_sim >= self.threshold:
            global_id = self.id_mapping[best_idx]
            
            # Plausible transition time check
            if camera_id and global_id in self.identity_states:
                last_state = self.identity_states[global_id]
                if last_state["last_camera_id"] != camera_id:
                    # Transitioned cameras! Check time delta
                    time_delta = (frame_ts - last_state["last_seen_ts"]).total_seconds()
                    # Hardcoded threshold for minimum plausible transition time between ANY two cameras
                    if time_delta < 5.0:
                        # Impossible transition, mint new ID
                        return self._add_new_identity(query, camera_id, frame_ts)
                        
            # Valid match (or same camera)
            self._update_identity(best_idx, query[0])
            self._update_state(global_id, camera_id, frame_ts)
            return global_id
        else:
            return self._add_new_identity(query, camera_id, frame_ts)

    def _add_new_identity(self, query, camera_id, frame_ts):
        internal_id = self.next_internal_id
        global_id = f"ID-{internal_id:04d}"
        
        self.id_mapping[internal_id - 1] = global_id # FAISS indices are 0-based
        self.gallery_embeddings[internal_id - 1] = query[0]
        self._update_state(global_id, camera_id, frame_ts)
        
        self.index.add(query)
        self.next_internal_id += 1
        return global_id

    def _update_identity(self, faiss_idx, new_embedding, alpha=0.1):
        current_emb = self.gallery_embeddings[faiss_idx]
        updated_emb = (1 - alpha) * current_emb + alpha * new_embedding
        updated_emb = updated_emb / np.linalg.norm(updated_emb)
        self.gallery_embeddings[faiss_idx] = updated_emb
        
        all_embeddings = np.array(list(self.gallery_embeddings.values()), dtype=np.float32)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(all_embeddings)

    def _update_state(self, global_id, camera_id, frame_ts):
        if camera_id is not None:
            self.identity_states[global_id] = {
                "last_camera_id": camera_id,
                "last_seen_ts": frame_ts
            }
