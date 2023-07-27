#Task list:
#
#Create a posting page and add it to flask
#Create a shorts page and add it to flask
#Add email verification
#Create a password reset page and add it to flask
#

import database
from flask import Flask, render_template, request, session, redirect, url_for
from waitress import serve

app = Flask(__name__)

app.secret_key = "v45g209yc7284h27890cgmq5829gm0c45h208cx02g58c74hm20mgut4ccm0"

def main():
    database.init()
    #serve(app, listen="*:5000")
    app.run(host="0.0.0.0", port=5000)
    database.session.commit()

@app.route("/")
def index():
    if "user_id" not in session:
        return(render_template("index.html", loggedin=False))
    elif is_valid_user(session["user_id"]):
        acc = database.session.query(database.Account).filter_by(id=session["user_id"]).first()
        return(render_template("index.html", name=acc.username, displayname=acc.display_name, loggedin=True))
    else:
        return render_template("index.html", loggedin=False)

@app.route("/logout")
def logout():
    del session["user_id"]
    return(redirect(url_for("index")))

@app.route("/test")
def test():
    return database.session.query(database.Post).first().body

def is_username_taken(name:str):
    return database.session.query(database.Account).filter_by(username=name).first() != None

def is_valid_user(id):
    return database.session.query(database.Account).filter_by(id=id).first() != None

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return(render_template("signup.html", error=None))
    else:
        signup = check_valid_signup(request.form)
        if signup["valid"]:
            acc = database.Account.new(request.form["displayname"], request.form["name"], request.form["pswd"])
            database.session.add(acc)
            database.session.commit()
            session["user_id"] = database.session.query(database.Account).filter_by(username=request.form["name"]).first().id
            return redirect(url_for("index"))
        else:
            return render_template("signup.html", error = signup["error"])

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return(render_template("login.html"))
    else:
        if check_login(request.form):
            session["user_id"] = database.session.query(database.Account).filter_by(username=request.form["name"]).first().id
            return redirect(url_for("index"))
        else:
            return(render_template("login.html", error="Invalid Username or Password"))
        

def check_valid_username(name):
    return not is_username_taken(name)

def check_valid_password(password):
    return True

def check_valid_display_name(display_name):
    return True

def check_valid_signup(data):
    if not check_valid_password(data["pswd"]):
        return {"valid":False, "error":None}
    if not check_valid_username(data["name"]):
        return {"valid":False, "error":"Username Taken"}
    if not check_valid_display_name(data["displayname"]):
        return {"valid":False, "error":None}
    return {"valid":True, "error":None}

def check_login(data):
    acc = database.session.query(database.Account).filter_by(username=data["name"]).first()
    return acc != None and acc.password == database.hash_password(data["pswd"])

def get_user_by_id(id):
    return database.session.query(database.Account).filter_by(id=id).first()

@app.route("/post", methods=["POST", "GET"])
def post():
    if is_valid_user(session["user_id"]):
        if request.method == "GET":
            return render_template("post.html", error=None)
        else:
            p = database.Post.new(session["user_id"], request.form["title"], request.form["text"])
            database.session.add(p)
            database.session.commit()
            return redirect(url_for("index"))
    else:
        return(redirect(url_for("login")))

@app.route("/posts")
def view_posts():
    return render_template("posts.html", posts=format_posts())

@app.route("/comment", methods=["POST"])
def comment():
    if is_valid_user(session["user_id"]):
        c = database.Comment.new(session["user_id"], request.form["post_id"], request.form["text"])
    else:
        return redirect(url_for("login"))

@app.route("/comments")
def comments():
    print(format_comments())
    return render_template("comments.html", comments=format_comments())

def format_comments():
    comments = database.session.query(database.Comment).filter_by(post_id=request.args["id"]).order_by(database.Comment.comment_id.desc())
    comments_out = []
    for p in comments:
        comments_out.append(p)
        comments_out[len(comments_out) - 1].name = get_user_by_id(comments_out[len(comments_out) - 1].commenter_id).username
        if len(comments_out) > 50:
            break
    return comments_out

def format_posts():
    posts = database.session.query(database.Post).order_by(database.Post.post_id.desc())
    posts_out = []
    for p in posts:
        posts_out.append(p)
        posts_out[len(posts_out) - 1].name = get_user_by_id(posts_out[len(posts_out) - 1].owner_id).username
        if len(posts_out) > 50:
            break
    return posts_out

if __name__ == "__main__":
    main()