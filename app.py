import os
import pandas as pd
import sqlite3
from flask import Flask
import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
from sqlalchemy import create_engine, text

# ------------------- CONFIGURATION -------------------
DB_PATH = "database.db"  # Fichier SQLite
CSV_PATH = "data.csv"  # Nom du fichier CSV à charger

# ------------------- BASE DE DONNÉES -------------------
def create_database():
    """Crée la base de données et la table si elles n'existent pas."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS salaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                genre TEXT,
                salaire REAL
            )
        """))
    return engine

def import_csv_to_db(engine, csv_path):
    """Importe les données du CSV dans la base."""
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, sep=";")
        df.to_sql("salaires", con=engine, if_exists="append", index=False)
        print("Importation réussie !")

# ------------------- FLASK + DASH -------------------
server = Flask(__name__)  # Serveur Flask
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/")

app.layout = html.Div([
    html.H1("Analyse des Salaires par Genre"),
    dcc.Graph(id="bar-chart"),
    dcc.Interval(id="interval", interval=5000, n_intervals=0)  # Mise à jour auto toutes les 5 sec
])

@app.callback(Output("bar-chart", "figure"), [Input("interval", "n_intervals")])
def update_graph(n):
    """Met à jour le graphique en interrogeant la base."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql("SELECT genre, AVG(salaire) AS salaire_moyen FROM salaires GROUP BY genre", engine)
    fig = px.bar(df, x="genre", y="salaire_moyen", title="Salaire Moyen par Genre", color="genre")
    return fig

# ------------------- LANCEMENT -------------------
if __name__ == "__main__":
    engine = create_database()
    import_csv_to_db(engine, CSV_PATH)  # Charger le CSV une fois
    app.run(host="0.0.0.0", port=8050, debug=True)  # Serveur accessible via IP du NAS
