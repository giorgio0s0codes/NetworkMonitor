from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm
import mysql.connector


app = Flask(__name__)

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="redmo",
        password="210681",
        database="monitor",
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )


def fetch_posts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Fetch results as dictionaries
    try:
        sql_fetch = "SELECT author, title, content, date_posted FROM posts"
        cursor.execute(sql_fetch)
        posts = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        posts = []
    finally:
        cursor.close()
        connection.close()
    return posts


def fetch_buildings():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Fetch results as dictionaries
    try:
        sql_fetch = "SELECT id, name, created_at FROM buildings"
        cursor.execute(sql_fetch)
        buildings = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        buildings = []
    finally:
        cursor.close()
        connection.close()
    return buildings


def fetch_traceroute_logs(building_id, limit=3):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Fetch results as dictionaries
    try:
        sql_fetch = """
        SELECT hop, hostname, ip_address
        FROM tracer_logs
        WHERE building_id = %s
        ORDER BY hop ASC
        LIMIT %s
        """
        cursor.execute(sql_fetch, (building_id, limit))
        traceroute_logs = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        traceroute_logs = []
    finally:
        cursor.close()
        connection.close()
    return traceroute_logs


@app.route("/")
@app.route("/home")
def home():
    buildings = fetch_buildings()  # Fetch buildings dynamically
    return render_template('home.html', buildings=buildings)


@app.route("/building")
def building():
    posts = fetch_posts()  # Fetch posts dynamically
    return render_template('building.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@blog.com" and form.password.data == "password":
            flash("You have been logged in!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/building/<int:building_id>", methods=["GET", "POST"])
def building_details(building_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        sql_fetch = "SELECT * FROM buildings WHERE id = %s"
        cursor.execute(sql_fetch, (building_id,))
        building = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        building = None
    finally:
        cursor.close()
        connection.close()

    if not building:
        return f"Building with ID {building_id} not found.", 404

    traceroute_logs = []
    if request.method == "POST":
        traceroute_logs = fetch_traceroute_logs(building_id)

    return render_template("building_details.html", building=building, traceroute_logs=traceroute_logs)


if __name__ == "__main__":
    app.run(debug=True)
