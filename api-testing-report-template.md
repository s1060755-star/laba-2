# API Testing Report Template

Project: Laba-2 API
Date: 
Tester: 

## Summary

- Purpose of testing: verify endpoints, responses, validation, and error handling.
- Environment: local (describe `base_url`, e.g. `http://127.0.0.1:5000`)

## Test Cases

1. Get all dishes
   - Request: `GET /api/v2/dishes`
   - Expected: 200, JSON array
   - Result: (pass/fail), notes

2. Create dish - valid
   - Request: `POST /api/v2/dishes` Body: `{name, price, ...}`
   - Expected: 201, response includes `id`
   - Result: (pass/fail), notes

3. Create dish - invalid (missing name)
   - Request: `POST /api/v2/dishes` Body: `{price:10}`
   - Expected: 400, validation error
   - Result: (pass/fail), notes

4. Create order - valid
   - Request: `POST /api/v2/orders` Body: `{address, items}`
   - Expected: 201, response includes `id` and `total`
   - Result: (pass/fail), notes

5. Create order - invalid (no address)
   - Expected: 400, validation error
   - Result: (pass/fail), notes

6. Favourites flow
   - Add favourite, get favourites
   - Expected: 201 then 200 with item present
   - Result: (pass/fail), notes

## Defects

- ID, endpoint, expected vs actual, steps to reproduce

## Conclusion

- Overall status, suggestions for improvements (auth, rate limits, etc.)
