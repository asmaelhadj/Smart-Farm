from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import cv2
import pickle
import joblib
import numpy as np
from sklearn.svm import SVC
from keras.models import load_model
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import matplotlib.pyplot as plt
import seaborn as sns
from flask_socketio import SocketIO, send, emit
import tensorflow as tf
from datetime import datetime
# Load environment variables from .env file
load_dotenv()

#load model
model_corn =load_model("AG_Corn_Plant_VGG19 .h5")
#model_cotton =load_model("AG_COTTON_plant_VGG19.h5")
model_grape= load_model("AI_Grape.h5")
model_potato= load_model("AI_Potato_VGG19.h5")
model_tomato= load_model("AI_Tomato_model_inception.h5")


COUNT = 0
app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1

app.secret_key = os.getenv('SECRET_KEY')  # Generates a random secret key each time the app starts

# Define the base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:1234@localhost/farm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app)

#define database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    plant_type = db.Column(db.String(100), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    causes = db.Column(db.Text, nullable=False)
    treatments = db.Column(db.Text, nullable=False)
#models of realtime
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('reactions', lazy=True))

migrate = Migrate(app, db)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Creating an instance of the form
    if request.method == 'POST':
        if form.validate_on_submit():  # Checking if the form is valid
            username = form.username.data
            email = form.email.data
            hashed_password = generate_password_hash(form.password.data)
            try:
                user = User(username=username, email=email, password=hashed_password)
                db.session.add(user)
                db.session.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('Email already exists. Please use a different email.', 'danger')
    return render_template('register.html', form=form)  # Passing the form object to the template

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html', form=form)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    msg = Message(subject=subject, recipients=['asmabelhaj03@gmail.com'])
    msg.body = f"Name: {name}\nPhone: {phone}\nEmail: {email}\n\nMessage:\n{message}"
    
    try:
        mail.send(msg)
        flash('Message sent successfully!', 'success')
    except Exception as e:
        flash(f'Failed to send message: {e}', 'danger')

    return render_template('index.html')

@app.route('/leaf_detection')
def leaf_detection():
    return render_template('leaf_detection.html')

@app.route('/inputapple')
def inputapple():
    return render_template('prediction_apple.html')


@app.route('/inputcorn')
def inputcorn():
    return render_template('prediction_Corn.html')

@app.route('/inputgrape')
def inputgrape():
    return render_template('prediction_Grape.html')

@app.route('/inputpotato')
def inputpotato():
    return render_template('prediction_potato.html')

@app.route('/inputtomato')
def inputtomato():
    return render_template('prediction_tomato.html')


@app.route('/diseases')
def list_diseases():
    plant_type = request.args.get('plant_type')
    disease_name = request.args.get('disease_name')

    query = db.session.query(Disease)

    if plant_type:
        query = query.filter(Disease.plant_type.ilike(f'%{plant_type}%'))
    
    if disease_name:
        query = query.filter(Disease.name.ilike(f'%{disease_name}%'))
    
    diseases = query.all()
    # Extract unique plant types from the filtered diseases
    plant_types = list(set(disease.plant_type for disease in diseases))

    return render_template('diseases.html', diseases=diseases, plant_types=plant_types)

@app.route('/disease/<int:disease_id>')
def disease_detail(disease_id):
    disease = Disease.query.get_or_404(disease_id)
    return render_template('disease_detail.html', disease=disease)

def preprocess_image(image_path):
    img_arr = cv2.imread(image_path)
    img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    img_arr = tf.convert_to_tensor(img_arr, dtype=tf.float32)
    img_arr = tf.image.resize(img_arr, [224, 224]) / 255.0  # Resize and rescale
    img_arr = tf.expand_dims(img_arr, axis=0)  # Add batch dimension
    return img_arr

def predict_and_plot(model, img_arr, result_map, count):
    predictions = model.predict(img_arr)
    prediction = np.argmax(predictions, axis=1)[0]
    probability = predictions[0][prediction]

    result = result_map.get(prediction, "Unknown")

    # Plot the probabilities
    classes = list(result_map.values())
    probabilities = predictions[0]

    plt.figure(figsize=(10, 6))
    sns.set(style="whitegrid")
    sns.barplot(x=probabilities, y=classes, palette="viridis")
    plt.xlabel('Probability', fontsize=14)
    plt.ylabel('Disease', fontsize=14)
    plt.title('Prediction Probabilities', fontsize=16)
    plt.xlim(0, 1)
    for index, value in enumerate(probabilities):
        plt.text(value, index, f'{value:.2f}', color='black', ha="left", va="center", fontsize=12)

    plot_path = f'static/img/{count}_plot.png'
    plt.savefig(plot_path, bbox_inches='tight', dpi=150)
    plt.close()

    # Fetch the disease details from the database
    disease = Disease.query.filter_by(name=result).first()

    return result, probability, plot_path, disease

@app.route('/predictiongrape', methods=['POST'])
def predictiongrape():
    global COUNT
    img = request.files['image']
    img_path = f'static/img/{COUNT}.jpg'
    img.save(img_path)
    
    img_arr = preprocess_image(img_path)
    
    result_map = {
        0: "Diseased: Black rot",
        1: "Diseased: Esca (Black Measles)",
        2: "Diseased: Leaf blight (Isariopsis)",
        3: "Healthy"
    }
    
    result, probability, plot_path, disease = predict_and_plot(model_grape, img_arr, result_map, COUNT)
    
    COUNT += 1
    return render_template('Output.html', data=[result, probability, plot_path, img_path], disease=disease)

@app.route('/predictioncorn', methods=['POST'])
def predictioncorn():
    global COUNT
    img = request.files['image']
    img_path = f'static/img/{COUNT}.jpg'
    img.save(img_path)
    
    img_arr = preprocess_image(img_path)
    
    result_map = {
        0: "Diseased: Northern Leaf Blight",
        1: "Diseased: Common rust",
        2: "Diseased: Cercospora leaf spot",
        3: "Healthy"
    }
    
    result, probability, plot_path, disease = predict_and_plot(model_corn, img_arr, result_map, COUNT)
    
    COUNT += 1
    return render_template('Output.html', data=[result, probability, plot_path, img_path], disease=disease)

@app.route('/predictionapple', methods=['POST'])
def predictionapple():
    global COUNT
    img = request.files['image']
    img_path = f'static/img/{COUNT}.jpg'
    img.save(img_path)
    
    img_arr = preprocess_image(img_path)
    
    result_map = {
        0: "Diseased: Scab",
        1: "Diseased: Black rot",
        2: "Diseased: Cedar apple rust",
        3: "Healthy"
    }
    
    result, probability, plot_path, disease = predict_and_plot(model_apple, img_arr, result_map, COUNT)
    
    COUNT += 1
    return render_template('Output.html', data=[result, probability, plot_path, img_path], disease=disease)

@app.route('/predictionpotato', methods=['POST'])
def predictionpotato():
    global COUNT
    img = request.files['image']
    img_path = f'static/img/{COUNT}.jpg'
    img.save(img_path)
    
    img_arr = preprocess_image(img_path)
    
    result_map = {
        0: "Diseased: Early blight",
        1: "Diseased: Late blight",
        2: "Healthy"
    }
    
    result, probability, plot_path, disease = predict_and_plot(model_potato, img_arr, result_map, COUNT)
    
    COUNT += 1
    return render_template('Output.html', data=[result, probability, plot_path, img_path], disease=disease)

@app.route('/predictiontomato', methods=['POST'])
def predictiontomato():
    global COUNT
    img = request.files['image']
    img_path = f'static/img/{COUNT}.jpg'
    img.save(img_path)
    
    img_arr = preprocess_image(img_path)
    
    result_map = {
        0: "Diseased: Bacterial spot",
        1: "Diseased: Early Blight",
        2: "Diseased: Late Blight",
        3: "Diseased: Leaf Mold",
        4: "Diseased: Septoria Leaf Spot",
        5: "Diseased: Two-spotted spider mite",
        6: "Diseased: Target Spot",
        7: "Diseased: Yellow Leaf Curl Virus",
        8: "Diseased: Tomato mosaic virus",
        9: "Healthy"
    }
    
    result, probability, plot_path, disease = predict_and_plot(model_tomato, img_arr, result_map, COUNT)
    
    COUNT += 1
    return render_template('Output.html', data=[result, probability, plot_path, img_path], disease=disease)


@app.route('/load_img')
def load_img():
    global COUNT
    return send_from_directory('static/img', "{}.jpg".format(COUNT-1))

#realtime
@app.route('/posts')
@login_required
def posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_with_comments = []
    for post in posts:
        recent_comment = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).first()
        posts_with_comments.append({
            'post': post,
            'recent_comment': recent_comment
        })
    return render_template('posts.html', posts_with_comments=posts_with_comments)

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    if content:
        post = Post(content=content, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        socketio.emit('new_post', {'content': content, 'username': current_user.username, 'post_id': post.id, 'timestamp': post.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, broadcast=True)
    return redirect(url_for('posts'))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
            db.session.add(comment)
            db.session.commit()
            socketio.emit('new_comment', {
                'content': content,
                'username': current_user.username,
                'post_id': post.id,
                'comment_id': comment.id,
                'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }, broadcast=True)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.asc()).all()
    return render_template('post.html', post=post, comments=comments)


@app.route('/react/<int:post_id>/<reaction_type>')
@login_required
def react(post_id, reaction_type):
    reaction = Reaction(type=reaction_type, post_id=post_id, user_id=current_user.id)
    db.session.add(reaction)
    db.session.commit()
    socketio.emit('new_reaction', {'reaction_type': reaction_type, 'username': current_user.username, 'post_id': post_id}, broadcast=True)
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/comment', methods=['POST'])
@login_required
def comment():
    post_id = request.form.get('post_id')
    content = request.form.get('content')
    if content and post_id:
        post = Post.query.get_or_404(post_id)
        comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        socketio.emit('new_comment', {
            'content': content,
            'username': current_user.username,
            'post_id': post.id,
            'comment_id': comment.id,
            'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }, broadcast=True)
    return redirect(url_for('view_post', post_id=post_id))

if __name__ == '__main__':
    socketio.run(app, debug=True)

