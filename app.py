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

#define database models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

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



@app.route('/data' , methods = ['POST','GET'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        phone = int(request.form['phone'])
        email = request.form['email']
        subject =request.form['subject']
        message =request.form['message']

        print("Name Of User:",name)
        print("Phone no:",phone)
        print("Email:",email)
        print("subject:",subject)
        print("message:",message)

        return render_template('index.html')
    
    else :
        return render_template('index.html')


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

    img.save('static/img/{}.jpg'.format(COUNT))
    img_arr = cv2.imread('static/img/{}.jpg'.format(COUNT))

    img_arr = cv2.resize(img_arr, (224, 224))
    img_arr = img_arr / 255.0
    img_arr = img_arr.reshape(1, 224, 224, 3)
    predictions = model_corn.predict(img_arr)
    prediction = np.argmax(predictions, axis=1)
    print(prediction[0])

    COUNT += 1
    if prediction[0] == 0:
        return render_template('Output.html', data=["Blight"])
    elif prediction[0] == 1:
        return render_template('Output.html', data=["Common_Rust"])
    elif prediction[0] == 2:
        return render_template('Output.html', data=["Gray_Leaf_Spot"])
    else:
        return render_template('Output.html', data=["Healthy"])



@app.route('/predictiongrape',methods = ['POST'])
def predictiongrape():
    global COUNT
    img = request.files['image']

    img.save('static/img/{}.jpg'.format(COUNT))
    img_arr = cv2.imread('static/img/{}.jpg'.format(COUNT))

    img_arr = cv2.resize(img_arr, (224, 224))
    img_arr = img_arr / 255.0
    img_arr = img_arr.reshape(1, 224, 224, 3)
    predictions = model_grape.predict(img_arr)
    prediction=np.argmax(predictions, axis=1)
    print(prediction[0])
    #
    # x = round(prediction[0])
    # # y = round(prediction[0, 1], 2)
    # preds = np.array([x])
    COUNT += 1
    if prediction[0] == 0:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["Grape___Black_rot'", 'green'])
    elif prediction[0] == 1:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["Grape___Esca_(Black_Measles)", 'red'])
    elif prediction[0] == 2:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", 'red'])
    else:
        # cv2.imwrite('static/images/{}.jpg'.format(COUNT), img)
        return render_template('Output.html', data=["Grape___healthy", 'red'])






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



@app.route('/crop_recommendation' , methods = ['POST','GET'])
def crop_recommendation():
    if request.method == 'POST':
        Nitrogen = float(request.form['Nitrogen'])
        Phosphorus = float(request.form['Phosphorus'])
        Potassium = float(request.form['Potassium'])
        temperature =float(request.form['temperature'])
        humidity =float(request.form['humidity'])
        rainfall =float(request.form['rainfall'])
        ph =float(request.form['ph'])
        # State =request.form['State']
        print(Nitrogen,Phosphorus,Potassium,temperature,humidity,rainfall,ph)

        # Load the Model back from file
        with open("Crop_Recomandation_RF.pkl", 'rb') as file:
            Pickled_RF_Model = pickle.load(file)
        result = Pickled_RF_Model.predict([[Nitrogen,Phosphorus,Potassium,temperature,humidity,ph,rainfall]])
        if result[0] == 20:
            return render_template('crop_recomdation.html', data=["rice",'green'])
        elif result[0] == 11:
            return render_template('crop_recomdation.html', data=["maize",'green'])
        elif result[0] == 3:
            return render_template('crop_recomdation.html', data=["chickpea",'green'])
        elif result[0] == 9:
            return render_template('crop_recomdation.html', data=["kidneybeans",'green'])
        elif result[0] == 18:
            return render_template('crop_recomdation.html', data=["pigeonpeas",'green'])
        elif result[0] == 13:
            return render_template('crop_recomdation.html', data=["mothbeans",'green'])
        elif result[0] == 14:
            return render_template('crop_recomdation.html', data=["mungbean",'green'])
        elif result[0] == 2:
            return render_template('crop_recomdation.html', data=["blackgram",'green'])
        elif result[0] == 10:
            return render_template('crop_recomdation.html', data=["lentil",'green'])
        elif result[0] == 19:
            return render_template('crop_recomdation.html', data=["pomegranate",'green'])
        elif result[0] == 1:
            return render_template('crop_recomdation.html', data=["banana",'green'])
        elif result[0] == 12:
            return render_template('crop_recomdation.html', data=["mango",'green'])
        elif result[0] == 7:
            return render_template('crop_recomdation.html', data=["grapes",'green'])
        elif result[0] == 21:
            return render_template('crop_recomdation.html', data=["watermelon",'green'])
        elif result[0] == 15:
            return render_template('crop_recomdation.html', data=["muskmelon",'green'])
        elif result[0] == 0:
            return render_template('crop_recomdation.html', data=["apple",'green'])
        elif result[0] == 16:
            return render_template('crop_recomdation.html', data=["orange",'green'])
        elif result[0] == 17:
            return render_template('crop_recomdation.html', data=["papaya",'green'])
        elif result[0] == 4:
            return render_template('crop_recomdation.html', data=["coconut",'green'])
        elif result[0] == 6:
            return render_template('crop_recomdation.html', data=["cotton",'green'])
        elif result[0] == 8:
            return render_template('crop_recomdation.html', data=["jute",'green'])

        else:
            return render_template('crop_recomdation.html', data=['coffee','green'])


    else :
        return render_template('crop_recomdation.html')


@app.route('/load_img')
def load_img():
    global COUNT
    return send_from_directory('static/img', "{}.jpg".format(COUNT-1))


if __name__ == '__main__':
    app.run(debug=True)

