from flask import Flask, render_template, flash,url_for, redirect, session, request, send_file, abort
from flask_mysqldb import MySQL
import bcrypt
import io


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'secret' 

mysql = MySQL()
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'mysqluser'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'ecommerce_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()
    
    cur.execute("SELECT * FROM Products")
    products = cur.fetchall()
    cur.close()
    
    return render_template('home.html', categories=categories, products=products)

@app.route('/category/<int:category_id>')
def category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM category")
    categories = cur.fetchall()
    
    cur.execute("SELECT * FROM Products WHERE category_id = %s", (category_id,))
    products = cur.fetchall()
    cur.close()
    
    return render_template('home.html', categories=categories, products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, password,role FROM Users WHERE username = %s", (username,))
        user = cur.fetchone()

        print(user)
        
        if user is None:
            flash('User not found!', 'danger')
            return redirect('/login')
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = username
            session['role'] = user['role']
            print(user['id'])
            flash('Login successful!', 'success')
            return redirect('/')
        else:
            flash('Invalid password!', 'danger')
            return redirect('/login')

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO Users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                        (username, hashed_password.decode('utf-8'), email, role))
            mysql.connection.commit()

            if role == 'seller':
                gstin = request.form['gstin']
                cur.execute("INSERT INTO Sellers (user_id, gstin) VALUES (LAST_INSERT_ID(), %s)", (gstin,))
                mysql.connection.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect('/login')
        except Exception as e:
            mysql.connection.rollback()
            flash('Error during registration: ' + str(e), 'danger')
        finally:
            cur.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'username' not in session:
        flash('Please log in to add items to the cart.', 'danger')
        return redirect('/login')

    quantity = request.form['quantity']
    username = session['username']

    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM Users WHERE username = %s", (username,))
    user = cur.fetchone()
    
    if user:
        user_id = user['id']

        try:
            cur.execute("INSERT INTO Orders (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (user_id, product_id, quantity))
            mysql.connection.commit()
            flash('Product added to cart!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash('Error adding product to cart: ' + str(e), 'danger')
    else:
        flash('User not found.', 'danger')

    cur.close()
    return redirect('/')

@app.route('/cart')
def cart():
    if 'username' not in session:
        flash('Please log in to view your cart.', 'danger')
        return redirect('/login')

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    try:
        cur.execute("""
            SELECT Products.id, Products.name, Products.price, Orders.quantity, Orders.id as order_id
            FROM Orders 
            JOIN Products ON Orders.product_id = Products.id 
            WHERE Orders.user_id = %s
        """, (user_id,))
        
        cart_items = cur.fetchall()

        total_price = 0

        for item in cart_items:
            cur.execute("SELECT CalculateOrderPrice(%s) AS total_price", (item['order_id'],))
            result = cur.fetchone()
            item_total_price = result['total_price']
            total_price += item_total_price
        
        cur.close()

        return render_template('cart.html', cart_items=cart_items, total_price=total_price)

    except Exception as e:
        flash(f'Error fetching cart: {e}', 'danger')
        cur.close()
        return redirect('/')


@app.route('/upload_product', methods=['GET', 'POST'])
def upload_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']
        selected_category = request.form['category']
        new_category = request.form['new_category'].strip()

        if new_category:
            cur = mysql.connection.cursor()
            cur.execute("SELECT category_id FROM category WHERE category_name = %s", (new_category,))
            existing_category = cur.fetchone()

            if not existing_category:
                cur.execute("INSERT INTO category (category_name) VALUES (%s)", (new_category,))
                mysql.connection.commit()
                cur.execute("SELECT category_id FROM category WHERE category_name = %s", (new_category,))
                new_cat_id = cur.fetchone()[0]
                selected_category = new_cat_id

            cur.close()

        if image:
            image_binary = image.read()

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO Products (name, price, description, image, category_id) 
                VALUES (%s, %s, %s, %s, %s)
            """, (name, price, description, image_binary, selected_category))
            mysql.connection.commit()
            cur.close()

        return redirect('/')
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT category_id, category_name FROM category")
    categories = cur.fetchall()
    cur.close()

    return render_template('upload_product.html', categories=categories)



@app.route('/image/<int:image_id>')
def get_image(image_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT image FROM Products WHERE id = %s", (image_id,))
    image_data = cur.fetchone()
    print(image_data['image'])
    if image_data is None:
        abort(404)
    cur.close()
    return send_file(io.BytesIO(image_data['image']), mimetype='image/png')
        
@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    if session.get('role') != 'seller':
        flash('Unauthorized action', 'danger')
        return redirect(url_for('home'))
    
    cur = mysql.connection.cursor()
    
    try:
        cur.execute("SELECT category_name FROM category WHERE category_id = %s", (category_id,))
        category = cur.fetchone()
        
        if not category:
            flash('Category not found', 'danger')
            return redirect(url_for('home'))
        
        cur.execute("DELETE FROM category WHERE category_id = %s", (category_id,))
        mysql.connection.commit()
        
        flash(f'Category {category["category_name"]} and its associated products have been deleted', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        mysql.connection.rollback()
    finally:
        cur.close()
    return redirect(url_for('home'))


@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    if 'role' not in session or session['role'] != 'seller':
        flash('Unauthorized action', 'danger')
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Get updated data from the form
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        selected_category = request.form['category']
        new_category = request.form['new_category'].strip()

        if new_category:
            cur.execute("INSERT IGNORE INTO category (category_name) VALUES (%s)", (new_category,))
            mysql.connection.commit()
            cur.execute("SELECT category_id FROM category WHERE category_name = %s", (new_category,))
            selected_category = cur.fetchone()['category_id']

        # Handle optional image update
        image = request.files['image']
        if image and allowed_file(image.filename):
            image_binary = image.read()
            cur.execute("""
                UPDATE Products SET name = %s, price = %s, description = %s, image = %s, category_id = %s 
                WHERE id = %s
            """, (name, price, description, image_binary, selected_category, product_id))
        else:
            cur.execute("""
                UPDATE Products SET name = %s, price = %s, description = %s, category_id = %s 
                WHERE id = %s
            """, (name, price, description, selected_category, product_id))

        mysql.connection.commit()
        flash('Product updated successfully!', 'success')
        cur.close()
        return redirect(url_for('home'))

    # GET request: Retrieve the product details to prefill the form
    cur.execute("SELECT * FROM Products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.execute("SELECT category_id, category_name FROM category")
    categories = cur.fetchall()
    cur.close()
    
    return render_template('update_product.html', product=product, categories=categories)


app.run(debug=True)