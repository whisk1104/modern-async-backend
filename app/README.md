## ⚙️ Pragmatic Design Decisions (Trade-offs)

### 1. Identity Verification vs. Cost Efficiency
Rather than maintaining an expansive, stateful session cluster, the system employs Stateless JWTs verified cryptographically at the edge. To handle instant token invalidation (e.g., explicit logout), a Redis-backed Blacklist Layer is introduced with an adaptive TTL tied exactly to the token's remaining lifespan, ensuring low memory footprint and zero database pressure.

### 2. Connection Resilience over Micro-Benchmarking
SQLAlchemy is configured with `pool_pre_ping=True`. While this introduces a minor millisecond-level overhead by executing a `SELECT 1` heartbeat probe prior to reusing checked-out connections, it completely shields the application from zombie connections or sudden database drops, providing absolute production determinism.

### 3. Declarative Startup over Fragile Code-Level Sleep
To resolve the classic container race condition where the web API spins up faster than the database instance initializing its WAL logs, we explicitly reject fragile application-level `time.sleep()` blocks. Instead, we delegate startup governance to the infrastructure tier using Docker Compose `depends_on` with `condition: service_healthy` semantics.

---

## 🏗️ Code Layering Architecture (Separation of Concerns)

To maintain a clean, maintainable, and unit-testable codebase, the application strictly adheres to the following decoupled layer boundaries:

```text
  [ Client Request ] 
          │
          ▼
  ┌───────────────────┐
  │   Views / Routes  │ ───► Role: HTTP Protocol, Params Validation (Pydantic), Status Codes
  └───────────────────┘
          │
          ▼
  ┌───────────────────┐
  │      Services     │ ───► Role: Pure Domain Logic, Database Transactions, Business Rules
  └───────────────────┘
          │
          ▼
  ┌───────────────────┐
  │  Database/Models  │ ───► Role: SQLAlchemy Async Schemas, Data Persistence
  └───────────────────┘
```
views/ (The Delivery Layer): Strictly restricted to handling HTTP mechanics (request parsing, response status codes, route dependency injection). Zero business logic should live here.

services/ (The Domain Layer): Orchestrates business rules and database state modifications. Services are designed to be completely decoupled from the web framework, making them easily unit-testable.

core/ (The System Backbone): Low-level machinery including security hashing (Bcrypt), JWT generation primitives, and raw async database engine initializations.

Getting Started (Docker Deployment)
Prerequisites
Docker and Docker Compose V2 installed.

Spinning Up the Environment
Bring up the entire stack (FastAPI API, PostgreSQL, Redis) with a single command. The API will deterministically wait until PostgreSQL passes its internal readiness checks.
  docker compose up --build -d

Verifying Service Health
Once deployed, check the container cluster log outputs:
  docker compose logs -f

The interactive OpenAPI documentation is automatically generated and accessible at:
-Swagger UI: http://localhost:8000/docs
-ReDoc: http://localhost:8000/redoc

Bare-Metal Local Development
For quick debugging cycles where spinning up full Docker containers is unnecessary, follow these steps to run the application bare-metal:

1. Environment Isolation
Create and activate a clean virtual environment:
  python3 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt

2. Live-Reload Development Server
Execute Uvicorn targeting the app instance with auto-reload enabled:
  uvicorn app.main:app --reload --port 8000

Testing & Code Quality Assurance
We enforce strict linting and continuous quality controls to mitigate technical debt:

Running Asynchronous Unit Tests
Testing the async boundary requires specialized fixtures. We utilize pytest-asyncio to drive our non-blocking test suites:
  pytest

Code Formatting Style-Guide
All code must strictly comply with PEP 8 standards. Run black to automatically format files prior to any Git commit:
  black . --check

Future Roadmap (Anti-Overengineering)
Consistent with our philosophy of avoiding unnecessary engineering overhead in the early-to-mid business lifecycle, the following telemetry and resiliency components are intentionally designated as out-of-scope for MVP, but pre-architected for pluggable integration:

-Distributed Tracing: Integration points reserved for OpenTelemetry to profile cross-service latency.
-Loop Telemetry: Native hooks for monitoring event_loop_lag to safeguard against asynchronous blockages.
-Graceful Degradation: Enhanced try-except circuit breakers to decouple token validation entirely if the memory cache crashes.
