Markdown
# Application Internals & Developer Guide

This directory contains the core domain logic and API delivery layers of the application. Unlike the root documentation, this guide focuses on **bare-metal local development, code layering standards, and quality assurance**.

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
views/ (The Delivery Layer): Strictly restricted to handling HTTP mechanics (request parsing, response status codes, route dependency injection). Zero business logic should live here.

services/ (The Domain Layer): Orchestrates business rules and database state modifications. Services are designed to be completely decoupled from the web framework, making them easily unit-testable.

core/ (The System Backbone): Low-level machinery including security hashing (Bcrypt), JWT generation primitives, and raw async database engine initializations.

Bare-Metal Local Development
For quick debugging cycles where spinning up full Docker containers is unnecessary, follow these steps to run the application bare-metal:

1. Environment Isolation
Create and activate a clean virtual environment:

Bash
python3 -m venv venv
source venv/bin/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
2. Live-Reload Development Server
Execute Uvicorn targeting the app instance with auto-reload enabled:

Bash
# Executed from the project root directory
uvicorn app.main:app --reload --port 8000

Testing & Code Quality Assurance
We enforce strict linting and continuous quality controls to mitigate technical debt:

Running Asynchronous Unit Tests
Testing the async boundary requires specialized fixtures. We utilize pytest-asyncio to drive our non-blocking test suites:

Bash
pytest
Code Formatting Style-Guide
All code code must strictly comply with PEP 8 standards. Run black to automatically format files prior to any Git commit:

Bash
black . --check
