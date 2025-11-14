from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
import pandas as pd
import statsmodels.formula.api as smf 
from sklearn.feature_selection import RFE 
from sklearn.svm import SVR

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

app.config['MYSQL_HOST'] = 'birgwsctdqjseds9gnvv-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'uaxoxacap5wshffb'
app.config['MYSQL_PASSWORD'] = 'DotLN7B4biuLI0J84l6L'
app.config['MYSQL_DB'] = 'birgwsctdqjseds9gnvv'
app.config['MYSQL_PORT'] = 3306
app.config['UPLOADS_FOLDER'] = 'UPLOADS'
os.makedirs(app.config['UPLOADS_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS =    {'xlsx', "xls", 'csv'}

mysql = MySQL(app)
bcrypt = Bcrypt(app)

def alowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

#Register
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == "POST":
        fullName = request.form["full_name"]
        age = request.form["age"]
        phone = request.form["phone"]
        e_mail = request.form["e-mail"]
        userName = request.form["userName"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE UserName=%s", [userName])
        user = cur.fetchone()

        if user == user:
            flash(f"The user {user[4]} already exist")
            return redirect("/register")


        cur.execute("INSERT INTO users (Full_Name, Age, Phone, E_mail, UserName, Password) VALUES (%s, %s, %s, %s, %s, %s)", (fullName, age, phone, e_mail, userName, password))
        mysql.connection.commit()
        cur.close()

        flash("Successful registration")
        return redirect('/')
    return render_template('register.html')

#Log in
@app.route("/login", methods=['POST'])
def login():
    userName = request.form['UserName']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE UserName=%s", [userName])
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.check_password_hash(user[5], password):
        session['Full_name'] = user[0]
        session['UserName'] = user[4]
        flash(f"Welcome, {user[0]}!")
        return redirect('/start')
    else:
        flash("UserName or password incorrect. ")
        return redirect("/")
    
@app.route('/start')
def start():
    if 'Full_name' in session:
        return render_template("upload.html")
    else:
        return redirect('/')

#Adding documents to the data base 
@app.route("/uploads", methods=['POST'])
def uploads_file():
    if 'file' not in request.files:
        flash("Nothing has been selected.")
        return redirect('/start')
    
    file = request.files['file']

    if file.filename == "":
        flash("Nothing has been selected.")
        return redirect("/start")
    
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        flash("We just allowed files Excel (.xlsx, .xls) or csv")
        return redirect("/start")
    
    filepath = os.path.join(app.config['UPLOADS_FOLDER'], file.filename)
    file.save(filepath)

    if file.filename.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)

    columns = df.columns
    clean_columns = [column.strip().lower() for column in columns]

    if clean_columns[-1] != "gain":
        flash(f"The last column it's not called 'Gain'")
        return redirect("/start")
    
    if (clean_columns[0] != "week" and clean_columns[0] != "month"):
        flash(f"The first column it's not called 'Week' or 'Month'")
        return redirect("/start")
    
    df.columns = df.columns.str.strip().str.lower()

    for col in df.columns[1:-1]:  
        new_values = []
        for val in df[col]:
            if isinstance(val, str) and val.isdigit():
                new_values.append(int(val))
            elif isinstance(val, (int, float)):
                new_values.append(val)
            else:
                flash(f"Error: '{val}' en la columna '{col}' no es un número válido.")
                return redirect("/start") 
        df[col] = new_values


    cur = mysql.connection.cursor()
    user_name = session['UserName']
    cur.execute("SELECT UserName FROM users WHERE Full_Name=%s", [session['Full_name']])
    
    for i, row in df.iterrows():
        for col in df.columns:
            value = str(row[col])
            cur.execute(
                "INSERT INTO user_files (user_name, file_name, column_name, value, upload_date) VALUES (%s, %s, %s, %s, NOW())",
                (user_name, file.filename, col, value)
            )

    mysql.connection.commit()
    cur.close()

    flash(f"File {file.filename} upload correctly")
    return redirect('/start')


@app.route("/analysis")
def analysis():
    if 'UserName' not in session:
        return redirect('/')
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT file_name FROM user_files WHERE user_name = %s", [session['UserName']])
    files = cur.fetchall()

    files_content = {}

    report = {}
    rsquared = {}
    report_t = {}
    rsquared_n = {}

    for f in files:
        file_name = f[0]

        cur.execute("SELECT column_name, value FROM user_files WHERE user_name = %s AND file_name = %s", [session['UserName'], file_name])

        rows = cur.fetchall()
        content = {}
        for col, val in rows:
            if col not in content:
                content[col] = []
            content[col].append(val)
        files_content[file_name] = content

        df = pd.DataFrame(content)
        df.columns = df.columns.str.strip().str.lower()

        content_clean = {k.strip().lower(): v for k, v in content.items()}

        last_key = list(content_clean.keys())[-1]
        colums = list(content_clean.keys())[1:-1]
            

        X = df[colums]
        Y = df[last_key]

        if len(colums) < 2:
            selected_columns = colums
        else: 
            estimador = SVR(kernel="linear")
            selector = RFE(estimador, n_features_to_select=2, step=1)
            selector = selector.fit(X, Y)

            selector_ranking = selector.ranking_
            z = []

            for i, val in enumerate(selector_ranking):
                if val == 1:
                    z.append(i)
            
            selected_columns = []

            for i in z: 
                selected_columns.append(colums[i])

        var = "+".join(selected_columns)

        df[selected_columns] = df[selected_columns].apply(pd.to_numeric, errors='coerce')
        df[last_key] = pd.to_numeric(df[last_key], errors='coerce')

        lm = smf.ols(formula=f"{last_key}~{var}", data=df).fit()


        list1 = [lm.params[col] for col in selected_columns]

        if file_name not in report:
            report[file_name] = []

        if file_name not in rsquared:
            rsquared[file_name] = []

        if file_name not in report_t:
            report_t[file_name] = []

        if file_name not in rsquared_n:
            rsquared_n[file_name] = []

        for col, value in zip(selected_columns, list1):
            if value < 0:
                y = lm.params['Intercept'] + (value * 200)
                message_t = [
                    f"📉 Attention: Investment in '{col}' is not recommended."
                ]
                message = [
                    f"- Coefficient: {value:.2f} (it could decrease your profits)",
                    f"- If you invest 200 units, the estimated profit would be: {y:.2f}"
                ]
            else:
                y = lm.params['Intercept'] + (value * 700)
                message_t = [
                    f"✅ Recommendation: Consider investing in '{col}'."
                ]
                message = [
                    f"- Coefficient: {value:.2f} (it could increase your profits)",
                    f"- If you invest 700 units, the estimated profit would be: {y:.2f}"
                ]

            report[file_name].append(message)
            report_t[file_name].append(message_t)

        rsquared[file_name].append(f"⚠️ This model predicts outcomes based on your data, with an accuracy of:")
        rsquared_n[file_name].append(f"{(lm.rsquared * 100):.2f}%")

    cur.close()

    return render_template("analysis.html", files_content=files_content, report=report, rsquared=rsquared, report_t=report_t, rsquared_n=rsquared_n)


def home():
    return render_template('upload.html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port, debug=True)

