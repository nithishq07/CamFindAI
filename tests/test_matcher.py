import pytest
import numpy as np
from datetime import datetime, timedelta
from app.pipeline.matcher import IdentityMatcher

def test_new_identity_creation():
    matcher = IdentityMatcher(embedding_dim=4, threshold=0.9)
    emb = np.array([1, 0, 0, 0])
    
    global_id = matcher.match(emb, camera_id=1, frame_ts_str=datetime.utcnow().isoformat())
    assert global_id == "ID-0001"

def test_successful_match():
    matcher = IdentityMatcher(embedding_dim=4, threshold=0.9)
    emb1 = np.array([1, 0, 0, 0])
    matcher.match(emb1, camera_id=1, frame_ts_str=datetime.utcnow().isoformat())
    
    emb2 = np.array([0.95, 0.05, 0, 0])
    global_id = matcher.match(emb2, camera_id=1, frame_ts_str=(datetime.utcnow() + timedelta(seconds=1)).isoformat())
    assert global_id == "ID-0001"

def test_plausible_transition_rejection():
    matcher = IdentityMatcher(embedding_dim=4, threshold=0.9)
    emb1 = np.array([1, 0, 0, 0])
    ts1 = datetime.utcnow()
    matcher.match(emb1, camera_id=1, frame_ts_str=ts1.isoformat())
    
    emb2 = np.array([0.95, 0.05, 0, 0])
    ts2 = ts1 + timedelta(seconds=1)
    
    global_id = matcher.match(emb2, camera_id=2, frame_ts_str=ts2.isoformat())
    assert global_id == "ID-0002"

def test_plausible_transition_acceptance():
    matcher = IdentityMatcher(embedding_dim=4, threshold=0.9)
    emb1 = np.array([1, 0, 0, 0])
    ts1 = datetime.utcnow()
    matcher.match(emb1, camera_id=1, frame_ts_str=ts1.isoformat())
    
    emb2 = np.array([0.95, 0.05, 0, 0])
    ts2 = ts1 + timedelta(seconds=10)
    
    global_id = matcher.match(emb2, camera_id=2, frame_ts_str=ts2.isoformat())
    assert global_id == "ID-0001"
