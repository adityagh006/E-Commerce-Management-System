# E-commerce Management System
A Flask-based e-commerce platform with MySQL backend that allows both customers and sellers to interact with the marketplace. The system features user authentication, product management, shopping cart functionality, and category organization.


## Features

### User Management
- User registration with role selection (customer/seller)
- Secure login/logout functionality
- Role-based access control
- Special seller registration with GSTIN verification

### Product Management
- Product listing with images
- Product categorization
- CRUD operations for products (sellers only)
- Image upload and storage
- Price management

### Category System
- Dynamic category creation
- Category-based product filtering
- Category management for sellers
- Cascade deletion of products when category is removed

### Shopping Cart
- Add products to cart with quantity selection
- View cart contents
- Calculate total prices
- Order management

### UI Features
- Responsive Bootstrap-based design
- User-friendly navigation
- Flash messages for user feedback
- Clean and intuitive interface

### Technical Stack
- Backend: Python Flask
- Database: MySQL
- Frontend: HTML, Bootstrap 4.5
- Authentication: bcrypt for password hashing
- Session Management: Flask sessions

### Prerequisites
- Python 3.x
- MySQL Server
- pip (Python package manager)


##Installation

### Clone the repository:
```bash
clone https://github.com/yourusername/ecommerce-management-system.git
cd ecommerce-management-system
```

### Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install required packages:
```bash
pip install flask flask-mysqldb bcrypt
```

### Set up the MySQL database:
```bash
mysql -u root -p < db.sql
```

### Configure the database connection in app.py:
```python
app.config['MYSQL_HOST'] = 'your_host'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'ecommerce_db'
```


## Running the Application

1. Start the Flask application:
```bash
python app.py
```
2. Access the application at http://localhost:5000


## Database Schema

### Users Table

- id (Primary Key)
- username (Unique)
- password (Hashed)
- email
- role (customer/seller)

### Products Table
- id (Primary Key)
- name
- price
- description
- image (LONGBLOB)
- category_id (Foreign Key)

### Category Table
- category_id (Primary Key)
- category_name

### Orders Table
- id (Primary Key)
- user_id (Foreign Key)
- product_id (Foreign Key)
- quantity
- order_date

### Sellers Table
- id (Primary Key)
- user_id (Foreign Key)
- gstin


## Security Features
- Password hashing using bcrypt
- Session-based authentication
- Role-based access control
- SQL injection protection through parameterized queries
- CSRF protection through Flask-WTF
- Secure file upload handling

## Contributing
1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request


## License
This project is licensed under the MIT License - see the LICENSE.md file for details


##Acknowledgments
- Flask documentation and community
- Bootstrap team for the frontend framework
- MySQL community
