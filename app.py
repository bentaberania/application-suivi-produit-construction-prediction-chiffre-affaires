from datetime import datetime
from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# Connection to the MySQL database
conn_mysql = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rania@123",
    database="Holding"
)

# Flask application setup
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)

class PersonnelForm(FlaskForm):
    nom = StringField('Nom', validators=[InputRequired()])
    prenom = StringField('Prénom', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    mot_passe = PasswordField('Mot de passe', validators=[InputRequired()])
    telephone = StringField('Téléphone', validators=[InputRequired()])
    submit = SubmitField('Ajouter/Modifier')

@app.route('/delete_personnel', methods=['POST'])
def delete_personnel():
    data = request.get_json()
    personnel_id = data.get('personnel_id')
    if personnel_id:
        try:
            cursor = conn_mysql.cursor()
            cursor.execute("DELETE FROM personnel WHERE id = %s", (personnel_id,))
            conn_mysql.commit()
            return jsonify({'message': 'Personnel supprimé avec succès'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'ID du personnel manquant dans la requête'}), 400

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = PersonnelForm()
    if form.validate_on_submit():
        nom = form.nom.data
        prenom = form.prenom.data
        email = form.email.data
        mot_passe = form.mot_passe.data
        telephone = form.telephone.data
        personnel_id = request.form.get('personnel_id')
        cursor = conn_mysql.cursor()

        if personnel_id == 'new':
            cursor.execute("INSERT INTO agent_securite (nom, prenom, email, mot_passe, telephone) VALUES (%s, %s, %s, %s, %s)", 
                           (nom, prenom, email, mot_passe, telephone))
        else:
            cursor.execute("UPDATE agent_securite SET nom=%s, prenom=%s, email=%s, mot_passe=%s, telephone=%s WHERE id=%s", 
                           (nom, prenom, email, mot_passe, telephone, personnel_id))
        
        conn_mysql.commit()
        return redirect(url_for('profile'))

    cursor = conn_mysql.cursor(dictionary=True)
    cursor.execute("SELECT * FROM agent_securite")
    agent_securites = cursor.fetchall()

    cursor.execute("SELECT * FROM agent_controle")
    agent_controles = cursor.fetchall()

    cursor.execute("SELECT * FROM admin")
    admins = cursor.fetchall()

    return render_template('profile.html', form=form, agent_securites=agent_securites, agent_controles=agent_controles, admins=admins)

@app.route('/chiffre', methods=['GET', 'POST'])
def chiffre():
    return render_template('chiffre.html')

@app.route('/qrbar', methods=['GET', 'POST'])
def qrbar():
    return render_template('qrbar.html')

@app.route('/entree')
def entree():
    return render_template('entree.html')

@app.route('/sortie')
def sortie():
    return render_template('sortie.html')

class BonDeLivraison:
    def __init__(self, conn_mysql):
        self.conn_mysql = conn_mysql

    def verifier_code_bv(self, code_bv):
        cursor = self.conn_mysql.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Bon_De_Livraison WHERE Code_BV = %s", (code_bv,))
            bon_de_livraison = cursor.fetchone()
            if bon_de_livraison:
                print(f"Code BV {code_bv} trouvé dans la table Bon_De_Livraison.")
            else:
                print(f"Le code BV {code_bv} n'existe pas dans la table Bon_De_Livraison.")
            cursor.fetchall()  # Consume any remaining results to avoid "Unread result found" error
            return bon_de_livraison
        finally:
            cursor.close()

@app.route('/submit_sortie', methods=['POST'])
def submit_sortie():
    code_bv = request.form.get('code_bv')
    print("Code BV soumis :", code_bv)

    bon_de_livraison_manager = BonDeLivraison(conn_mysql)
    bon_de_livraison = bon_de_livraison_manager.verifier_code_bv(code_bv)

    if bon_de_livraison:
        cursor = conn_mysql.cursor(dictionary=True)
        try:
            etat_sortie = True
            cursor.execute("SELECT * FROM Audit WHERE Code_BV = %s", (code_bv,))
            existing_audit = cursor.fetchone()
            cursor.fetchall()  # Consume any remaining results

            if existing_audit:
                # Mettre à jour le nombre de sorties
                new_flg_sortie = bon_de_livraison['FLG_sortie'] + 1
                cursor.execute("UPDATE Bon_De_Livraison SET FLG_sortie = %s WHERE Code_BV = %s", (new_flg_sortie, code_bv))
                if new_flg_sortie > 1:
                    etat_sortie = False
            else:
                # Insérer une nouvelle entrée dans la table Audit
                now = datetime.now()
                cursor.execute("INSERT INTO Audit (Code_BV, DateTimeScan, TypeScan) VALUES (%s, %s, %s)",
                               (code_bv, now, 'Sortie'))

                # Mettre à jour le nombre de sorties dans Bon_De_Livraison
                new_flg_sortie_bon_de_livraison = bon_de_livraison['FLG_sortie'] + 1
                cursor.execute("UPDATE Bon_De_Livraison SET FLG_sortie = %s WHERE Code_BV = %s", (new_flg_sortie_bon_de_livraison, code_bv))

            conn_mysql.commit()
        finally:
            cursor.close()

        # Récupérer les données spécifiques pour le Code_BV soumis
        cursor = conn_mysql.cursor(dictionary=True)
        cursor.execute("SELECT Bon_De_Livraison.Code_BL, Bon_De_Livraison.FLG_sortie FROM Bon_De_Livraison WHERE Bon_De_Livraison.Code_BV = %s", (code_bv,))
        data = cursor.fetchall()
        cursor.close()

        if etat_sortie:
            return render_template('sortie_reussie.html', data=data)
        else:
            return render_template('sortie_echouee.html', data=data)
    else:
        print("Sortie Interdite: Le code BV soumis est invalide ou n'existe pas.")
        return redirect(url_for('sortie_echouee'))

@app.route('/submit_entree', methods=['POST'])
def submit_entree():
    code_bv = request.form.get('code_bv')
    print("Code BV soumis :", code_bv)

    bon_de_livraison_manager = BonDeLivraison(conn_mysql)
    bon_de_livraison = bon_de_livraison_manager.verifier_code_bv(code_bv)

    if bon_de_livraison:
        cursor = conn_mysql.cursor(dictionary=True)
        try:
            etat_entree = True  # Initialiser l'état d'entrée

            if bon_de_livraison['FLG_sortie'] > 0:
                now = datetime.now()
                cursor.execute(
                    "INSERT INTO Audit (Code_BV, DateTimeScan, TypeScan) VALUES (%s, %s, %s)",
                    (bon_de_livraison['Code_BV'], now, 'Entrée')
                )

                new_flg_entree = bon_de_livraison['FLG_entre'] + 1
                cursor.execute(
                    "UPDATE Bon_De_Livraison SET FLG_entre = %s WHERE Code_BV = %s",
                    (new_flg_entree, code_bv)
                )
                conn_mysql.commit()

                # Vérifier si FLG_entre > 1 et mettre à jour l'état d'entrée
                if new_flg_entree > 1:
                    etat_entree = False

                # Récupérer les données spécifiques pour le Code_BV soumis
                cursor.execute(
                    "SELECT Code_BL, FLG_entre, cachete, signe FROM Bon_De_Livraison WHERE Code_BV = %s",
                    (code_bv,)
                )
                data = cursor.fetchall()

                # Afficher la page appropriée en fonction de l'état d'entrée
                if etat_entree:
                    return render_template('entree_reussie.html', data=data, code_bv=code_bv)
                else:
                    return render_template('entree_echouee.html', data=data)
            else:
                cursor.execute(
                    "SELECT Code_BL, FLG_entre FROM Bon_De_Livraison WHERE Code_BV = %s",
                    (code_bv,)
                )
                data = cursor.fetchall()

                return render_template('entree_echouee.html', data=data)
        finally:
            cursor.close()
    else:
        print("Entrée Interdite: Le code BV soumis est invalide ou n'existe pas.")
        return redirect(url_for('entree_echouee'))

@app.route('/submit_cachete_signe', methods=['POST'])
def submit_cachete_signe():
    code_bv = request.form.get('code_bv')
    code_bls = request.form.getlist('code_bl')
    cachete_values = request.form.getlist('cachete')
    signe_values = request.form.getlist('signe')

    cursor = conn_mysql.cursor(dictionary=True)
    try:
        for code_bl, cachete, signe in zip(code_bls, cachete_values, signe_values):
            cachete_bool = cachete == 'Oui'
            signe_bool = signe == 'Oui'
            cursor.execute(
                "UPDATE Bon_De_Livraison SET cachete = %s, signe = %s WHERE Code_BL = %s AND Code_BV = %s",
                (cachete_bool, signe_bool, code_bl, code_bv)
            )
        conn_mysql.commit()

        # Récupérer les données spécifiques pour le Code_BV soumis après la mise à jour
        cursor.execute(
            "SELECT Code_BL, FLG_entre, cachete, signe FROM Bon_De_Livraison WHERE Code_BV = %s",
            (code_bv,)
        )
        data = cursor.fetchall()
    finally:
        cursor.close()

    return render_template('entree_reussie.html', data=data, code_bv=code_bv)

@app.route('/entree_reussie')
def entree_reussie():
    return render_template('entree_reussie.html')

@app.route('/entree_echouee')
def entree_echouee():
    return render_template('entree_echouee.html')

@app.route('/sortie_reussie')
def sortie_reussie():
    return render_template('sortie_reussie.html')

@app.route('/sortie_echouee')
def sortie_echouee():
    return render_template('sortie_echouee.html')

def get_audit_data(limit, offset):
    try:
        with conn_mysql.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM Audit LIMIT %s OFFSET %s", (limit, offset))
            audit_data = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) AS total FROM Audit")
            audit_data_length = cursor.fetchone()['total']
        return audit_data, audit_data_length
    except Exception as e:
        print("Erreur lors de la récupération des données d'audit :", e)
        return [], 0

def get_details_by_code_bv(code_bv):
    try:
        with conn_mysql.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT Code_BL, FLG_entre, FLG_sortie, cachete, signe FROM Bon_De_Livraison WHERE Code_BV = %s", (code_bv,))
            details = cursor.fetchall()
        return details
    except Exception as e:
        print("Erreur lors de la récupération des détails :", e)
        return []

@app.route('/suivi_voyage', methods=['GET', 'POST'])
def suivi_voyage():
    page = request.args.get('page', 1, type=int)
    limit = 10
    offset = (page - 1) * limit
    audit_data, audit_data_length = get_audit_data(limit, offset)
    return render_template('suivi_voyage.html', audit_data=audit_data, page=page, audit_data_length=audit_data_length, limit=limit)

@app.route('/filter_audit', methods=['GET'])
def filter_audit():
    date = request.args.get('date')
    codeBV = request.args.get('codeBV')
    typeScan = request.args.get('typeScan')

    try:
        with conn_mysql.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM Audit WHERE 1=1"
            params = []
            if date:
                sql += " AND DateTimeScan LIKE %s"
                params.append(date + '%')
            if codeBV:
                sql += " AND Code_BV = %s"
                params.append(codeBV)
            if typeScan:
                sql += " AND TypeScan = %s"
                params.append(typeScan)

            cursor.execute(sql, params)
            audit_data = cursor.fetchall()

        table_html = ''
        for entry in audit_data:
            table_html += f'<tr><td>{entry["Code_BV"]}</td><td>{entry["DateTimeScan"]}</td><td>{entry["TypeScan"]}</td></tr>'
        return table_html
    except Exception as e:
        print("Erreur lors du filtrage des données d'audit :", e)
        return ''

@app.route('/get_details/<code_bv>', methods=['GET'])
def get_details(code_bv):
    try:
        with conn_mysql.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT Code_BL, FLG_entre, FLG_sortie, cachete, signe FROM Bon_De_Livraison WHERE Code_BV = %s", (code_bv,))
            details = cursor.fetchall()
        return jsonify(details)
    except Exception as e:
        print("Erreur lors de la récupération des détails :", e)
        return jsonify([])
    
def hash_existing_passwords():
    try:
        with conn_mysql.cursor() as cursor:
            tables = ['agent_securite', 'agent_controle', 'admin']
            for table in tables:
                cursor.execute(f"SELECT id, mot_passe FROM {table}")
                users = cursor.fetchall()
                for user in users:
                    user_id, plain_password = user
                    hashed_password = generate_password_hash(plain_password)
                    cursor.execute(f"UPDATE {table} SET mot_passe = %s WHERE id = %s", (hashed_password, user_id))
                conn_mysql.commit()
    except Exception as e:
        print(f"Erreur lors du hachage des mots de passe : {e}")

#safe hadi ka execute mra whda hta nzid chihaja f DB o nhyd comment hta run o nrj3o
#hash_existing_passwords()

def check_login(email, mot_passe, table):
    cursor = conn_mysql.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.fetchall()  # Consommer tous les résultats restants pour éviter une erreur "Résultat non lu trouvé"
        
        if user and check_password_hash(user['mot_passe'], mot_passe):
            return True
        return False
    finally:
        cursor.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        mot_passe = request.form['mot_passe']

        if check_login(email, mot_passe, 'agent_securite'):
            return redirect(url_for('qrbar'))
        elif check_login(email, mot_passe, 'agent_controle'):
            return redirect(url_for('suivi_voyage'))
        elif check_login(email, mot_passe, 'admin'):
            return redirect(url_for('chiffre'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/logout_confirm')
def logout_confirm():
    session.clear()  # Supprimer toutes les données de session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)