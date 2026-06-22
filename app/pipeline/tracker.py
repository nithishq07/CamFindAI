from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    def __init__(self, max_age=30, n_init=3, nn_budget=100):
        # Initialize DeepSORT
        self.tracker = DeepSort(
            max_age=max_age, 
            n_init=n_init, 
            nn_budget=nn_budget, 
            override_track_class=0, # only track persons
            embedder="mobilenet" # Restore mobilenet embedder to fix crash
        )

    def update(self, detections, frame):
        """
        Update the tracker with new detections.
        detections format: list of ([left, top, width, height], confidence, class_id)
        Returns:
            list of Track objects
        """
        # DeepSORT update expects detections in the format we prepared
        tracks = self.tracker.update_tracks(detections, frame=frame)
        return tracks
