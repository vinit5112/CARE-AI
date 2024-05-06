import pickle
from flask import Flask, render_template, request,redirect,url_for, session
from sklearn.preprocessing import normalize
import pymysql
import pandas as pd


mydb = pymysql.connect(host="localhost",user="root",password="")
mycursor = mydb.cursor()


mycursor.execute("create database if not exists Tevde")
mydb.commit()

mydb = pymysql.connect(host="localhost",user="root",password="",database="Tevde")
mycursor = mydb.cursor()


mycursor.execute("create table if not exists Feedback(id int not null auto_increment,name varchar(20),contact varchar(20),category varchar(20),email varchar(20),message varchar(20),primary key (id))")
mydb.commit()

app = Flask(__name__)

app.secret_key = 'vinittavde'

@app.route("/create",methods=['POST','GET'])

def create():
    if request.method == "POST":
        
        name = request.form['name']
        contact = request.form['contact']
        category = request.form['category']
        email = request.form['email']
        message = request.form['message']
        
        student = (name,contact,category,email,message)
        
        query = "insert into student(name,contact,category,email,message) value('%s','%s','%s','%s','%s')"
        
        mycursor.execute(query%student)
        mydb.commit()
        
        return redirect('/')
    else:
        return render_template('index1.html')



with open('train_data.pkl', 'rb') as file:
    model = pickle.load(file)

@app.route('/')
def home():
    if "username" in session:  
        username = session['username']
        data = {'username': username}
        return render_template('index1.html',data = data)
    else:
        return render_template('index1.html')



@app.route('/predict', methods=['POST'])
def predict():
    uploaded_file = request.files['excel_file']
    excel_data = pd.read_excel(uploaded_file) 
    input_features = excel_data.iloc[:, 0:178].values.flatten().tolist()

    normalized_features = normalize([input_features])
    prediction = model.predict(normalized_features)
    result = "Seizure Detected" if prediction[0] == 1 else "No Seizure Detected"
    return render_template('eeg.html', result=result)


@app.route('/eeg')
def eeg():
    return render_template('eeg.html')

@app.route('/Lung')
def Lung():
    return render_template('Lung.html')

@app.route('/Heart')
def Heart():
    return render_template('Heart.html')

# MySQL configurations
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'Tevde'

def get_db_connection():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


# Function to create user table if not exists
def create_user_table():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL
        )''')
    connection.commit()
    connection.close()

create_user_table()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    return "Username already exists!"
                else:
                    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                                   (username, email, password))
                    connection.commit()
                    connection.close()
                    return redirect(url_for('login'))
        else:
            return "Passwords do not match!"
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        username = session['username']
        print('username',username)
        data={"username":username}
        return render_template('index1.html',data=data)
    else:
        error = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
                connection.close()

            if user:
                # Redirect to index1.html on successful login
                session['username'] = user[1]
                return redirect('/')
            else:
                error = "Invalid username or password!"

        return render_template('login.html',error=error)
    
@app.route('/logout')
def logout():
    # Clear the session
    session.pop("username")
    # Redirect to the login page
    return redirect(url_for('login'))    

if __name__ == '__main__':
    app.run(debug=True)
