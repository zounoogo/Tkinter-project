import csv
import sqlite3
from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

# Connexion et structuration de la base de données SQLite
conn = sqlite3.connect('gestion_notes.db')
cursor = conn.cursor()

# Création des tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_naissance TEXT,
    sexe TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS matieres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    niveau INTEGER,
    filiere TEXT NOT NULL
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER,
    matiere_id INTEGER,
    controle REAL,
    examen REAL,
    tp REAL,
    FOREIGN KEY(etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY(matiere_id) REFERENCES matieres(id)
)
""")
conn.commit()

# Interfaces graphiques Tkinter
class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Notes des Étudiants")
        self.root.geometry("1000x800")

        # Charger l'image d'arrière-plan
        self.bg_image = Image.open("INPT.png")
        self.bg_image = self.bg_image.resize((1500, 800), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Interface principale
        self.create_main_interface()

    def create_main_interface(self):
        Label(self.root, text="LISTE DE TOUTES LES REQUÊTES", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)

        # Boutons principaux
        Button(self.root, text="Liste des étudiants d'un niveau d'une filière", command=self.show_students_by_level, width=40).pack(pady=5)
        Button(self.root, text="Liste des matières d'un niveau d'une filière", command=self.show_subjects_by_level, width=40).pack(pady=5)
        Button(self.root, text="Liste des notes des étudiants dans une matière", command=self.show_grades_by_subject, width=40).pack(pady=5)
        Button(self.root, text="Liste des notes d'un étudiant dans ses matières", command=self.show_student_grades, width=40).pack(pady=5)
        Button(self.root, text="Liste des moyennes des étudiants dans une matière", command=self.show_averages_by_subject, width=40).pack(pady=5)

        Button(self.root, text="Ajouter un étudiant", command=self.add_student_interface, width=40, bg="green", fg="white").pack(pady=5)
        Button(self.root, text="Ajouter une matière", command=self.add_subject_interface, width=40, bg="green", fg="white").pack(pady=5)
        Button(self.root, text="Ajouter une note", command=self.add_note_interface, width=40, bg="green",fg="white").pack(pady=5)

        Button(self.root, text="Quitter", command=self.root.quit, width=20, bg="red", fg="white").pack(pady=20)

    def create_table_interface(self, title, columns, fetch_function):
        self.clear_window()
        self.bg_image = Image.open("INPT.png")
        self.bg_image = self.bg_image.resize((1500, 800), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        Label(self.root, text=title, font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)

        # Création du tableau
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=10, fill=BOTH, expand=True)

        # Remplir les données
        fetch_function(self.tree)

        Button(self.root, text="Exporter les données en CSV", command=self.export_to_csv, width=30, bg="blue",
               fg="white").pack(pady=5)
        Button(self.root, text="Retour", command=self.create_main_interface, width=20, bg="gray", fg="white").pack(
            pady=10)

    def export_to_csv(self):
        if not hasattr(self, 'tree') or not self.tree.get_children():
            print("Aucun tableau à exporter ou le tableau est vide.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichier CSV", "*.csv")])
        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)

                    # Écrire les en-têtes de colonnes
                    headers = [self.tree.heading(col, "text") for col in self.tree['columns']]
                    writer.writerow(headers)

                    # Écrire les données des lignes
                    for row_id in self.tree.get_children():
                        row = self.tree.item(row_id, "values")
                        writer.writerow(row)

                print(f"Données exportées avec succès vers {file_path}.")
            except Exception as e:
                print(f"Erreur lors de l'exportation : {e}")

    def show_students_by_level(self):
        def fetch_students(tree):
            cursor.execute("""
            SELECT  m.niveau, m.filiere, e.matricule, e.nom, e.prenom, e.date_naissance, e.sexe
            FROM etudiants e, matieres m, notes n
           WHERE n.matiere_id=m.id and e.id = n.etudiant_id
           order by m.niveau, m.filiere, e.matricule
            """)
            data = cursor.fetchall()
            for row in data:
                tree.insert("", "end", values=row)

        columns = ["Niveau","Filiere","Matricule", "Nom", "Prénom", "Date Naissance", "Sexe"]
        self.create_table_interface("Liste des étudiants d'un niveau d'une filière", columns, fetch_students)

    def show_subjects_by_level(self):
        def fetch_subjects(tree):
            cursor.execute("""
            SELECT niveau, nom,filiere
            FROM matieres
            order by niveau, filiere
            """)
            data = cursor.fetchall()
            for row in data:
                tree.insert("", "end", values=row)

        columns = ["Niveau","Matière", "Filière"]
        self.create_table_interface("Liste des matières d'un niveau d'une filière", columns, fetch_subjects)

    def show_grades_by_subject(self):
        def fetch_grades(tree):
            cursor.execute("""
            SELECT m.nom, e.nom, e.prenom, n.controle, n.examen, n.tp
            FROM notes n
            JOIN etudiants e ON n.etudiant_id = e.id, matieres m
            WHERE n.matiere_id=m.id
            order by m.nom
            """)
            data = cursor.fetchall()
            for row in data:
                tree.insert("", "end", values=row)

        columns = ["Matiere","Nom", "Prénom", "Contrôle", "Examen", "TP"]
        self.create_table_interface("Liste des notes des étudiants dans une matière", columns, fetch_grades)

    def show_student_grades(self):
        def fetch_student_grades(tree):
            cursor.execute("""
            SELECT e.nom, e.prenom, m.nom, n.controle, n.examen, n.tp
            FROM notes n
            JOIN matieres m ON n.matiere_id = m.id, etudiants e
            WHERE n.matiere_id=m.id and e.id = n.etudiant_id
            order by m.nom
            """)
            data = cursor.fetchall()
            for row in data:
                tree.insert("", "end", values=row)

        columns = ["Nom", "Prenom", "Matière", "Contrôle", "Examen", "TP"]
        self.create_table_interface("Liste des notes d'un étudiant dans ses matières", columns, fetch_student_grades)

    def show_averages_by_subject(self):
        def fetch_averages(tree):
            cursor.execute("""
            SELECT e.nom, e.prenom, m.nom,((n.controle + n.examen + n.tp) / 3.0) as moyenne ,AVG((n.controle + n.examen + n.tp) / 3.0) as moyenne_des_etudiants
            FROM notes n
            JOIN matieres m ON n.matiere_id = m.id, etudiants e
            WHERE e.id = n.etudiant_id
            GROUP BY m.nom
            """)
            data = cursor.fetchall()
            for row in data:
                tree.insert("", "end", values=row)

        columns = ["Nom", "Prenom", "Matière", "Moyenne", "Moyenne des etudiants"]
        self.create_table_interface("Liste des moyennes des étudiants dans une matière", columns, fetch_averages)

    def add_note_interface(self):
        self.clear_window()

        Label(self.root, text="Ajouter une note", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)

        # Sélectionner un étudiant
        Label(self.root, text="Étudiant", font=("Arial", 12)).pack(pady=5)
        students = cursor.execute("SELECT id, nom || ' ' || prenom FROM etudiants").fetchall()
        student_var = StringVar()
        student_combobox = ttk.Combobox(self.root, textvariable=student_var, state="readonly")
        student_combobox['values'] = [f"{id_} - {name}" for id_, name in students]
        student_combobox.pack(pady=5)

        # Sélectionner une matière
        Label(self.root, text="Matière", font=("Arial", 12)).pack(pady=5)
        subjects = cursor.execute("SELECT id, nom FROM matieres").fetchall()
        subject_var = StringVar()
        subject_combobox = ttk.Combobox(self.root, textvariable=subject_var, state="readonly")
        subject_combobox['values'] = [f"{id_} - {name}" for id_, name in subjects]
        subject_combobox.pack(pady=5)

        # Champs de saisie pour les notes
        fields = ["Contrôle", "Examen", "TP"]
        entries = {}

        for field in fields:
            Label(self.root, text=field, font=("Arial", 12)).pack(pady=5)
            entry = Entry(self.root)
            entry.pack(pady=5)
            entries[field] = entry

        def save_note():
            try:
                student_id = int(student_var.get().split(" - ")[0])
                subject_id = int(subject_var.get().split(" - ")[0])
                data = {
                    "etudiant_id": student_id,
                    "matiere_id": subject_id,
                    "controle": float(entries["Contrôle"].get()),
                    "examen": float(entries["Examen"].get()),
                    "tp": float(entries["TP"].get())
                }
                cursor.execute("""
                    INSERT INTO notes (etudiant_id, matiere_id, controle, examen, tp)
                    VALUES (:etudiant_id, :matiere_id, :controle, :examen, :tp)
                """, data)
                conn.commit()
                self.create_main_interface()
            except Exception as e:
                print(f"Erreur lors de l'enregistrement : {e}")

        Button(self.root, text="Enregistrer", command=save_note, bg="green", fg="white", width=20).pack(pady=10)
        Button(self.root, text="Retour", command=self.create_main_interface, width=20, bg="gray", fg="white").pack(
            pady=10)

    def add_student_interface(self):
        self.clear_window()

        Label(self.root, text="Ajouter un étudiant", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)

        # Champs du formulaire avec les nouvelles colonnes
        fields = ["Matricule", "Nom", "Prénom", "Date_Naissance", "Sexe"]
        entries = {}

        for field in fields:
            Label(self.root, text=field, font=("Arial", 12)).pack(pady=5)
            entry = Entry(self.root)
            entry.pack(pady=5)
            entries[field] = entry

        def save_student():
            data = {field: entry.get() for field, entry in entries.items()}
            cursor.execute("""
            INSERT INTO etudiants (matricule, nom, prenom, date_naissance, sexe)
            VALUES (:Matricule, :Nom, :Prénom, :Date_Naissance, :Sexe)
            """, data)
            conn.commit()
            self.create_main_interface()

        Button(self.root, text="Enregistrer", command=save_student, bg="green", fg="white", width=20).pack(pady=10)
        Button(self.root, text="Retour", command=self.create_main_interface, width=20, bg="gray", fg="white").pack(
pady=10)

    def add_subject_interface(self):
        self.clear_window()

        Label(self.root, text="Ajouter une matière", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)

        fields = ["Nom", "Niveau", "filiere"]
        entries = {}

        for field in fields:
            Label(self.root, text=field, font=("Arial", 12)).pack(pady=5)
            entry = Entry(self.root)
            entry.pack(pady=5)
            entries[field] = entry

        def save_subject():
            data = {field: entry.get() for field, entry in entries.items()}
            cursor.execute("""
            INSERT INTO matieres (nom, niveau, filiere)
            VALUES (:Nom, :Niveau, :filiere)
            """, data)
            conn.commit()
            self.create_main_interface()

        Button(self.root, text="Enregistrer", command=save_subject, bg="green", fg="white", width=20).pack(pady=10)
        Button(self.root, text="Retour", command=self.create_main_interface, width=20, bg="gray", fg="white").pack(pady=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Exécution de l'application
if __name__ == "__main__":
    root = Tk()
    app = Application(root)
    root.mainloop()
