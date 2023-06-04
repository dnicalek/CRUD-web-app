import mysql.connector
from flask import Flask, request, render_template, redirect
import redis

mydb = mysql.connector.connect(
    host="db",
    user="root",
    password="password",
    database="users",
    port=3306
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255), email VARCHAR(255))")

app = Flask(__name__, static_folder='static')
cache = redis.Redis(host='redis', port=6379)

@app.route('/')
def index():
    users = cache.get('users')
    if users is None:
        mycursor.execute("SELECT * FROM users")
        users = mycursor.fetchall()
        cache.set('users', str(users))
    else:
        users = eval(users)

    return render_template('index.html', users=users)

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        sql = "INSERT INTO users (first_name, last_name, email) VALUES (%s, %s, %s)"
        val = (first_name, last_name, email)
        mycursor.execute(sql, val)
        mydb.commit()
        cache.delete('users')  # Usunięcie danych z pamięci podręcznej po dodaniu użytkownika
        return redirect('/')

    return render_template('add.html')

@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        email = request.form['email']
        sql = "UPDATE users SET email = %s WHERE id = %s"
        val = (email, user_id)
        mycursor.execute(sql, val)
        mydb.commit()
        cache.delete('users')  # Usunięcie danych z pamięci podręcznej po aktualizacji użytkownika
        return redirect('/')
    else:
        sql = "SELECT * FROM users WHERE id = %s"
        val = (user_id,)
        mycursor.execute(sql, val)
        user = mycursor.fetchone()
        return render_template('edit.html', user=user)

@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    sql = "DELETE FROM users WHERE id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    cache.delete('users')  # Usunięcie danych z pamięci podręcznej po usunięciu użytkownika
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
