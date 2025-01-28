import pickle
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pandas as pd
from sklearn import metrics
import warnings
from convert import convertion
from feature import FeatureExtraction



warnings.filterwarnings('ignore')

file = open("Phishing-detector/newmodel.pkl", "rb")
gbc = pickle.load(file)
file.close()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URLData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2083), nullable=False)
    prediction = db.Column(db.Integer, nullable=False)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/result', methods=['POST', 'GET'])
def predict():
    if request.method == "POST":
        url = request.form["name"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1, 30)
    
        y_pred = gbc.predict(x)[0]
        name = convertion(url, int(y_pred))
        
        # Save the result to the database
        new_url_data = URLData(url=url, prediction=int(y_pred))
        db.session.add(new_url_data)
        db.session.commit()
        
        return render_template("index.html", name=name)

@app.route('/usecases', methods=['GET', 'POST'])
def usecases():
    return render_template('usecases.html')

@app.route('/urls')
def urls():
    url_data = URLData.query.all()
    return render_template('urls.html', url_data=url_data)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)