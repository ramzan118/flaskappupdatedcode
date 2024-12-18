import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
from pymongo import MongoClient

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flask_user'
app.config['MYSQL_PASSWORD'] = 'StrongP@ssword123'
app.config['MYSQL_DB'] = 'mariadb'

mysql = MySQL(app)

# Configure MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['mydatabase']
    collection = db['mycollection']
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# MongoDB form submission
@app.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']

        # Log the received form data
        app.logger.info(f"Received form data: name={name}, email={email}, phone={phone}, subject={subject}, message={message}")

        # Insert data into MongoDB
        collection.insert_one({
            "name": name,
            "email": email,
            "phone": phone,
            "subject": subject,
            "message": message
        })
        app.logger.info("Data inserted into MongoDB successfully")
    except Exception as e:
        app.logger.error(f"Error inserting data into MongoDB: {e}")
    return redirect(url_for('index'))


# MySQL DB connectivity check
@app.route('/check_db')
def check_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        return f"Connected to database: {db_name[0]}"
    except Exception as e:
        return str(e)


# MongoDB connectivity check
@app.route('/test-mongo-connection')
def test_mongo_connection():
    try:
        # Insert a test document into the MongoDB collection
        data = {'name': 'Test User', 'email': 'test@example.com'}
        collection.insert_one(data)
        return 'Test document inserted successfully!'
    except Exception as e:
        return str(e)


# Configure logging to a file
file_handler = logging.FileHandler('app.log')  # Specify log file
file_handler.setLevel(logging.DEBUG)  # Set the desired logging level
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)


@app.route('/')
def index():
    app.logger.info("Index page accessed")
    return render_template('index.html')


@app.route('/about')
def about():
    app.logger.info("About page accessed")
    return render_template('about.html')


@app.route('/services')
def services():
    app.logger.info("Services page accessed")
    return render_template('services.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        app.logger.debug(request.form)
        required_fields = ['name', 'email', 'phone', 'subject', 'message']
        for field in required_fields:
            if field not in request.form:
                return jsonify({"error": f"{field.capitalize()} is required"}), 400

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']

        # Insert data into the MySQL database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO contacts (name, email, phone, subject, message) VALUES (%s, %s, %s, %s, %s)",
                       (name, email, phone, subject, message))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Success", "phone": phone}), 200
    else:
        return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
