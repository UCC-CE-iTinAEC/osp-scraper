from flask import Flask,render_template,redirect
app = Flask(__name__)

@app.route("/")
def index():
    return "This is a test server"

@app.route("/infinite/<page>")
def infinite(page):
    page_num = int(page)
    return render_template(
        "template.html",
        title=f"infinite page {page}",
        links=[
            "/infinite/{page_num+1}"
        ]
    )

app.run(debug=True)
