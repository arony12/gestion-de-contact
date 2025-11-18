import os
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from gmail_import import importer_contacts_gmail


# Fichier de sauvegarde
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(DOSSIER_SCRIPT, "contacts.txt")
TOKEN_FILE = os.path.join(DOSSIER_SCRIPT, "token.json")


# ------------------- Fonctions principales -------------------
def charger_contacts():
    contacts = []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()
                if ligne:
                    parts = ligne.split(";")
                    while len(parts) < 3:
                        parts.append("Non renseigné")
                    contacts.append(parts[:3])
    except FileNotFoundError:
        pass
    return contacts


def sauvegarder_contacts():
    with open(FILENAME, "w", encoding="utf-8") as f:
        for nom, tel, mail in contacts:
            f.write(f"{nom};{tel};{mail}\n")
    messagebox.showinfo("Sauvegarde", "Contacts enregistrés avec succès ✅")


def ajouter_contact():
    nom = entry_nom.get().strip()
    tel = entry_tel.get().strip()
    mail = entry_mail.get().strip() or "Non renseigné"

    if not nom or not tel:
        messagebox.showerror("Erreur", "Nom et téléphone sont obligatoires ⚠️")
        return

    contacts.append([nom, tel, mail])
    tree.insert("", "end", values=(nom, tel, mail))
    sauvegarder_contacts()
    entry_nom.delete(0, tk.END)
    entry_tel.delete(0, tk.END)
    entry_mail.delete(0, tk.END)


def supprimer_contact():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Suppression", "Aucun contact sélectionné ⚠️")
        return

    for item in selected:
        values = tree.item(item, "values")
        contacts[:] = [c for c in contacts if c != list(values)]
        tree.delete(item)

    sauvegarder_contacts()
    messagebox.showinfo("Suppression", "Contact supprimé avec succès 🗑️")


def rechercher_contact():
    terme = entry_search.get().strip().lower()
    for i in tree.get_children():
        tree.delete(i)

    for nom, tel, mail in contacts:
        if terme in nom.lower() or terme in tel.lower() or terme in mail.lower():
            tree.insert("", "end", values=(nom, tel, mail))


def rafraichir():
    entry_search.delete(0, tk.END)
    tree.delete(*tree.get_children())
    for c in contacts:
        tree.insert("", "end", values=c)


def importer_gmail_ui():
    try:
        contacts_gmail = importer_contacts_gmail()
        if not contacts_gmail:
            messagebox.showinfo("Importation Gmail", "Aucun contact trouvé dans Gmail.")
            return

        # Ajouter les contacts importés dans la liste locale et le Treeview
        added_count = 0
        for c in contacts_gmail:
            if c not in contacts:  # éviter les doublons
                contacts.append(c)
                tree.insert("", "end", values=c)
                added_count += 1

        sauvegarder_contacts()
        messagebox.showinfo("Importation Gmail", f"{added_count} contact(s) importé(s) depuis Gmail ✅")
    except Exception as e:
        messagebox.showerror("Erreur Gmail", f"Impossible d'importer les contacts.\n{e}")


# ------------------- Fonction de fermeture sécurisée -------------------
def fermer_application():
    """Supprime le token Gmail et ferme l'application"""
    try:
        # Supprimer le fichier token.json s'il existe
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            print("[SECURITE] token.json supprimé")
    except Exception as e:
        print(f"[ERREUR] Impossible de supprimer token.json : {e}")
    finally:
        # Fermer l'application
        app.destroy()


# ------------------- Interface graphique -------------------
app = tb.Window(themename="flatly")
app.title("Contacteo")
app.geometry("900x640")

# Intercepter la fermeture de la fenêtre
app.protocol("WM_DELETE_WINDOW", fermer_application)

contacts = charger_contacts()

# --- Barre de recherche ---
frame_top = ttk.Frame(app, padding=10)
frame_top.pack(fill="x")

entry_search = ttk.Entry(frame_top, width=40)
entry_search.pack(side="left", padx=5)
ttk.Button(frame_top, text="🔍 Rechercher", command=rechercher_contact).pack(side="left", padx=5)
ttk.Button(frame_top, text="↻ Rafraîchir", command=rafraichir).pack(side="left")

# --- Tableau des contacts ---
frame_table = ttk.Frame(app, padding=10)
frame_table.pack(fill="both", expand=True)

columns = ("Nom", "Téléphone", "Email")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200)
tree.pack(fill="both", expand=True, pady=10)

# Remplir le tableau
for c in contacts:
    tree.insert("", "end", values=c)

# --- Formulaire d'ajout ---
frame_form = ttk.Frame(app, padding=10)
frame_form.pack(fill="x")

ttk.Label(frame_form, text="Nom :").grid(row=0, column=0, sticky="e", padx=5, pady=5)
ttk.Label(frame_form, text="Téléphone :").grid(row=0, column=2, sticky="e", padx=5, pady=5)
ttk.Label(frame_form, text="Email :").grid(row=1, column=0, sticky="e", padx=5, pady=5)

entry_nom = ttk.Entry(frame_form, width=25)
entry_tel = ttk.Entry(frame_form, width=25)
entry_mail = ttk.Entry(frame_form, width=25)

entry_nom.grid(row=0, column=1, padx=5, pady=5)
entry_tel.grid(row=0, column=3, padx=5, pady=5)
entry_mail.grid(row=1, column=1, padx=5, pady=5)

ttk.Button(frame_form, text="➕ Ajouter", command=ajouter_contact).grid(row=2, column=3, padx=5)
ttk.Button(frame_form, text="🗑️ Supprimer", command=supprimer_contact).grid(row=2, column=4, padx=8)

# --- Pied de page ---
frame_bottom = ttk.Frame(app, padding=10)
frame_bottom.pack(fill="x")
ttk.Button(frame_bottom, text="💾 Sauvegarder", command=sauvegarder_contacts).pack(side="right")
ttk.Button(frame_bottom, text="📧 Connecter Gmail", command=importer_gmail_ui).pack(side="right", padx=5)

# Lancer l'application
app.mainloop()