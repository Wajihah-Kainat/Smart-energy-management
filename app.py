import os
from subsystem3 import create_app

app = create_app({
    "DATABASE": os.getenv("DATABASE_PATH", "instance/smart_energy.sqlite3"),
    "SECRET_KEY": os.getenv("SECRET_KEY", "local-development-only"),
    "TESTING": False,
})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
