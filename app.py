from flask import Flask, render_template, request, redirect, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'notesnest_secret_key'

# MongoDB Config
app.config["MONGO_URI"] = "mongodb+srv://svickyvignesh141:Vignesh7898@cluster0.khuqtfx.mongodb.net/notesnest?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# Routes

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = mongo.db.users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.find_one({'username': username}):
            flash("Username already exists!")
            return redirect('/register')
        users.insert_one({'username': username, 'password': password})
        flash("Registered successfully. Please log in.")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = mongo.db.users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username, 'password': password})
        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            return redirect('/notes')
        flash("Invalid credentials")
        return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'user_id' not in session:
        return redirect('/login')
    
    notes_collection = mongo.db.notes
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        notes_collection.insert_one({
            'user_id': session['user_id'],
            'title': title,
            'content': content
        })
        return redirect('/notes')

    user_notes = notes_collection.find({'user_id': session['user_id']})
    return render_template('notes.html', notes=user_notes)

@app.route('/delete/<note_id>')
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    notes_collection = mongo.db.notes
    note = notes_collection.find_one({'_id': ObjectId(note_id)})
    
    if note and note['user_id'] == session['user_id']:
        notes_collection.delete_one({'_id': ObjectId(note_id)})
    else:
        flash("Unauthorized to delete this note.")
    return redirect('/notes')

if __name__ == '__main__':
    print("✅ Flask is starting...")
    app.run(debug=True)