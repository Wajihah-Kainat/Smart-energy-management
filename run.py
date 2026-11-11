# Starts the web application.
from app import create_app

app = create_app()

if __name__ == "__main__":
    # host 0.0.0.0 lets Docker reach the app from outside the container
    app.run(host="0.0.0.0", port=5000, debug=False)
