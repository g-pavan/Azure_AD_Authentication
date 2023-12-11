# main.py
from flask import Flask, render_template
from config import AzureADConfig, Config
from authetication.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)
app.config.from_object(AzureADConfig)

# Register the authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
