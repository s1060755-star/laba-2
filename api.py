from flask import Blueprint, jsonify, request
from database import (
    get_all_dish, get_dish_by_id, add_dish, update_dish, delete_dish,
    get_all_orders, add_order, get_all_favourites, add_favourite, get_db,
    get_all_accounts
)
import json


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
    order_id = add_order(data.get('name','Guest'), data.get('phone',''), address, safe_items, total)
    return jsonify({'id': order_id, 'total': total}), 201


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
    order_id = add_order(data.get('name', 'Guest'), data.get('phone', ''), data.get('address', ''), safe_items, total)
    return jsonify({'id': order_id, 'total': total}), 201


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
from flask import Blueprint, jsonify, request
from database import (
    get_all_dish, get_dish_by_id, add_dish, update_dish, delete_dish,
    get_all_orders, add_order, get_all_favourites, add_favourite, get_db,
    get_all_accounts
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _row_to_dict(row):
    return dict(row) if row is not None else None


@api_bp.errorhandler(400)
def _handle_400(err):
    return jsonify({'error': 'bad_request', 'message': str(err)}), 400


@api_bp.errorhandler(404)
def _handle_404(err):
    return jsonify({'error': 'not_found', 'message': str(err)}), 404


@api_bp.errorhandler(Exception)
def _handle_exception(err):
    return jsonify({'error': 'server_error', 'message': str(err)}), 500


# --- Dishes ---
@api_bp.route('/dishes', methods=['GET'])
def api_get_all_dishes():
    try:
        dishes = get_all_dish()
        return jsonify([_row_to_dict(d) for d in dishes])
    except Exception as e:
        return _handle_exception(e)


@api_bp.route('/dishes/<int:dish_id>', methods=['GET'])
def api_get_dish(dish_id):
    try:
        d = get_dish_by_id(dish_id)
        if not d:
            return jsonify({'error': 'not_found'}), 404
        return jsonify(_row_to_dict(d))
    except Exception as e:
        return _handle_exception(e)


@api_bp.route('/dishes', methods=['POST'])
def api_create_dish():
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        price = data.get('price', 0)
        image = data.get('image', '')
        description = data.get('description', '')
        ingredients = data.get('ingredients', '')
        calories = data.get('calories', None)
        if not name:
            return jsonify({'error': 'name_required'}), 400
        new_id = add_dish(name, float(price or 0), image, description, ingredients, calories)
        return jsonify({'id': new_id}), 201
    except Exception as e:
        return _handle_exception(e)


@api_bp.route('/dishes/<int:dish_id>', methods=['PUT'])
def api_update_dish(dish_id):
    try:
        data = request.get_json(force=True)
        name = data.get('name', '')
        price = data.get('price', 0)
        image = data.get('image', '')
        description = data.get('description', '')
        ingredients = data.get('ingredients', '')
        calories = data.get('calories', None)
        existing = get_dish_by_id(dish_id)
        if not existing:
            return jsonify({'error': 'not_found'}), 404
        update_dish(dish_id, name or existing['name'], float(price or existing['price']), image or existing.get('image',''), description or existing.get('description',''), ingredients or existing.get('ingredients',''), calories or existing.get('calories'))
        return jsonify({'ok': True})
    except Exception as e:
        return _handle_exception(e)


@api_bp.route('/dishes/<int:dish_id>', methods=['DELETE'])
def api_delete_dish(dish_id):
    try:
        existing = get_dish_by_id(dish_id)
        if not existing:
            return jsonify({'error': 'not_found'}), 404
        delete_dish(dish_id)
        return jsonify({'ok': True})
    except Exception as e:
        return _handle_exception(e)


# --- Orders ---
@api_bp.route('/orders', methods=['GET'])
def api_get_orders():
    try:
        orders = get_all_orders()
        return jsonify([_row_to_dict(o) for o in orders])
    except Exception as e:
        return _handle_exception(e)


@api_bp.route('/orders', methods=['POST'])
def api_create_order():
    try:
        data = request.get_json(force=True)
        name = data.get('name', 'Guest')
        phone = data.get('phone', '')
        address = data.get('address', '')
        items = data.get('items', [])
        if not address:
            return jsonify({'error': 'address_required'}), 400
        # compute total from DB to avoid trusting client
        db = get_db()
        cur = db.cursor()
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
        order_id = add_order(name, phone, address, safe_items, total)
        return jsonify({'id': order_id, 'total': total}), 201
    except Exception as e:
        return _handle_exception(e)


# --- Favourites ---
@api_bp.route('/favourites/<int:account_id>', methods=['GET'])
def api_get_favourites(account_id):
    try:
        favs = get_all_favourites(account_id)
        return jsonify([_row_to_dict(f) for f in favs])
    except Exception as e:
        return _handle_exception(e)


@api_bp.route('/favourites', methods=['POST'])
def api_add_favourite():
    try:
        data = request.get_json(force=True)
        dish_id = data.get('dish_id')
        account_id = data.get('account_id')
        if not dish_id:
            return jsonify({'error': 'dish_id_required'}), 400
        new_id = add_favourite(int(dish_id), int(account_id) if account_id is not None else None)
        return jsonify({'id': new_id}), 201
    except Exception as e:
        return _handle_exception(e)


# --- Accounts ---
@api_bp.route('/accounts', methods=['GET'])
def api_get_accounts():
    try:
        accounts = get_all_accounts()
        return jsonify([_row_to_dict(a) for a in accounts])
    except Exception as e:
        return _handle_exception(e)
