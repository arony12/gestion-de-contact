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

# Catégories disponibles
CATEGORIES = ["Tous", "👨‍👩‍👧 Famille", "👥 Amis", "💼 Collaborateurs", "🏪 Magasins", "📋 Autres"]
CATEGORIES_COULEURS = {
    "👨‍👩‍👧 Famille": "danger",
    "👥 Amis": "success",
    "💼 Collaborateurs": "primary",
    "🏪 Magasins": "warning",
    "📋 Autres": "secondary"
}


# ------------------- Fonctions principales -------------------
def charger_contacts():
    contacts = []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()
                if ligne:
                    parts = ligne.split(";")
                    while len(parts) < 4:  # Maintenant 4 champs : nom, tel, mail, catégorie
                        parts.append("📋 Autres" if len(parts) == 3 else "Non renseigné")
                    contacts.append(parts[:4])
    except FileNotFoundError:
        pass
    return contacts


def sauvegarder_contacts():
    with open(FILENAME, "w", encoding="utf-8") as f:
        for nom, tel, mail, cat in contacts:
            f.write(f"{nom};{tel};{mail};{cat}\n")
    messagebox.showinfo("✅ Sauvegarde", "Contacts enregistrés avec succès !")
    mettre_a_jour_compteur()


def ajouter_contact():
    nom = entry_nom.get().strip()
    tel = entry_tel.get().strip()
    mail = entry_mail.get().strip() or "Non renseigné"
    cat = combo_categorie.get()

    if not nom or not tel:
        messagebox.showerror("❌ Erreur", "Nom et téléphone obligatoires")
        return

    contacts.append([nom, tel, mail, cat])
    afficher_contacts_par_categorie()
    sauvegarder_contacts()
    entry_nom.delete(0, tk.END)
    entry_tel.delete(0, tk.END)
    entry_mail.delete(0, tk.END)
    combo_categorie.set("📋 Autres")


def supprimer_contact(nom, tel, mail, cat):
    if messagebox.askyesno("🗑️ Confirmation", f"Supprimer {nom} ?"):
        contacts[:] = [c for c in contacts if c != [nom, tel, mail, cat]]
        afficher_contacts_par_categorie()
        sauvegarder_contacts()


def rechercher_contact():
    terme = entry_search.get().strip().lower()
    
    for widget in frame_cards.winfo_children():
        widget.destroy()
    
    resultats = [c for c in contacts if 
                 terme in c[0].lower() or terme in c[1].lower() or terme in c[2].lower()]
    
    if resultats:
        afficher_contacts_liste(resultats)
    else:
        label_vide = tb.Label(
            frame_cards, 
            text="🔍 Aucun résultat trouvé", 
            font=("Segoe UI", 16),
            bootstyle="secondary"
        )
        label_vide.pack(pady=100)


def filtrer_par_categorie(event=None):
    cat_selectionnee = var_categorie.get()
    
    for widget in frame_cards.winfo_children():
        widget.destroy()
    
    if cat_selectionnee == "Tous":
        contacts_filtres = contacts
    else:
        contacts_filtres = [c for c in contacts if c[3] == cat_selectionnee]
    
    if contacts_filtres:
        afficher_contacts_liste(contacts_filtres)
    else:
        label_vide = tb.Label(
            frame_cards, 
            text=f"📭 Aucun contact dans '{cat_selectionnee}'", 
            font=("Segoe UI", 16),
            bootstyle="secondary"
        )
        label_vide.pack(pady=100)


def afficher_contacts_par_categorie():
    filtrer_par_categorie()


def mettre_a_jour_compteur():
    label_count.config(text=f"{len(contacts)} contacts")


def afficher_contacts_liste(liste_contacts):
    # Canvas avec scrollbar
    canvas = tk.Canvas(frame_cards, bg="#f8f9fa", highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame_cards, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Container principal avec padding
    main_container = tb.Frame(scrollable_frame)
    main_container.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Afficher les contacts en cartes (3 par ligne)
    row, col = 0, 0
    
    for idx, (nom, tel, mail, cat) in enumerate(liste_contacts):
        # Couleur selon la catégorie
        couleur = CATEGORIES_COULEURS.get(cat, "info")
        
        # Frame externe pour les bordures arrondies
        card_container = tb.Frame(main_container, bootstyle="light")
        card_container.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Carte de contact avec style personnalisé
        card = tb.Frame(card_container, bootstyle=couleur, relief="flat", borderwidth=0)
        card.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Badge catégorie en haut
        badge_cat = tb.Label(
            card,
            text=cat,
            font=("Segoe UI", 9),
            bootstyle=f"inverse-{couleur}",
            padding=(8, 3)
        )
        badge_cat.pack(pady=(10, 5))
        
        # Avatar avec initiales
        initiales = "".join([n[0].upper() for n in nom.split()[:2]])
        avatar = tb.Label(
            card, 
            text=initiales, 
            font=("Segoe UI", 22, "bold"),
            bootstyle=f"inverse-{couleur}",
            width=4,
            padding=10
        )
        avatar.pack(pady=(5, 10))
        
        # Nom
        label_nom = tb.Label(
            card, 
            text=nom, 
            font=("Segoe UI", 14, "bold"),
            bootstyle=couleur,
            wraplength=220
        )
        label_nom.pack(padx=10)
        
        # Séparateur
        sep = ttk.Separator(card, orient="horizontal")
        sep.pack(fill="x", padx=20, pady=10)
        
        # Téléphone
        frame_tel = tb.Frame(card, bootstyle=couleur)
        frame_tel.pack(fill="x", padx=15, pady=3)
        
        icon_tel = tb.Label(frame_tel, text="📱", font=("Segoe UI", 11), bootstyle=couleur)
        icon_tel.pack(side="left", padx=(0, 5))
        
        label_tel = tb.Label(
            frame_tel, 
            text=tel, 
            font=("Segoe UI", 10),
            bootstyle=couleur
        )
        label_tel.pack(side="left")
        
        # Email
        frame_mail = tb.Frame(card, bootstyle=couleur)
        frame_mail.pack(fill="x", padx=15, pady=3)
        
        icon_mail = tb.Label(frame_mail, text="📧", font=("Segoe UI", 11), bootstyle=couleur)
        icon_mail.pack(side="left", padx=(0, 5))
        
        label_mail = tb.Label(
            frame_mail, 
            text=mail[:25] + "..." if len(mail) > 25 else mail, 
            font=("Segoe UI", 10),
            bootstyle=couleur
        )
        label_mail.pack(side="left")
        
        # Bouton supprimer
        btn_del = tb.Button(
            card,
            text="🗑️ Supprimer",
            bootstyle=f"outline-{couleur}",
            command=lambda n=nom, t=tel, m=mail, c=cat: supprimer_contact(n, t, m, c),
            width=18
        )
        btn_del.pack(pady=15)
        
        # Configurer la grille
        main_container.columnconfigure(col, weight=1, minsize=280)
        col += 1
        if col > 2:
            col = 0
            row += 1
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def rafraichir():
    entry_search.delete(0, tk.END)
    var_categorie.set("Tous")
    afficher_contacts_par_categorie()


def importer_gmail_ui():
    try:
        contacts_gmail = importer_contacts_gmail()
        if not contacts_gmail:
            messagebox.showinfo("📧 Gmail", "Aucun contact trouvé dans Gmail.")
            return

        added_count = 0
        for c in contacts_gmail:
            # Ajouter une catégorie par défaut pour les imports Gmail
            c_with_cat = c + ["📋 Autres"]
            if c_with_cat not in contacts:
                contacts.append(c_with_cat)
                added_count += 1

        afficher_contacts_par_categorie()
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
app = tb.Window(themename="cosmo")
app.title("📇 Contacteo - Gestionnaire de Contacts")
app.geometry("1300x850")
app.protocol("WM_DELETE_WINDOW", fermer_application)

contacts = charger_contacts()

# --- En-tête ---
frame_header = tb.Frame(app, bootstyle="dark")
frame_header.pack(fill="x", pady=(0, 0))

title = tb.Label(
    frame_header,
    text="📇 Contacteo",
    font=("Segoe UI", 26, "bold"),
    bootstyle="inverse-dark"
)
title.pack(side="left", padx=20, pady=18)

label_count = tb.Label(
    frame_header,
    text=f"{len(contacts)} contacts",
    font=("Segoe UI", 13),
    bootstyle="inverse-dark"
)
label_count.pack(side="left", padx=10)

# --- Barre de recherche et filtres ---
frame_search = tb.Frame(app, padding=15)
frame_search.pack(fill="x", padx=20, pady=15)

# Recherche
entry_search = tb.Entry(
    frame_search, 
    font=("Segoe UI", 12),
    width=35
)
entry_search.pack(side="left", padx=5)

btn_search = tb.Button(
    frame_search,
    text="🔍 Rechercher",
    command=rechercher_contact,
    bootstyle="primary",
    width=15
)
btn_search.pack(side="left", padx=5)

btn_refresh = tb.Button(
    frame_search,
    text="↻ Réinitialiser",
    command=rafraichir,
    bootstyle="secondary",
    width=15
)
btn_refresh.pack(side="left", padx=5)

# Séparateur vertical
sep_vertical = ttk.Separator(frame_search, orient="vertical")
sep_vertical.pack(side="left", fill="y", padx=15)

# Filtre par catégorie
tb.Label(frame_search, text="Catégorie:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(10, 5))

var_categorie = tk.StringVar(value="Tous")
for cat in CATEGORIES:
    rb = tb.Radiobutton(
        frame_search,
        text=cat,
        variable=var_categorie,
        value=cat,
        bootstyle="toolbutton",
        command=filtrer_par_categorie
    )
    rb.pack(side="left", padx=2)

# --- Zone des cartes de contacts ---
frame_cards = tb.Frame(app, bootstyle="light")
frame_cards.pack(fill="both", expand=True, padx=0, pady=0)

# --- Formulaire d'ajout ---
frame_form = tb.Labelframe(
    app,
    text="➕ Ajouter un nouveau contact",
    bootstyle="info",
    padding=18
)
frame_form.pack(fill="x", padx=20, pady=15)

form_inner = tb.Frame(frame_form)
form_inner.pack()

tb.Label(form_inner, text="Nom:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=8, sticky="w")
entry_nom = tb.Entry(form_inner, width=22, font=("Segoe UI", 10))
entry_nom.grid(row=0, column=1, padx=8)

tb.Label(form_inner, text="Téléphone:", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=8, sticky="w")
entry_tel = tb.Entry(form_inner, width=22, font=("Segoe UI", 10))
entry_tel.grid(row=0, column=3, padx=8)

tb.Label(form_inner, text="Email:", font=("Segoe UI", 10, "bold")).grid(row=0, column=4, padx=8, sticky="w")
entry_mail = tb.Entry(form_inner, width=28, font=("Segoe UI", 10))
entry_mail.grid(row=0, column=5, padx=8)

tb.Label(form_inner, text="Catégorie:", font=("Segoe UI", 10, "bold")).grid(row=0, column=6, padx=8, sticky="w")
combo_categorie = tb.Combobox(
    form_inner,
    values=[c for c in CATEGORIES if c != "Tous"],
    state="readonly",
    width=18,
    font=("Segoe UI", 10)
)
combo_categorie.set("📋 Autres")
combo_categorie.grid(row=0, column=7, padx=8)

btn_add = tb.Button(
    form_inner,
    text="➕ Ajouter",
    command=ajouter_contact,
    bootstyle="success",
    width=13
)
btn_add.grid(row=0, column=8, padx=12)

# --- Pied de page ---
frame_footer = tb.Frame(app, bootstyle="secondary")
frame_footer.pack(fill="x", pady=(0, 0))

btn_gmail = tb.Button(
    frame_footer,
    text="📧 Importer depuis Gmail",
    command=importer_gmail_ui,
    bootstyle="warning",
    width=25
)
btn_gmail.pack(side="right", padx=10, pady=12)

btn_save = tb.Button(
    frame_footer,
    text="💾 Sauvegarder",
    command=sauvegarder_contacts,
    bootstyle="success",
    width=20
)
btn_save.pack(side="right", padx=5, pady=12)

# Afficher les contacts au démarrage
afficher_contacts_par_categorie()

app.mainloop()