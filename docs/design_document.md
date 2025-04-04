# Bazar.com Design Document

## 1. System Architecture
- Three-tier architecture: Frontend, Catalog, Order
- Microservices design pattern
- RESTful HTTP communication

## 2. Component Details
### Frontend Server
- Acts as gateway for clients
- Routes requests to appropriate backend services
- Provides unified API interface

### Catalog Server
- Maintains book inventory
- Supports search and info operations
- Handles stock updates

### Order Server
- Processes purchase requests
- Verifies stock availability
- Logs successful orders

## 3. Data Persistence
- Catalog: JSON file
- Orders: Text log file
- Simple file-based approach chosen for simplicity

## 4. Concurrency Handling
- Flask's built-in threaded request handling
- No explicit locking needed for this scale

## 5. Limitations
- No authentication/authorization
- Basic error handling
- No transaction rollback on failures

## 6. Possible Extensions
- Add user accounts
- Implement shopping cart
- Add more robust database
- Include book images and descriptions