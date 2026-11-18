# Choice of API Design

## Context

Milestone 2 requires an API specification for our key-value store, supporting CREATE, READ, EXISTS, and DELETE operations.

We need to choose an API approach for communication between clients and the Coordinator, as well as between the Coordinator and shards.

Three approaches were considered: **REST with OpenAPI**, **gRPC**, and **GraphQL**.

## Alternatives Considered

### 1. REST with OpenAPI

**Advantages:**
- Simple to implement and test using standard HTTP methods.
- OpenAPI provides clear documentation of endpoints, requests, and responses.
- Easy to test using tools such as curl or Postman.
- Well suited for basic CRUD operations.

**Disadvantages:**
- JSON serialization can introduce more overhead compared to binary protocols.
- HTTP endpoints and response codes need to be designed and maintained consistently.

### 2. gRPC

**Advantages:**
- Efficient communication using Protocol Buffers.
- Strongly typed API contracts.
- Suitable for communication between distributed services.

**Disadvantages:**
- Requires additional setup and code generation from `.proto` files.
- More difficult to test manually compared to REST.
- Adds unnecessary complexity for our current CRUD operations.

### 3. GraphQL

**Advantages:**
- Allows clients to request only the data they need.
- Provides a flexible API through a single endpoint.

**Disadvantages:**
- Requires additional schema and resolver implementation.
- More complex than necessary for a simple key-value store.
- Its flexibility provides limited benefits for our current operations.

## Decision

I decided to use **REST with OpenAPI** for both client-to-Coordinator and Coordinator-to-shard communication.

Our key-value store supports a small set of CRUD operations, so REST provides a simple and sufficient interface without introducing additional complexity.

OpenAPI will allow us to define and document the API contract before implementation. Using REST for both external and internal communication also makes development, testing, and debugging easier.

## Consequences

- Both the Coordinator and shards will communicate using HTTP REST APIs.
- API endpoints, request formats, responses, and error codes will be documented using OpenAPI.
- The API can be tested using standard HTTP tools.
- The same communication approach can be used across the system.
- REST/JSON may introduce more communication overhead compared to gRPC.
- FastAPI handles HTTP routing and request validation, while the Coordinator and storage logic remain separate; Uvicorn runs the ASGI application.
