from flask import Flask, render_template, request
import urllib.request as ul
import json

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/write_complete", methods=["GET", "POST"])
def index():

    content = ""

    if Flask.request.method == "POST":
        result = Flask.request.form
        content = result.get("content")
        temptoken = result.get("temptoken")

        url = f"http://127.0.0.1:8000/write?content={content},temptoken={temptoken}"
        req = ul.Flask.request(url)
        response = ul.urlopen(Flask.request)
        rescode = response.getcode()

        sendtext = ""

        if rescode == 200:
            responsedata = response.read()

            if responsedata == "success":
                return render_template("write_complete.html", result=result)
            else:
                return render_template("write_fail.html")


@app.route("/write")
def write_page():
    return render_template("write.html")


@app.route("/read")
def read_page():
    values = request.query_string

    subno = request.args.get("subno")
    postno = request.args.get("postno")

    print(subno)
    print(postno)

    url = f"http://127.0.0.1:8000/items?subjectno={subno}&postno={postno}"
    req = ul.Request(url)
    response = ul.urlopen(req)
    rescode = response.getcode()

    sendtext = ""

    if rescode == 200:
        responsedata = response.read()
        responsedata = responsedata.decode("utf-8")
        responsedata = responsedata.replace("\n", "<br>")

    return responsedata


@app.route("/all")
def get_food():
    url = f"http://127.0.0.1:8000/all"

    req = ul.Request(url)
    response = ul.urlopen(req)
    rescode = response.getcode()

    sendtext = ""

    if rescode == 200:
        responsedata = response.read()

        result = responsedata.decode("utf-8")
        result = result.replace("(", "")
        result = result.replace("'", "")
        result = result.replace(")", ",")
        result = result.replace('"', "")
        flist = result.split(",")

        index = 0

        for i in flist:
            print(i)
            sendtext += f"{i}  "
            index += 1

            if index == 4:
                sendtext += "<br>"
                index = 0

    print(sendtext)

    return sendtext


if __name__ == "__main__":
    app.run(debug=True)
