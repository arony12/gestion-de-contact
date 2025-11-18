import os
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
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
    messagebox.showinfo("✅ Sauvegarde", "Contacts enregistrés avec succès !")


def ajouter_contact():
    nom = entry_nom.get().strip()
    tel = entry_tel.get().strip()
    mail = entry_mail.get().strip() or "Non renseigné"

    if not nom or not tel:
        messagebox.showerror("❌ Erreur", "Nom et téléphone obligatoires")
        return

    contacts.append([nom, tel, mail])
    afficher_tous_contacts()
    sauvegarder_contacts()
    entry_nom.delete(0, tk.END)
    entry_tel.delete(0, tk.END)
    entry_mail.delete(0, tk.END)


def supprimer_contact(nom, tel, mail):
    if messagebox.askyesno("🗑️ Confirmation", f"Supprimer {nom} ?"):
        contacts[:] = [c for c in contacts if c != [nom, tel, mail]]
        afficher_tous_contacts()
        sauvegarder_contacts()


def rechercher_contact():
    terme = entry_search.get().strip().lower()
    
    # Effacer l'affichage actuel
    for widget in frame_cards.winfo_children():
        widget.destroy()
    
    # Filtrer et afficher
    resultats = [c for c in contacts if 
                 terme in c[0].lower() or terme in c[1].lower() or terme in c[2].lower()]
    
    if resultats:
        afficher_contacts_liste(resultats)
    else:
        label_vide = tb.Label(
            frame_cards, 
            text="Aucun résultat trouvé 🔍", 
            font=("Segoe UI", 14),
            bootstyle="secondary"
        )
        label_vide.pack(pady=50)


def afficher_tous_contacts():
    # Effacer l'affichage actuel
    for widget in frame_cards.winfo_children():
        widget.destroy()
    
    if not contacts:
        label_vide = tb.Label(
            frame_cards, 
            text="📭 Aucun contact\nCliquez sur '+ Ajouter' pour commencer", 
            font=("Segoe UI", 14),
            bootstyle="secondary",
            justify="center"
        )
        label_vide.pack(pady=80)
    else:
        afficher_contacts_liste(contacts)


def afficher_contacts_liste(liste_contacts):
    # Créer un canvas avec scrollbar pour les cartes
    canvas = tk.Canvas(frame_cards, bg="#f8f9fa", highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame_cards, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Afficher les contacts en cartes (3 par ligne)
    row, col = 0, 0
    couleurs = ["primary", "success", "info", "warning", "danger", "secondary"]
    
    for idx, (nom, tel, mail) in enumerate(liste_contacts):
        couleur = couleurs[idx % len(couleurs)]
        
        # Carte de contact
        card = tb.Frame(scrollable_frame, bootstyle=couleur, relief="raised")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Avatar avec initiales
        initiales = "".join([n[0].upper() for n in nom.split()[:2]])
        avatar = tb.Label(
            card, 
            text=initiales, 
            font=("Segoe UI", 20, "bold"),
            bootstyle=f"inverse-{couleur}",
            width=4,
            anchor="center"
        )
        avatar.pack(pady=(15, 10))
        
        # Nom
        label_nom = tb.Label(
            card, 
            text=nom, 
            font=("Segoe UI", 13, "bold"),
            bootstyle=couleur
        )
        label_nom.pack()
        
        # Téléphone
        label_tel = tb.Label(
            card, 
            text=f"📱 {tel}", 
            font=("Segoe UI", 10),
            bootstyle=couleur
        )
        label_tel.pack(pady=3)
        
        # Email
        label_mail = tb.Label(
            card, 
            text=f"📧 {mail}", 
            font=("Segoe UI", 10),
            bootstyle=couleur
        )
        label_mail.pack(pady=3)
        
        # Bouton supprimer
        btn_del = tb.Button(
            card,
            text="🗑️ Supprimer",
            bootstyle=f"outline-{couleur}",
            command=lambda n=nom, t=tel, m=mail: supprimer_contact(n, t, m),
            width=15
        )
        btn_del.pack(pady=(10, 15))
        
        # Configurer la grille (3 colonnes)
        scrollable_frame.columnconfigure(col, weight=1, minsize=250)
        col += 1
        if col > 2:  # 3 cartes par ligne
            col = 0
            row += 1
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def rafraichir():
    entry_search.delete(0, tk.END)
    afficher_tous_contacts()


def importer_gmail_ui():
    try:
        contacts_gmail = importer_contacts_gmail()
        if not contacts_gmail:
            messagebox.showinfo("📧 Gmail", "Aucun contact trouvé dans Gmail.")
            return

        added_count = 0
        for c in contacts_gmail:
            if c not in contacts:
                contacts.append(c)
                added_count += 1

        afficher_tous_contacts()
        sauvegarder_contacts()
        messagebox.showinfo("✅ Gmail", f"{added_count} contact(s) importé(s) !")
    except Exception as e:
        messagebox.showerror("❌ Erreur Gmail", f"Impossible d'importer.\n{e}")


def fermer_application():
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            print("[SECURITE] token.json supprimé")
    except Exception as e:
        print(f"[ERREUR] {e}")
    finally:
        app.destroy()


# ------------------- Interface graphique -------------------
app = tb.Window(themename="cosmo")  # Thèmes modernes: cosmo, flatly, litera, minty
app.title("📇 Contacteo - Gestionnaire de Contacts")
app.geometry("1200x800")
app.protocol("WM_DELETE_WINDOW", fermer_application)

contacts = charger_contacts()

# --- En-tête ---
frame_header = tb.Frame(app, bootstyle="dark")
frame_header.pack(fill="x", pady=(0, 10))

title = tb.Label(
    frame_header,
    text="📇 Contacteo",
    font=("Segoe UI", 24, "bold"),
    bootstyle="inverse-dark"
)
title.pack(side="left", padx=20, pady=15)

# Compteur de contacts
label_count = tb.Label(
    frame_header,
    text=f"{len(contacts)} contacts",
    font=("Segoe UI", 12),
    bootstyle="inverse-dark"
)
label_count.pack(side="left", padx=10)

# --- Barre de recherche ---
frame_search = tb.Frame(app)
frame_search.pack(fill="x", padx=20, pady=10)

entry_search = tb.Entry(
    frame_search, 
    font=("Segoe UI", 12),
    width=40
)
entry_search.pack(side="left", padx=5)

btn_search = tb.Button(
    frame_search,
    text="🔍 Rechercher",
    command=rechercher_contact,
    bootstyle="primary"
)
btn_search.pack(side="left", padx=5)

btn_refresh = tb.Button(
    frame_search,
    text="↻ Tout afficher",
    command=rafraichir,
    bootstyle="secondary"
)
btn_refresh.pack(side="left", padx=5)

# --- Zone des cartes de contacts ---
frame_cards = tb.Frame(app, bootstyle="light")
frame_cards.pack(fill="both", expand=True, padx=20, pady=10)

# --- Formulaire d'ajout (modal) ---
frame_form = tb.Labelframe(
    app,
    text="➕ Ajouter un nouveau contact",
    bootstyle="info",
    padding=15
)
frame_form.pack(fill="x", padx=20, pady=10)

# Disposition horizontale du formulaire
form_inner = tb.Frame(frame_form)
form_inner.pack()

tb.Label(form_inner, text="Nom:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, sticky="w")
entry_nom = tb.Entry(form_inner, width=20, font=("Segoe UI", 10))
entry_nom.grid(row=0, column=1, padx=5)

tb.Label(form_inner, text="Téléphone:", font=("Segoe UI", 10)).grid(row=0, column=2, padx=5, sticky="w")
entry_tel = tb.Entry(form_inner, width=20, font=("Segoe UI", 10))
entry_tel.grid(row=0, column=3, padx=5)

tb.Label(form_inner, text="Email:", font=("Segoe UI", 10)).grid(row=0, column=4, padx=5, sticky="w")
entry_mail = tb.Entry(form_inner, width=25, font=("Segoe UI", 10))
entry_mail.grid(row=0, column=5, padx=5)

btn_add = tb.Button(
    form_inner,
    text="➕ Ajouter",
    command=ajouter_contact,
    bootstyle="success",
    width=12
)
btn_add.grid(row=0, column=6, padx=10)

# --- Pied de page ---
frame_footer = tb.Frame(app, bootstyle="secondary")
frame_footer.pack(fill="x", pady=(10, 0))

btn_gmail = tb.Button(
    frame_footer,
    text="📧 Importer depuis Gmail",
    command=importer_gmail_ui,
    bootstyle="warning"
)
btn_gmail.pack(side="right", padx=10, pady=10)

btn_save = tb.Button(
    frame_footer,
    text="💾 Sauvegarder",
    command=sauvegarder_contacts,
    bootstyle="success"
)
btn_save.pack(side="right", padx=5, pady=10)

# Afficher les contacts au démarrage
afficher_tous_contacts()

# Lancer l'application
app.mainloop()