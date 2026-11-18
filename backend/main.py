import logging
import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AquaSense API",
    description="Backend API for retrieving validated water-quality sensor readings.",
    version="1.0.0",
)

CONTROLLER_URL = os.getenv("CONTROLLER_URL", "http://127.0.0.1:9000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))


class Reading(BaseModel):
    """Validated water-quality and location reading returned by the controller."""

    temperature: float = Field(description="Water temperature in degrees Celsius")
    turbidity: float = Field(ge=0, description="Turbidity in NTU")
    tds: int = Field(ge=0, description="Total dissolved solids in ppm")
    latitude: float = Field(ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(ge=-180, le=180, description="GPS longitude")


@app.get("/", tags=["Service"])
def root() -> dict[str, str]:
    """Return basic service information."""
    return {"service": "AquaSense API", "status": "running", "docs": "/docs"}


@app.get("/health", tags=["Service"])
def health() -> dict[str, str]:
    """Check whether the API process is responsive."""
    return {"status": "healthy"}


@app.get("/readings", response_model=Reading, tags=["Readings"])
def get_readings() -> Reading:
    """Fetch the latest reading from the controller and validate its payload."""
    try:
        response = requests.get(
            f"{CONTROLLER_URL}/readings",
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload: Any = response.json()
        return Reading.model_validate(payload)
    except (requests.RequestException, ValueError, ValidationError) as error:
        logger.warning("Unable to retrieve a valid controller reading: %s", error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Controller unavailable or returned an invalid reading",
        ) from error
