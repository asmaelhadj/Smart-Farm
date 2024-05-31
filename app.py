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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
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
            password = form.password.data
            try:
                user = User(username=username, email=email, password=password)
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
def inputcotton():
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
    query = request.args.get('query')
    plant_type = request.args.get('plant_type')
    diseases = Disease.query

    if query:
        diseases = diseases.filter(Disease.name.contains(query))
    if plant_type:
        diseases = diseases.filter_by(plant_type=plant_type)

    return render_template('diseases.html', diseases=diseases.all())

@app.route('/disease/<int:disease_id>')
def disease_detail(disease_id):
    disease = Disease.query.get_or_404(disease_id)
    return render_template('disease_detail.html', disease=disease)

@app.route('/predictioncotton',methods = ['POST'])
def predictioncotton():
    global COUNT
    img = request.files['image']

    img.save('static/img/{}.jpg'.format(COUNT))
    img_arr = cv2.imread('static/img/{}.jpg'.format(COUNT))

    img_arr = cv2.resize(img_arr, (224, 224))
    img_arr = img_arr / 255.0
    img_arr = img_arr.reshape(1, 224, 224, 3)
    predictions = model_cotton.predict(img_arr)
    prediction=np.argmax(predictions, axis=1)
    print(prediction[0])
    #
    # x = round(prediction[0])
    # # y = round(prediction[0, 1], 2)
    # preds = np.array([x])
    COUNT += 1
    if prediction[0] == 0:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["diseased cotton leaf", 'green'])
    elif prediction[0] == 1:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["diseased cotton plant", 'red'])
    elif prediction[0] == 2:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["fresh cotton leaf", 'red'])
    else:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["fresh cotton plant", 'red'])


@app.route('/predictioncorn', methods=['POST'])
def predictioncorn():
    global COUNT
    img = request.files['image']
    img_path = f'static/img/{COUNT}.jpg'
    img.save(img_path)
    
    # Preprocess the image
    img_arr = cv2.imread(img_path)
    img_arr = cv2.resize(img_arr, (224, 224)) / 255.0
    img_arr = img_arr.reshape(1, 224, 224, 3)
    
    # Make predictions
    predictions = model_corn.predict(img_arr)
    prediction = np.argmax(predictions, axis=1)[0]
    probability = predictions[0][prediction]

    result_map = {
        0: "Blight",
        1: "Common Rust",
        2: "Gray Leaf Spot",
        3: "Healthy"
    }
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
    
    plot_path = f'static/img/{COUNT}_plot.png'
    plt.savefig(plot_path, bbox_inches='tight', dpi=150)
    plt.close()

    COUNT += 1
    return render_template('Output.html', data=[result, probability, plot_path, img_path])





@app.route('/predictionpotato',methods = ['POST'])
def predictionpotato():
    global COUNT
    img = request.files['image']

    img.save('static/img/{}.jpg'.format(COUNT))
    img_arr = cv2.imread('static/img/{}.jpg'.format(COUNT))

    img_arr = cv2.resize(img_arr, (224, 224))
    img_arr = img_arr / 255.0
    img_arr = img_arr.reshape(1, 224, 224, 3)
    predictions = model_potato.predict(img_arr)
    prediction=np.argmax(predictions, axis=1)
    print(prediction[0])
    #
    # x = round(prediction[0])
    # # y = round(prediction[0, 1], 2)
    # preds = np.array([x])
    COUNT += 1
    if prediction[0] == 0:

        return render_template('Output.html', data=["Potato_Early_blight", 'red'])
    elif prediction[0] == 1:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["Potato_Late_blight", 'red'])

    else:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["Potato_healthy ", 'red'])




@app.route('/predictiontomato', methods=['POST'])
def predictiontomato():
    global COUNT
    img = request.files['image']

    img.save('static/img/{}.jpg'.format(COUNT))
    img_arr = cv2.imread('static/img/{}.jpg'.format(COUNT))

    img_arr = cv2.resize(img_arr, (224, 224))
    img_arr = img_arr / 255.0
    img_arr = img_arr.reshape(1, 224, 224, 3)
    predictions = model_tomato.predict(img_arr)
    prediction = np.argmax(predictions, axis=1)
    print(prediction[0])

    COUNT += 1
    if prediction[0] == 0:
        return render_template('Output.html', data=["Bacterial_spot"])
    elif prediction[0] == 1:
        return render_template('Output.html', data=["Early_blight"])
    elif prediction[0] == 2:
        return render_template('Output.html', data=["Late_blight"])
    elif prediction[0] == 3:
        return render_template('Output.html', data=["Leaf_Mold"])
    elif prediction[0] == 4:
        return render_template('Output.html', data=["Septoria_leaf_spot"])
    elif prediction[0] == 5:
        return render_template('Output.html', data=["Spider_mites Two-spotted_spider_mite"])
    elif prediction[0] == 6:
        return render_template('Output.html', data=["Target_Spot"])
    elif prediction[0] == 7:
        return render_template('Output.html', data=["Tomato_Yellow_Leaf_Curl_Virus"])
    elif prediction[0] == 8:
        return render_template('Output.html', data=["Tomato_mosaic_virus"])
    else:
        return render_template('Output.html', data=["Healthy"])


@app.route('/load_img')
def load_img():
    global COUNT
    return send_from_directory('static/img', "{}.jpg".format(COUNT-1))

#realtime
@app.route('/posts')
@login_required
def posts():
    posts = Post.query.all()
    return render_template('Posts.html', posts=posts)

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    if content:
        post = Post(content=content, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        socketio.emit('new_post', {'content': content, 'username': current_user.username}, to='/')
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
            socketio.emit('new_comment', {'content': content, 'username': current_user.username, 'post_id': post.id}, to='/')
    return render_template('post.html', post=post)

@app.route('/react/<int:post_id>/<reaction_type>')
@login_required
def react(post_id, reaction_type):
    reaction = Reaction(type=reaction_type, post_id=post_id, user_id=current_user.id)
    db.session.add(reaction)
    db.session.commit()
    socketio.emit('new_reaction', {'reaction_type': reaction_type, 'username': current_user.username, 'post_id': post_id}, to='/')
    return redirect(url_for('view_post', post_id=post_id))

if __name__ == '__main__':
    socketio.run(app, debug=True)

