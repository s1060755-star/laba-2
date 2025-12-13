from flask import Blueprint, jsonify, request
from database import (
    get_all_dish, get_dish_by_id, add_dish, update_dish, delete_dish,
    get_all_orders, add_order, get_all_favourites, add_favourite, get_db,
    get_all_accounts
)
import json
import traceback


def _row_to_dict(row):
    return dict(row) if row is not None else None


# --- API v1: minimal JSON endpoints (backwards compatible) ---
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@api_v1_bp.route('/dishes', methods=['GET'])
def v1_get_all_dishes():
    dishes = get_all_dish()
    return jsonify([_row_to_dict(d) for d in dishes])


@api_v1_bp.route('/dishes/<int:dish_id>', methods=['GET'])
def v1_get_dish(dish_id):
    d = get_dish_by_id(dish_id)
    if not d:
        return jsonify({'error': 'not_found'}), 404
    return jsonify(_row_to_dict(d))


@api_v1_bp.route('/dishes', methods=['POST'])
def v1_create_dish():
    data = request.get_json(force=True)
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name_required'}), 400
    price = float(data.get('price', 0) or 0)
    new_id = add_dish(name, price, data.get('image', ''), data.get('description', ''), data.get('ingredients', ''), data.get('calories'))
    return jsonify({'id': new_id}), 201


@api_v1_bp.route('/orders', methods=['GET'])
def v1_get_orders():
    orders = get_all_orders()
    return jsonify([_row_to_dict(o) for o in orders])


@api_v1_bp.route('/orders', methods=['POST'])
def v1_create_order():
    data = request.get_json(force=True)
    address = data.get('address', '')
    if not address:
        return jsonify({'error': 'address_required'}), 400
    items = data.get('items', [])
    db = get_db(); cur = db.cursor()
    total = 0.0
    safe_items = []
    for it in items:
        try:
            did = int(it.get('dish_id') if isinstance(it, dict) else it[0])
            qty = int(it.get('qty', 1) if isinstance(it, dict) else (it[1] if len(it) > 1 else 1))
        except Exception:
            continue
        cur.execute('SELECT price FROM dish WHERE id = ?', (did,))
        row = cur.fetchone()
        price_f = 0.0
        if row:
            try:
                price_val = row['price'] if 'price' in row.keys() else row[0]
                price_f = float(price_val)
            except Exception:
                price_f = 0.0
        total += price_f * qty
        safe_items.append({'dish_id': did, 'qty': qty})
    # support optional discount percent in payload
    try:
        discount = float(data.get('discount', 0) or 0)
    except Exception:
        discount = 0.0
    discounted_total = round(total * (1.0 - max(0, min(100, discount)) / 100.0), 2)
    order_id = add_order(data.get('name','Guest'), data.get('phone',''), address, safe_items, discounted_total, discount)
    return jsonify({'id': order_id, 'total': discounted_total, 'discount': discount}), 201


@api_v1_bp.route('/favourites/<int:account_id>', methods=['GET'])
def v1_get_favourites(account_id):
    favs = get_all_favourites(account_id)
    return jsonify([_row_to_dict(f) for f in favs])


@api_v1_bp.route('/accounts', methods=['GET'])
def v1_get_accounts():
    accounts = get_all_accounts()
    return jsonify([_row_to_dict(a) for a in accounts])


# --- API v2: improved validation, OpenAPI docstrings for Flasgger ---
api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')


def _bad_request(message, code='bad_request'):
    return jsonify({'error': code, 'message': message}), 400


def _not_found(message='Resource not found'):
    return jsonify({'error': 'not_found', 'message': message}), 404


def validate_dish_payload(data):
    if not isinstance(data, dict):
        return 'payload_must_be_object'
    if not data.get('name'):
        return 'name_required'
    try:
        if 'price' in data and data['price'] is not None:
            float(data['price'])
    except Exception:
        return 'price_must_be_number'
    return None


def validate_order_payload(data):
    if not isinstance(data, dict):
        return 'payload_must_be_object'
    if not data.get('address'):
        return 'address_required'
    if 'items' in data and not isinstance(data['items'], list):
        return 'items_must_be_array'
    return None


@api_v2_bp.route('/dishes', methods=['GET'])
def v2_get_all_dishes():
    """
    Get list of dishes
    ---
    responses:
      200:
        description: List of dishes
        schema:
          type: array
          items:
            type: object
    """
    dishes = get_all_dish()
    return jsonify([_row_to_dict(d) for d in dishes])


@api_v2_bp.route('/dishes/<int:dish_id>', methods=['GET'])
def v2_get_dish(dish_id):
    """
    Get dish by id
    ---
    parameters:
      - name: dish_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Dish object
      404:
        description: Not Found
    """
    d = get_dish_by_id(dish_id)
    if not d:
        return _not_found()
    return jsonify(_row_to_dict(d))


@api_v2_bp.route('/dishes', methods=['POST'])
def v2_create_dish():
    """
    Create a new dish
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [name]
          properties:
            name: {type: string}
            price: {type: number}
            image: {type: string}
            description: {type: string}
            ingredients: {type: string}
            calories: {type: integer}
    responses:
      201:
        description: Created
      400:
        description: Validation error
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return _bad_request('invalid_json')
    err = validate_dish_payload(data)
    if err:
        return _bad_request(err)
    price = float(data.get('price', 0) or 0)
    new_id = add_dish(data['name'], price, data.get('image',''), data.get('description',''), data.get('ingredients',''), data.get('calories'))
    return jsonify({'id': new_id}), 201


@api_v2_bp.route('/dishes/<int:dish_id>', methods=['PUT'])
def v2_update_dish(dish_id):
    """
    Update dish
    ---
    consumes:
      - application/json
    parameters:
      - name: dish_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
    responses:
      200:
        description: OK
      400:
        description: Validation error
      404:
        description: Not found
    """
    try:
        existing = get_dish_by_id(dish_id)
        if not existing:
            return _not_found()
        try:
            data = request.get_json(force=True)
        except Exception:
            return _bad_request('invalid_json')
        err = validate_dish_payload({**dict(existing), **(data or {})})
        if err:
            return _bad_request(err)
        # merge
        name = data.get('name') or existing['name']
        price = float(data.get('price', existing['price']) or existing['price'])
        image = data.get('image', existing.get('image',''))
        description = data.get('description', existing.get('description',''))
        ingredients = data.get('ingredients', existing.get('ingredients',''))
        calories = data.get('calories', existing.get('calories'))
        update_dish(dish_id, name, price, image, description, ingredients, calories)
        return jsonify({'ok': True})
    except Exception as e:
        print('v2_update_dish error:', e)
        traceback.print_exc()
        return jsonify({'error': 'server_error', 'message': str(e)}), 500


@api_v2_bp.route('/dishes/<int:dish_id>', methods=['DELETE'])
def v2_delete_dish(dish_id):
    """
    Delete dish
    ---
    parameters:
      - name: dish_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: OK
    """
    existing = get_dish_by_id(dish_id)
    if not existing:
        return _not_found()
    delete_dish(dish_id)
    return jsonify({'ok': True})


@api_v2_bp.route('/orders', methods=['GET'])
def v2_get_orders():
    """
    List orders
    ---
    responses:
      200:
        description: List of orders
    """
    orders = get_all_orders()
    return jsonify([_row_to_dict(o) for o in orders])


@api_v2_bp.route('/orders', methods=['POST'])
def v2_create_order():
    """
    Create order
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [address]
          properties:
            name: {type: string}
            phone: {type: string}
            address: {type: string}
            items:
              type: array
              items:
                type: object
                properties:
                  dish_id: {type: integer}
                  qty: {type: integer}
    responses:
      201:
        description: Created
      400:
        description: Validation error
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return _bad_request('invalid_json')
    err = validate_order_payload(data)
    if err:
        return _bad_request(err)
    items = data.get('items', [])
    db = get_db(); cur = db.cursor()
    total = 0.0
    safe_items = []
    for it in items:
        try:
            did = int(it.get('dish_id') if isinstance(it, dict) else it[0])
            qty = int(it.get('qty', 1) if isinstance(it, dict) else (it[1] if len(it) > 1 else 1))
        except Exception:
            continue
        cur.execute('SELECT price FROM dish WHERE id = ?', (did,))
        row = cur.fetchone()
        price_f = 0.0
        if row:
            try:
                price_val = row['price'] if 'price' in row.keys() else row[0]
                price_f = float(price_val)
            except Exception:
                price_f = 0.0
        total += price_f * qty
        safe_items.append({'dish_id': did, 'qty': qty})
    try:
        discount = float(data.get('discount', 0) or 0)
    except Exception:
        discount = 0.0
    discount = max(0.0, min(100.0, discount))
    discounted_total = round(total * (1.0 - discount/100.0), 2)
    order_id = add_order(data.get('name', 'Guest'), data.get('phone', ''), data.get('address', ''), safe_items, discounted_total, discount)
    return jsonify({'id': order_id, 'total': discounted_total, 'discount': discount}), 201


@api_v2_bp.route('/favourites/<int:account_id>', methods=['GET'])
def v2_get_favourites(account_id):
    """
    Get favourites for account
    ---
    parameters:
      - name: account_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of favourites
    """
    favs = get_all_favourites(account_id)
    return jsonify([_row_to_dict(f) for f in favs])


@api_v2_bp.route('/favourites', methods=['POST'])
def v2_add_favourite():
    """
    Add favourite
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required: [dish_id]
          properties:
            dish_id: {type: integer}
            account_id: {type: integer}
    responses:
      201:
        description: Created
      400:
        description: Validation error
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return _bad_request('invalid_json')
    if not data.get('dish_id'):
        return _bad_request('dish_id_required')
    new_id = add_favourite(int(data['dish_id']), int(data['account_id']) if data.get('account_id') is not None else None)
    return jsonify({'id': new_id}), 201


@api_v2_bp.route('/accounts', methods=['GET'])
def v2_get_accounts():
    """
    List accounts
    ---
    responses:
      200:
        description: List of accounts
    """
    accounts = get_all_accounts()
    return jsonify([_row_to_dict(a) for a in accounts])


# --- Legacy non-versioned API to support existing clients / Postman collection ---
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/dishes', methods=['GET'])
def legacy_get_all_dishes():
    return v1_get_all_dishes()


@api_bp.route('/dishes/<int:dish_id>', methods=['GET'])
def legacy_get_dish(dish_id):
    return v1_get_dish(dish_id)


@api_bp.route('/dish/<int:dish_id>', methods=['GET'])
def legacy_get_dish_singular(dish_id):
    # some clients may use /api/dish/:id (singular)
    return v1_get_dish(dish_id)


@api_bp.route('/dishes', methods=['POST'])
def legacy_create_dish():
    return v1_create_dish()


@api_bp.route('/dishes/<int:dish_id>', methods=['PUT'])
def legacy_update_dish(dish_id):
    return v1_create_dish() if request.method == 'POST' else (v1_get_dish(dish_id) if request.method == 'GET' else v1_get_dish(dish_id))


@api_bp.route('/dishes/<int:dish_id>', methods=['DELETE'])
def legacy_delete_dish(dish_id):
    # call v2 delete for stronger behavior
    return v2_delete_dish(dish_id)


@api_bp.route('/orders', methods=['GET'])
def legacy_get_orders():
    return v1_get_orders()


@api_bp.route('/orders', methods=['POST'])
def legacy_create_order():
    return v1_create_order()


@api_bp.route('/accounts', methods=['GET'])
def legacy_get_accounts():
    return v1_get_accounts()


@api_bp.route('/favourites/<int:account_id>', methods=['GET'])
def legacy_get_favourites(account_id):
    return v1_get_favourites(account_id)

