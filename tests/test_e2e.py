import numpy as np
from datetime import datetime, timedelta
from app.pipeline.matcher import IdentityMatcher

def test_e2e_reid_workflow():
    """
    Simulates the multi-camera re-identification workflow end-to-end logically
    without requiring a live Kafka broker.
    """
    matcher = IdentityMatcher(embedding_dim=512, threshold=0.72)
    
    # 1. Person walks into Camera 1
    base_embedding = np.random.rand(512)
    base_embedding = base_embedding / np.linalg.norm(base_embedding)
    
    ts1 = datetime.utcnow()
    global_id_cam1 = matcher.match(base_embedding, camera_id=1, frame_ts_str=ts1.isoformat())
    
    assert global_id_cam1 == "ID-0001"
    
    # 2. Same person is seen on Camera 2, 30 seconds later (plausible transition)
    # Add a tiny bit of noise to simulate real-world ReID variations
    noise = np.random.normal(0, 0.05, 512)
    cam2_embedding = base_embedding + noise
    cam2_embedding = cam2_embedding / np.linalg.norm(cam2_embedding)
    
    ts2 = ts1 + timedelta(seconds=30)
    global_id_cam2 = matcher.match(cam2_embedding, camera_id=2, frame_ts_str=ts2.isoformat())
    
    assert global_id_cam2 == "ID-0001", "Failed to merge person across cameras!"
    
    # 3. Different person on Camera 1
    diff_embedding = np.random.rand(512)
    diff_embedding = diff_embedding / np.linalg.norm(diff_embedding)
    
    ts3 = ts2 + timedelta(seconds=10)
    global_id_new = matcher.match(diff_embedding, camera_id=1, frame_ts_str=ts3.isoformat())
    
    assert global_id_new == "ID-0002", "Incorrectly merged a distinct person!"

if __name__ == "__main__":
    test_e2e_reid_workflow()
    print("End-to-End multi-camera simulation logic passed successfully!")
