from pydantic import BaseModel, field_validator

class Track(BaseModel):
    title: str
    artist: str
    duration_ms: int
    source: str = "unknown"

    def duration_seconds(self):
        return self.duration_ms / 1000
    
    def describe(self):
        seconds = self.duration_seconds()
        print(f"{self.title} by {self.artist} ({seconds:.1f}s) - source: {self.source}")


    @field_validator("duration_ms")
    @classmethod
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("duration_ms must be positive")
        return v
    
    @classmethod
    def from_spotify(cls, title, artist, duration_ms):
        return cls(title=title, artist=artist, duration_ms=duration_ms, source="spotify")

