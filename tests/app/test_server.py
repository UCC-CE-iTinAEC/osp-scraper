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

@app.route("/path/<path_num>/")
def path_root(path_num):
    next_path = int(path_num) + 1
    return render_template(
        "template.html",
        title=path_num,
        links=[
            f"/path/{next_path}/",
            f"/path/{path_num}/infinite/1",
            f"/redirect?url=/path/{path_num}/redirected?redirected_from=off_path",
            f"/redirect?url=/off_path/{path_num}/redirected?redirected_from=off_path",
            f"/path/{path_num}/redirect?url=/path/{path_num}/redirected?redirected_from=on_path",
            f"/path/{path_num}/redirect?url=/off_path/{path_num}/redirected?redirected_from=on_path",
            f"/path/{path_num}/file/fileA.doc",
            f"/path/{path_num}/file/fileA.docx",
            f"/path/{path_num}/file/fileA.pdf",
            f"/path/{path_num}/file/fileA.rtf",
            f"/path/{path_num}/redirect?url=/path/{path_num}/file/redirected_file.pdf",
            f"/path/{path_num}/iframe?url=/path/{path_num}/iframe_embedded",
            f"/path/{path_num}/frame?url=/path/{path_num}/frame_embedded",
            f"http://httpbin.org/html?source_path={path_num}",
        ]
    )

@app.route("/path/<path_num>/infinite/<page>")
def infinite(path_num, page):
    next_page = int(page) + 1
    return render_template(
        "template.html",
        title=f"infinite page {page}",
        links=[
            f"/path/{path_num}/infinite/{next_page}"
        ]
    )

@app.route("/redirect")
def redirect_to():
    url = request.args.get('url', "/")
    return redirect(url)

@app.route("/path/<path_num>/redirect")
def on_path_redirect(path_num):
    url = request.args.get('url', "/")
    return redirect(url)

@app.route("/path/<path_num>/<page_name>")
def on_path_page(path_num, page_name):
    return render_template(
        "template.html",
        title=page_name,
        links=[]
    )

@app.route("/path/<path_num>/iframe")
def iframe(path_num):
    url = request.args.get('url', "/")
    return render_template(
        "iframe.html",
        title="iframe",
        url=url
    )

@app.route("/path/<path_num>/frame")
def frame(path_num):
    url = request.args.get('url', "/")
    return render_template(
        "frame.html",
        title="frame",
        url=url
    )

@app.route("/off_path/<path_num>/<page_name>")
def off_path_page(path_num, page_name):
    return render_template(
        "template.html",
        title=page_name,
        links=[]
    )

@app.route("/path/<path_num>/file/<filename>")
def file(path_num, filename):
    return send_from_directory("files", filename)

if __name__ == "__main__":
    app.run(debug=True)
