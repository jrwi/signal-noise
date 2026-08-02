class Track:
    # a property set for all objects of this class
    # a class variable
    source = "unknown"

    def __init__(self, title, artist, duration_ms):
        self.title = title
        self.artist = artist
        self.duration_ms = duration_ms

    def __repr__(self):
        return f"Track(title={self.title!r}, artist={self.artist!r}, duration_ms={self.duration_ms})"

    def duration_seconds(self):
        return self.duration_ms / 1000
    
    def describe(self):
        seconds = self.duration_seconds()
        print(f"{self.title} by {self.artist} ({seconds:.1f}s) - source: {self.source}")
        
    # here we attach a method to the Track class object itself by basically creating a function where you st
    @classmethod
    def from_spotify(cls, title, artist, duration_ms):
        track = cls(title, artist, duration_ms) #cls is literally calling the __init__ here and 
        track.source = "spotify"
        return track

