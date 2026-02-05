---
title: {{PROJECT_NAME}} - API Specification
status: draft
version: 1.0.0
last-updated: {{CURRENT_DATE}}
owner: {{TEAM_NAME}}
---

# {{PROJECT_NAME}} - API Specification

## API Overview

**Base URL:** `{{BASE_URL}}` (e.g., `https://api.example.com/v1`)
**Protocol:** REST over HTTPS
**Data Format:** JSON
**Authentication:** {{AUTH_TYPE}} (e.g., JWT Bearer Token)

## Authentication

### Authentication Flow

{{Describe auth flow: login → token → refresh}}

### Headers

All authenticated requests must include:
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

### Authentication Endpoints

#### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-02-02T10:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `400` - Validation error (email invalid, password too weak)
- `409` - Email already registered

#### POST /auth/login

Authenticate and receive access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-02-03T10:30:00Z"
}
```

**Errors:**
- `401` - Invalid credentials
- `429` - Too many login attempts

## Resource Endpoints

### {{RESOURCE_NAME}} Endpoints

#### GET /api/{{resource}}

List all {{resource}} items for authenticated user.

**Query Parameters:**
| Parameter | Type    | Required | Default | Description                    |
|-----------|---------|----------|---------|--------------------------------|
| page      | integer | No       | 1       | Page number for pagination     |
| limit     | integer | No       | 20      | Items per page (max 100)       |
| status    | string  | No       | all     | Filter by status               |
| sort      | string  | No       | -created| Sort field (prefix - for desc) |

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "{{ID}}",
      "{{FIELD_1}}": "{{VALUE_1}}",
      "{{FIELD_2}}": "{{VALUE_2}}",
      "created_at": "2025-02-02T10:30:00Z",
      "updated_at": "2025-02-02T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

**Errors:**
- `401` - Unauthorized

#### GET /api/{{resource}}/:id

Get a specific {{resource}} by ID.

**Response (200 OK):**
```json
{
  "id": "{{ID}}",
  "{{FIELD_1}}": "{{VALUE_1}}",
  "{{FIELD_2}}": "{{VALUE_2}}",
  "created_at": "2025-02-02T10:30:00Z",
  "updated_at": "2025-02-02T10:30:00Z"
}
```

**Errors:**
- `401` - Unauthorized
- `404` - {{Resource}} not found
- `403` - Forbidden (not owned by user)

#### POST /api/{{resource}}

Create a new {{resource}}.

**Request:**
```json
{
  "{{FIELD_1}}": "{{VALUE_1}}",
  "{{FIELD_2}}": "{{VALUE_2}}"
}
```

**Validation Rules:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| {{FIELD_1}} | {{TYPE}} | Yes | {{CONSTRAINTS}} |
| {{FIELD_2}} | {{TYPE}} | No | {{CONSTRAINTS}} |

**Response (201 Created):**
```json
{
  "id": "{{ID}}",
  "{{FIELD_1}}": "{{VALUE_1}}",
  "{{FIELD_2}}": "{{VALUE_2}}",
  "created_at": "2025-02-02T10:30:00Z",
  "updated_at": "2025-02-02T10:30:00Z"
}
```

**Errors:**
- `400` - Validation error
- `401` - Unauthorized

#### PATCH /api/{{resource}}/:id

Update an existing {{resource}}.

**Request (all fields optional):**
```json
{
  "{{FIELD_1}}": "{{NEW_VALUE_1}}",
  "{{FIELD_2}}": "{{NEW_VALUE_2}}"
}
```

**Response (200 OK):**
```json
{
  "id": "{{ID}}",
  "{{FIELD_1}}": "{{NEW_VALUE_1}}",
  "{{FIELD_2}}": "{{NEW_VALUE_2}}",
  "created_at": "2025-02-02T10:30:00Z",
  "updated_at": "2025-02-02T15:45:00Z"
}
```

**Errors:**
- `400` - Validation error
- `401` - Unauthorized
- `404` - Not found
- `403` - Forbidden

#### DELETE /api/{{resource}}/:id

Delete a {{resource}}.

**Response (204 No Content)**

**Errors:**
- `401` - Unauthorized
- `404` - Not found
- `403` - Forbidden

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional error context"
    }
  }
}
```

### Error Codes

| Code | Status | Description | Example |
|------|--------|-------------|---------|
| `VALIDATION_ERROR` | 400 | Request validation failed | Missing required field |
| `UNAUTHORIZED` | 401 | Authentication required | Invalid or missing token |
| `FORBIDDEN` | 403 | Insufficient permissions | Cannot access resource |
| `NOT_FOUND` | 404 | Resource not found | {{Resource}} ID doesn't exist |
| `CONFLICT` | 409 | Resource conflict | Email already registered |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Try again in 60 seconds |
| `INTERNAL_ERROR` | 500 | Server error | Database connection failed |

## Rate Limiting

- **Limit:** {{RATE_LIMIT}} requests per {{TIME_WINDOW}} (e.g., 100 requests per minute)
- **Headers:**
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1625097600
  ```

## Pagination

All list endpoints support pagination:

**Request:**
```
GET /api/{{resource}}?page=2&limit=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 125,
    "pages": 7,
    "has_next": true,
    "has_prev": true
  }
}
```

## Filtering and Sorting

### Filtering
```
GET /api/{{resource}}?status=active&{{filter_field}}={{filter_value}}
```

### Sorting
```
GET /api/{{resource}}?sort=-created_at,title
```
- Prefix `-` for descending order
- Comma-separated for multiple fields

## Versioning

API version is included in the base URL: `/v1/`

Breaking changes will result in a new version (`/v2/`).

## CORS

**Allowed Origins:** {{ALLOWED_ORIGINS}}
**Allowed Methods:** GET, POST, PATCH, DELETE, OPTIONS
**Allowed Headers:** Authorization, Content-Type

## WebSocket API (Optional)

### Connection
```javascript
const ws = new WebSocket('wss://{{WS_URL}}?token={{JWT_TOKEN}}');
```

### Events
```json
{
  "event": "{{EVENT_NAME}}",
  "data": {
    "{{FIELD}}": "{{VALUE}}"
  }
}
```

## API Endpoint Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /auth/register | No | Register new user |
| POST | /auth/login | No | User login |
| GET | /api/{{resource}} | Yes | List {{resource}} |
| GET | /api/{{resource}}/:id | Yes | Get {{resource}} |
| POST | /api/{{resource}} | Yes | Create {{resource}} |
| PATCH | /api/{{resource}}/:id | Yes | Update {{resource}} |
| DELETE | /api/{{resource}}/:id | Yes | Delete {{resource}} |

## Testing

### Example cURL Requests

**Register:**
```bash
curl -X POST {{BASE_URL}}/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'
```

**Create {{Resource}}:**
```bash
curl -X POST {{BASE_URL}}/api/{{resource}} \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"{{FIELD}}":"{{VALUE}}"}'
```

## References

- [Database Schema](./database-schema.md)
- [Architecture Documentation](./architecture.md)
- [Authentication Flow Diagram](./architecture.md#authentication)

## Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | {{CURRENT_DATE}} | Initial API specification | {{AUTHOR}} |
