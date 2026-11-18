import random

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="AquaSense Controller Service",
    description="Sensor-controller API providing water-quality readings.",
    version="1.0.0",
)


class Reading(BaseModel):
    """Sensor measurements and GPS coordinates."""

    temperature: float = Field(description="Water temperature in degrees Celsius")
    turbidity: float = Field(ge=0, description="Turbidity in NTU")
    tds: int = Field(ge=0, description="Total dissolved solids in ppm")
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


@app.get("/health", tags=["Service"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readings", response_model=Reading, tags=["Readings"])
def get_readings() -> Reading:
    """Generate a simulated reading using representative development values."""
    return Reading(
        temperature=round(random.uniform(27.0, 32.0), 1),
        turbidity=round(random.uniform(1.0, 4.0), 1),
        tds=random.randint(150, 250),
        latitude=round(26.4499 + random.uniform(-0.001, 0.001), 4),
        longitude=round(80.3319 + random.uniform(-0.001, 0.001), 4),
    )
