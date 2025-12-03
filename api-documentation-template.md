# API Documentation Template

This is a template for documenting the REST API for the project. If you use Flasgger, the live Swagger UI will be available at `/apidocs` when Flasgger is installed and running.

**Overview**
- Base paths:
  - `/api/v1`: Minimal backward-compatible API
  - `/api/v2`: Improved API with validation and OpenAPI documentation

**Endpoints (summary)**
- `GET /api/v1/dishes` — list dishes (v1)
- `GET /api/v1/dishes/{id}` — get dish by id (v1)
- `POST /api/v1/dishes` — create dish (v1)
- `GET /api/v1/orders` — list orders (v1)
- `POST /api/v1/orders` — create order (v1)
- `GET /api/v1/favourites/{account_id}` — favourites (v1)
- `GET /api/v1/accounts` — accounts (v1)

- `GET /api/v2/dishes` — list dishes (v2)
- `GET /api/v2/dishes/{id}` — get dish by id (v2)
- `POST /api/v2/dishes` — create dish (v2)
- `PUT /api/v2/dishes/{id}` — update dish (v2)
- `DELETE /api/v2/dishes/{id}` — delete dish (v2)
- `GET /api/v2/orders` — list orders (v2)
- `POST /api/v2/orders` — create order (v2)
- `GET /api/v2/favourites/{account_id}` — favourites (v2)
- `POST /api/v2/favourites` — add favourite (v2)
- `GET /api/v2/accounts` — accounts (v2)

**Schemas (examples)**
- Dish object:
```json
{
  "id": 1,
  "name": "Borscht",
  "price": 45.5,
  "image": "",
  "description": "Tasty",
  "ingredients": "beet, potato",
  "calories": 200
}
```

- Order create request:
```json
{
  "name": "Ivan",
  "phone": "380*********",
  "address": "Street 1",
  "items": [{"dish_id":1, "qty":2}]
}
```

**Error responses**
- 400 Bad Request: validation error. Body: `{ "error": "code", "message": "human message" }`
- 404 Not Found: resource not found. Body: `{ "error": "not_found" }`
- 500 Server Error: internal error. Body: `{ "error": "server_error", "message": "..." }`

**Examples**
- curl examples and Postman collection: see `postman_collection.json` provided.

**Notes / Template**
- Use the OpenAPI docstrings in `api.py` (v2) as canonical documentation for fields and responses.
- If you add endpoints, include a YAML docstring in the function so Flasgger picks it up.
