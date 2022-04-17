from flask import Flask, render_template, request, flash
import main
import Queries as qr

app = Flask(__name__)
app.secret_key = "testestest"


@app.route("/")
def start_app():
    return render_template("index.html")


@app.route("/interpretActions", methods=['POST'])
def interpretActions():
    main.interpretActions()
    return render_template("index.html")


@app.route("/addAction", methods=['POST'])
def addAction():
    main.insertAction()
    return render_template("index.html")


@app.route("/deleteAction", methods=['POST'])
def deleteAction():
    qr.deleteAction()
    return render_template("index.html")


@app.route("/viewActions", methods=['POST'])
def viewActions():
    actions = qr.getAllActions()
    formatActions = []
    for s in actions:
        formatActions.append(str(s).replace("(", "").replace(")", "").replace("'", "").replace(",", ""))
    return render_template("actionsPage.html", data=formatActions)


@app.route("/returnMain", methods=['POST'])
def returnMain():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
