import psycopg2
from flask import Flask
from flask import redirect, render_template, request

app = Flask(__name__)

conn = psycopg2.connect(dbname='tele', user='postgres',
                        password='nazim080', host='localhost')
cursor = conn.cursor()

sql_query = f"SELECT u_id, f_val, n_val, otc_val, s_val, bldn, bldn_k, app, tele " \
            f"FROM main join fam on main.fam=fam.f_id join nam on main.name_=nam.n_id " \
            f"join otc on main.otc=otc.otc_id join street on main.street=street.s_id;"
cursor.execute(sql_query)

users_list = []

for row in cursor.fetchall():
    user_dict = {'id': row[0],
                 'surname': row[1],
                 'name': row[2],
                 'otc': row[3],
                 'street': row[4],
                 'bldn': row[5],
                 'bldn_k': row[6],
                 'app': row[7],
                 'tele': row[8]}
    users_list.append(user_dict)


@app.route('/')
def index():
    return redirect('http://127.0.0.1:5000/users')


@app.route('/users/')
def users():
    return render_template('list.html', users_list=users_list)


@app.route('/users/add/', methods=['get', 'post'])
def user_add():
    conn = psycopg2.connect(dbname='tele', user='postgres',
                            password='nazim080', host='localhost')
    cursor = conn.cursor()

    if request.method == 'POST':
        surname = request.form.get('surname')
        name = request.form.get('name')
        otc = request.form.get('otc')
        street = request.form.get('street')
        bldn = request.form.get('bldn')
        bldn_k = request.form.get('bldn_k')
        app = request.form.get('app')
        tele = request.form.get('tele')

        personal_data = {'fam': surname,
                         'name': name,
                         'otc': otc,
                         'street': street,
                         'bldn': bldn,
                         'bldn_k': bldn_k,
                         'app': app,
                         'tele': tele}

        for k in personal_data.keys():
            if personal_data[k] is None:
                personal_data[k] = "null"

        sql_list = [f"SELECT count(f_id) FROM fam WHERE f_val='{personal_data['fam']}'",
                    f"SELECT count(n_id) FROM nam WHERE n_val='{personal_data['name']}'",
                    f"SELECT count(otc_id) FROM otc WHERE otc_val='{personal_data['otc']}'",
                    f"SELECT count(s_id) FROM street WHERE s_val='{personal_data['street']}'"]

        sql_insert_list = [f"INSERT INTO fam (f_val) VALUES ('{personal_data['fam']}');",
                           f"INSERT INTO nam (n_val) VALUES ('{personal_data['name']}');",
                           f"INSERT INTO otc (otc_val) VALUES ('{personal_data['otc']}');",
                           f"INSERT INTO street (s_val) VALUES ('{personal_data['street']}');"]
        i = 0
        for sql_checking in sql_list:
            data = []
            cursor.execute(sql_checking, data)
            results = cursor.fetchone()
            conn.commit()
            if results[0] == 0:
                cursor.execute(sql_insert_list[i])
                print("вставка произошла")
            i += 1

        # запрос в main
        sql_query = f"INSERT INTO main (bldn, bldn_k, app, tele, fam, name_, otc, street) VALUES(" \
                    f"{personal_data['bldn']}, {personal_data['bldn_k']}, {personal_data['app']}, {personal_data['tele']}," \
                    f"(SELECT f_id from fam where f_val='{personal_data['fam']}')," \
                    f"(SELECT n_id from nam where n_val='{personal_data['name']}')," \
                    f"(SELECT otc_id from otc where otc_val='{personal_data['otc']}')," \
                    f"(SELECT s_id from street where s_val='{personal_data['street']}'));"

        cursor.execute(sql_query)
        conn.commit()

    return render_template('add.html')


@app.route('/user/<user_id>')
def user(user_id):
    user = ''
    for i in users_list:
        if str(i['id']) == user_id:
            user = i
    return render_template('user_info.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
