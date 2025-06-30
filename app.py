from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session

# Sample product data
products = [
    {
        'id': 1,
        'name': 'Premium Dog Food',
        'description': 'High-quality nutrition for your canine companion.',
        'price': 250000,
        'image': 'dog_food.jpg'
    },
    {
        'id': 2,
        'name': 'Cat Scratching Post',
        'description': 'Keep your furniture safe with this durable scratching post.',
        'price': 350000,
        'image': 'cat_post.jpg'
    },
    {
        'id': 3,
        'name': 'Bird Cage',
        'description': 'Spacious and comfortable home for your feathered friend.',
        'price': 450000,
        'image': 'bird_cage.jpg'
    },
    {
        'id': 4,
        'name': 'Fish Tank',
        'description': 'Complete aquarium setup for beautiful aquatic displays.',
        'price': 750000,
        'image': 'fish_tank.jpg'
    }
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def product_list():
    return render_template('products.html', products=products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        product_id = int(request.form.get('product_id'))
        
        # Initialize cart if it doesn't exist
        if 'cart' not in session:
            session['cart'] = []
        
        # Find the product
        product = next((p for p in products if p['id'] == product_id), None)
        
        if product:
            # Check if product is already in cart
            cart_item = next((item for item in session['cart'] if item['id'] == product_id), None)
            
            if cart_item:
                # Update quantity if product already in cart
                cart_item['quantity'] += 1
                flash(f"Added another {product['name']} to your cart!", "success")
            else:
                # Add new product to cart
                cart_item = {
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': 1
                }
                session['cart'].append(cart_item)
                flash(f"{product['name']} added to your cart!", "success")
            
            # Force session update
            session.modified = True
            print(f"Cart updated: {session['cart']}")  # Debug print
            
            return redirect(url_for('product_list'))
        else:
            flash("Product not found!", "error")
            return redirect(url_for('product_list'))
    except Exception as e:
        print(f"Error adding to cart: {str(e)}")  # Debug print
        flash(f"Error adding to cart: {str(e)}", "error")
        return redirect(url_for('product_list'))
    
@app.route('/api/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    product = next((p for p in products if p['id'] == id), None)
    if product:
        return jsonify(product)
    else:
        return jsonify({'error': 'Product not found'}), 404


@app.route('/api/products', methods=['GET'])
def get_all_products():
    return jsonify(products)

# PUT (update product)
@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    for product in products:
        if product['id'] == id:
            product['name'] = data.get('name', product['name'])
            product['price'] = data.get('price', product['price'])
            return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

# DELETE product
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    global products
    products = [p for p in products if p['id'] != id]
    return jsonify({'message': 'Product deleted'})

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = {
        "id": data["id"],
        "name": data["name"],
        "price": data["price"]
    }
    products.append(new_product)
    return jsonify(new_product), 201


@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        product_id = int(request.form.get('product_id'))
        
        if 'cart' in session:
            # Find the product in the cart
            for i, item in enumerate(session['cart']):
                if item['id'] == product_id:
                    # Remove the item
                    del session['cart'][i]
                    session.modified = True
                    flash("Item removed from cart!", "success")
                    break
        
        return redirect(url_for('view_cart'))
    except Exception as e:
        flash(f"Error removing from cart: {str(e)}", "error")
        return redirect(url_for('view_cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity'))
        
        if 'cart' in session:
            # Find the product in the cart
            for item in session['cart']:
                if item['id'] == product_id:
                    if quantity > 0:
                        item['quantity'] = quantity
                        flash("Cart updated!", "success")
                    else:
                        # Remove item if quantity is 0
                        session['cart'].remove(item)
                        flash("Item removed from cart!", "success")
                    
                    session.modified = True
                    break
        
        return redirect(url_for('view_cart'))
    except Exception as e:
        flash(f"Error updating cart: {str(e)}", "error")
        return redirect(url_for('view_cart'))

if __name__ == '__main__':
    app.run(debug=True)

