# AquaSense

**Backend API for IoT-Based Water Quality Monitoring**

AquaSense is a Python backend project designed to retrieve, validate, and expose water-quality readings from a controller service through REST APIs. It provides a clear service boundary between a sensor-facing controller and applications that consume the readings.

The current repository is intentionally backend-focused. It does not include the dashboard or other frontend assets.

> **Implementation status:** The two FastAPI services are implemented. The controller currently generates simulated sensor readings for development and API testing. Direct ESP8266 and physical sensor integration is a planned hardware integration step, not a feature implemented by the Python files in this repository.

## Problem

Water-quality information is often collected manually or is not available in a consistent, machine-readable format. An IoT monitoring system needs a reliable way to collect measurements, transfer them from a device-side controller, validate the data, and make it available to other software.

AquaSense focuses on the backend communication layer: defining a consistent reading schema and exposing an API that can retrieve readings from a separate controller service.

## What AquaSense does

The project is split into two independent FastAPI applications:

1. **Controller service** – exposes `/readings` and currently simulates sensor values in the same shape expected from a device controller.
2. **Backend API** – calls the controller over HTTP, applies a timeout, validates the returned JSON with Pydantic, and exposes a normalized `/readings` endpoint to API consumers.

This separation keeps controller communication independent from the main API and makes it easier to replace simulated values with actual hardware readings later.

## Measurements represented

| Measurement | Field | Unit | Current implementation |
|---|---|---|---|
| Water temperature | `temperature` | °C | Simulated |
| Turbidity | `turbidity` | NTU | Simulated |
| Total dissolved solids | `tds` | ppm | Simulated |
| GPS latitude | `latitude` | Decimal degrees | Simulated near configured development coordinates |
| GPS longitude | `longitude` | Decimal degrees | Simulated near configured development coordinates |

The controller currently generates development values in these ranges:

- Temperature: 27.0–32.0 °C
- Turbidity: 1.0–4.0 NTU
- TDS: 150–250 ppm
- GPS: small random variation around latitude `26.4499` and longitude `80.3319`

These are simulated values for API development and should not be interpreted as real measurements or water-safety certification.

## Architecture

```text
      Sensor / IoT device integration
       (planned ESP8266 integration)
                    |
                    v
        Controller Service (FastAPI)
        GET /readings
        Current: simulated measurements
                    |
             HTTP + JSON
                    |
                    v
           AquaSense Backend
              (FastAPI)
        - Calls controller service
        - Applies request timeout
        - Validates response with Pydantic
        - Handles upstream errors
                    |
                    v
             REST API Consumer
       GET /readings  |  GET /health
       Swagger /docs | OpenAPI schema
```

## Technology stack

| Technology | Role |
|---|---|
| Python | Backend implementation |
| FastAPI | REST API framework for both services |
| Pydantic | Reading schema and payload validation |
| Requests | HTTP communication between backend and controller |
| Uvicorn | ASGI server |
| Pytest | Automated API tests |
| HTTPX | FastAPI test client dependency |

## Repository structure

```text
AquaSense/
├── backend/
│   └── main.py              # Main API, controller client, validation and errors
├── controller/
│   └── controller.py        # Controller API and simulated sensor readings
├── tests/
│   ├── test_backend.py      # Backend API and upstream failure tests
│   └── test_controller.py   # Controller health and reading tests
├── .env.example             # Example runtime configuration
├── .gitignore
├── requirements.txt
└── README.md
```

## API reference

Run both services locally, then use the interactive Swagger documentation.

### Controller service — port 9000

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Controller health check |
| `GET` | `/readings` | Returns a simulated sensor reading |

Swagger UI: `http://127.0.0.1:9000/docs`

### Main backend — port 8000

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service information |
| `GET` | `/health` | Backend health check |
| `GET` | `/readings` | Fetches and validates the controller reading |

Swagger UI: `http://127.0.0.1:8000/docs`

### Example reading response

```json
{
  "temperature": 29.4,
  "turbidity": 2.3,
  "tds": 187,
  "latitude": 26.4501,
  "longitude": 80.3317
}
```

### Error handling

The backend uses a configurable timeout when requesting the controller. If the controller cannot be reached, returns an unsuccessful HTTP response, provides invalid JSON, or returns data that fails schema validation, the backend responds with `502 Bad Gateway` and a consistent error message.

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AquaSense.git
cd AquaSense
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the environment's Python executable directly or use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the backend

Copy `.env.example` to `.env` and adjust the values if needed.

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

The backend reads:

| Variable | Default | Description |
|---|---|---|
| `CONTROLLER_URL` | `http://127.0.0.1:9000` | Base URL of the controller service |
| `REQUEST_TIMEOUT_SECONDS` | `5` | Maximum wait for a controller response |
| `LOG_LEVEL` | `INFO` | Python logging level |

### 5. Start the controller service

Open a terminal at the repository root:

```bash
uvicorn controller.controller:app --host 127.0.0.1 --port 9000 --reload
```

### 6. Start the main backend

Open a second terminal at the repository root:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 7. Verify the APIs

- Controller docs: `http://127.0.0.1:9000/docs`
- Backend docs: `http://127.0.0.1:8000/docs`
- Backend health: `http://127.0.0.1:8000/health`
- Latest reading through backend: `http://127.0.0.1:8000/readings`

## Run tests

From the repository root:

```bash
pytest -v
```

The tests cover controller response shape and ranges, backend health, successful reading retrieval, and upstream controller failure handling.

## Engineering considerations

- **Service separation:** The controller and main API run as separate applications and can be developed or deployed independently.
- **Typed contracts:** Pydantic models define the expected reading structure and validate numeric ranges for turbidity, TDS, and GPS coordinates.
- **Bounded network calls:** The backend sets a timeout on controller requests so an unresponsive upstream service does not block indefinitely.
- **Consistent upstream error handling:** Controller/network/JSON/schema failures are translated into an HTTP 502 response.
- **Configurable controller endpoint:** The controller URL is supplied through an environment variable rather than being fixed in application logic.

## Roadmap

The following are potential next steps and are not implemented in the current code:

- Connect the ESP8266 to the controller service and replace simulated readings with actual sensor values.
- Integrate DS18B20, turbidity, and TDS sensor drivers.
- Add device-to-server authentication and request signing.
- Add a device ingestion endpoint if the hardware communication design requires push-based telemetry.
- Persist historical readings in a database.
- Add timestamps, device identifiers, and reading metadata.
- Add alert thresholds and anomaly detection.
- Add automated deployment and monitoring.

## Scope note

AquaSense in this repository is the backend/API foundation and a simulated controller. It currently does not persist historical readings, authenticate IoT devices, receive telemetry through a POST endpoint, or establish that water is safe to drink. Sensor readings and water-quality interpretation require calibrated hardware and appropriate testing.

## License

No license is included. Add a `LICENSE` file if you want to specify reuse and distribution terms.
