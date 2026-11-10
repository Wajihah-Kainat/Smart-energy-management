from flask import Flask
from subsystem4 import subsystem4_bp

app = Flask(__name__)
app.register_blueprint(subsystem4_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
