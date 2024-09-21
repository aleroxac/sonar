from flask import Flask
from flask_wtf.csrf import CSRFProtect


app = Flask("sample-app")
csrf = CSRFProtect()
csrf.init_app(app)


@app.route("/status")
def healthcheck():
    return {"status": "UP"}


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
