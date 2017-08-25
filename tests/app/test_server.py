from flask import Flask, render_template, redirect, request, send_from_directory
app = Flask(__name__)

@app.route("/")
def index():
    return "This is a test server"

@app.route("/start_path/")
def start():
    return render_template(
        "template.html",
        title="start page",
        links=[
            "/"
        ]
    )

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

@app.route("/redirect")
def redirect_to():
    path = request.args.get('path', "/")
    return redirect(path)

@app.route("/file/<filename>")
def file(filename):
    return send_from_directory("files", filename)

if __name__ == "__main__":
    app.run(debug=True)
