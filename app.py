


from app import create_app
from flask import jsonify, render_template

app = create_app()


@app.route("/api/hello", methods=["GET"])
def api_hello():
    return jsonify({"msg": "Hello depuis l'API !"})


# Route pour le frontend de test
@app.route("/test")
def test_page():
    return render_template("front_test.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)