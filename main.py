import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image
import customtkinter as ctk

# --- IMPORT DE VOTRE MODULE GMAIL ---
try:
    from gmail_import import importer_contacts_gmail
except ImportError:
    # Fonction vide de secours si le fichier n'est pas là
    def importer_contacts_gmail():
        return []

# ------------------- CONFIGURATION & THEME -------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Chemins des fichiers
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(DOSSIER_SCRIPT, "contacts.txt")
DOSSIER_IMAGES = os.path.join(DOSSIER_SCRIPT, "avatars")

if not os.path.exists(DOSSIER_IMAGES):
    os.makedirs(DOSSIER_IMAGES)

class ContactApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration de la fenêtre ---
        self.title("Pocket Contact") # Nouveau nom de l'application
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Variables
        self.contacts = []
        self.current_image_path = None 
        self.categories_disponibles = ["Tout voir", "Ami", "Famille", "Travail", "VIP", "Gmail", "Autre"] # Liste pour le filtre

        # Layout : Grille 1x2
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. SIDEBAR (Gauche) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="POCKET CONTACT", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Boutons Menu
        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="Liste Contacts", command=self.show_home_frame)
        self.btn_home.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_add = ctk.CTkButton(self.sidebar_frame, text="Nouveau Contact", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.show_add_frame)
        self.btn_add.grid(row=2, column=0, padx=20, pady=10)

        # Bouton Gmail
        self.btn_gmail = ctk.CTkButton(self.sidebar_frame, text="Connecter Gmail", fg_color="#DB4437", hover_color="#C53929", command=self.action_import_gmail)
        self.btn_gmail.grid(row=3, column=0, padx=20, pady=(20, 10))

        # Settings en bas
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Thème:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

        # --- 2. ZONE PRINCIPALE (Droite) ---
        
        # FRAME : LISTE DES CONTACTS
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(2, weight=1)
        
        # Header avec Titre + Recherche/Filtre
        self.header_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        self.lbl_title_home = ctk.CTkLabel(self.header_frame, text="Mes Contacts", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title_home.pack(side="left")

        # CONTENEUR DROIT (Filtre Catégorie + Recherche)
        self.right_header_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.right_header_container.pack(side="right")
        
        # --- FILTRE PAR CATÉGORIE ---
        self.combo_filter_cat = ctk.CTkOptionMenu(self.right_header_container, 
                                                  values=self.categories_disponibles, 
                                                  command=self.filter_contacts)
        self.combo_filter_cat.set("Tout voir")
        self.combo_filter_cat.pack(side="left", padx=(0, 20))


        # BARRE DE RECHERCHE + ICONE LOUPE
        self.search_container = ctk.CTkFrame(self.right_header_container, fg_color="transparent")
        self.search_container.pack(side="right")

        self.icon_search = ctk.CTkLabel(self.search_container, text="🔍", font=("Arial", 18))
        self.icon_search.pack(side="left", padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_container, width=300, placeholder_text="Rechercher (Nom, Mail, Tel)...", textvariable=self.search_var)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.filter_contacts)

        # Zone de défilement
        self.scrollable_frame = ctk.CTkScrollableFrame(self.home_frame, label_text="Répertoire")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # FRAME : AJOUTER CONTACT
        self.add_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.add_frame.grid_columnconfigure(0, weight=1)

        self.lbl_title_add = ctk.CTkLabel(self.add_frame, text="Créer un nouveau contact", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title_add.pack(pady=20, padx=20, anchor="w")

        self.form_container = ctk.CTkFrame(self.add_frame, corner_radius=15)
        self.form_container.pack(pady=20, padx=60, fill="both", expand=True)
        self.create_form()

        # Chargement initial
        self.charger_contacts()
        self.show_home_frame()

    # --- GESTION DE L'INTERFACE ---
    def show_home_frame(self):
        self.add_frame.grid_forget()
        self.home_frame.grid(row=0, column=1, sticky="nsew")
        self.refresh_contact_list()

    def show_add_frame(self):
        self.home_frame.grid_forget()
        self.add_frame.grid(row=0, column=1, sticky="nsew")
        self.reset_form()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def reset_form(self):
        self.entry_nom.delete(0, "end")
        self.entry_tel.delete(0, "end")
        self.entry_mail.delete(0, "end")
        self.current_image_path = None
        self.lbl_img_preview.configure(text="Aucune image sélectionnée")

    # --- CONSTRUCTION DU FORMULAIRE D'AJOUT ---
    def create_form(self):
        self.form_container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.form_container, text="Nom Complet :").grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.entry_nom = ctk.CTkEntry(self.form_container, placeholder_text="Ex: Jean Dupont", height=40)
        self.entry_nom.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.form_container, text="Téléphone :").grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_tel = ctk.CTkEntry(self.form_container, placeholder_text="Ex: 06 12 34 56 78", height=40)
        self.entry_tel.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.form_container, text="Email :").grid(row=2, column=1, padx=20, pady=(10, 5), sticky="w")
        self.entry_mail = ctk.CTkEntry(self.form_container, placeholder_text="Ex: jean@mail.com", height=40)
        self.entry_mail.grid(row=3, column=1, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.form_container, text="Catégorie :").grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")
        self.combo_cat = ctk.CTkOptionMenu(self.form_container, values=[c for c in self.categories_disponibles if c != "Tout voir"])
        self.combo_cat.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.form_container, text="Photo de profil :").grid(row=4, column=1, padx=20, pady=(10, 5), sticky="w")
        self.btn_photo = ctk.CTkButton(self.form_container, text="Choisir une photo", command=self.choisir_photo, fg_color="gray")
        self.btn_photo.grid(row=5, column=1, padx=20, pady=5, sticky="ew")
        
        self.lbl_img_preview = ctk.CTkLabel(self.form_container, text="Aucune image", font=("Arial", 10))
        self.lbl_img_preview.grid(row=6, column=1, padx=20, sticky="w")

        self.btn_save = ctk.CTkButton(self.form_container, text="Enregistrer le Contact", height=50, font=ctk.CTkFont(size=15, weight="bold"), command=self.ajouter_contact)
        self.btn_save.grid(row=7, column=0, columnspan=2, padx=20, pady=40, sticky="ew")

    # --- LOGIQUE MODIFICATION (EDIT) ---
    def open_edit_modal(self, contact):
        """Ouvre une fenêtre pop-up pour modifier le contact"""
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Modifier Contact")
        edit_window.geometry("400x550")
        edit_window.grab_set()
        
        # Variables locales pour cette fenêtre
        self.edit_img_path = contact['img']

        # UI Modification
        ctk.CTkLabel(edit_window, text=f"Modifier {contact['nom']}", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(edit_window, text="Nom :").pack(anchor="w", padx=20)
        entry_edit_nom = ctk.CTkEntry(edit_window)
        entry_edit_nom.insert(0, contact['nom'])
        entry_edit_nom.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(edit_window, text="Téléphone :").pack(anchor="w", padx=20)
        entry_edit_tel = ctk.CTkEntry(edit_window)
        entry_edit_tel.insert(0, contact['tel'])
        entry_edit_tel.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(edit_window, text="Email :").pack(anchor="w", padx=20)
        entry_edit_mail = ctk.CTkEntry(edit_window)
        entry_edit_mail.insert(0, contact['mail'])
        entry_edit_mail.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(edit_window, text="Catégorie :").pack(anchor="w", padx=20, pady=(10,0))
        cat_menu = ctk.CTkOptionMenu(edit_window, values=[c for c in self.categories_disponibles if c != "Tout voir"])
        cat_menu.set(contact['cat'])
        cat_menu.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(edit_window, text="Photo :").pack(anchor="w", padx=20, pady=(10,0))
        lbl_curr_img = ctk.CTkLabel(edit_window, text=os.path.basename(contact['img']) if contact['img'] != "None" else "Aucune", text_color="gray")
        lbl_curr_img.pack(anchor="w", padx=20)

        def changer_photo_edit():
            filename = filedialog.askopenfilename(title="Nouvelle image", filetypes=[("Images", "*.png *.jpg *.jpeg")])
            if filename:
                try:
                    ext = os.path.splitext(filename)[1]
                    new_filename = f"{contact['nom'].replace(' ', '_')}_EDIT_{ext}"
                    destination = os.path.join(DOSSIER_IMAGES, new_filename)
                    shutil.copy(filename, destination)
                    self.edit_img_path = destination
                    lbl_curr_img.configure(text=os.path.basename(destination))
                except Exception as e:
                    print(f"Erreur changement photo: {e}")

        btn_change_img = ctk.CTkButton(edit_window, text="Changer Photo", command=changer_photo_edit, fg_color="gray")
        btn_change_img.pack(fill="x", padx=20, pady=5)

        def sauver_modifs():
            contact['nom'] = entry_edit_nom.get()
            contact['tel'] = entry_edit_tel.get()
            contact['mail'] = entry_edit_mail.get()
            contact['cat'] = cat_menu.get()
            contact['img'] = self.edit_img_path
            
            self.sauvegarder_contacts_fichier()
            self.refresh_contact_list()
            edit_window.destroy()
            messagebox.showinfo("Succès", "Contact modifié !")

        ctk.CTkButton(edit_window, text="Enregistrer Modifications", command=sauver_modifs).pack(pady=20, padx=20, fill="x")

    # --- FONCTIONS METIER ---

    def charger_contacts(self):
        self.contacts = []
        try:
            with open(FILENAME, "r", encoding="utf-8") as f:
                for ligne in f:
                    ligne = ligne.strip()
                    if ligne:
                        parts = ligne.split(";")
                        nom = parts[0] if len(parts) > 0 else "Inconnu"
                        tel = parts[1] if len(parts) > 1 else ""
                        mail = parts[2] if len(parts) > 2 else ""
                        cat = parts[3] if len(parts) > 3 else "Autre"
                        img = parts[4] if len(parts) > 4 else "None"
                        self.contacts.append({"nom": nom, "tel": tel, "mail": mail, "cat": cat, "img": img})
        except FileNotFoundError:
            pass

    def sauvegarder_contacts_fichier(self):
        with open(FILENAME, "w", encoding="utf-8") as f:
            for c in self.contacts:
                f.write(f"{c['nom']};{c['tel']};{c['mail']};{c['cat']};{c['img']}\n")

    def action_import_gmail(self):
        try:
            imported_list = importer_contacts_gmail() 
            if not imported_list:
                messagebox.showinfo("Info", "Aucun contact récupéré.")
                return

            count = 0
            for item in imported_list:
                nom = item[0]
                tel = item[1]
                mail = item[2]
                
                existe = any(c['nom'] == nom for c in self.contacts)
                if not existe:
                    new_c = {"nom": nom, "tel": tel, "mail": mail, "cat": "Gmail", "img": "None"}
                    self.contacts.append(new_c)
                    count += 1
            
            self.sauvegarder_contacts_fichier()
            self.refresh_contact_list()
            messagebox.showinfo("Succès", f"{count} contacts Gmail importés !")

        except Exception as e:
            messagebox.showerror("Erreur Import", f"Une erreur est survenue : {e}")

    def choisir_photo(self):
        filename = filedialog.askopenfilename(title="Choisir une image", filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if filename:
            self.current_image_path = filename
            self.lbl_img_preview.configure(text=os.path.basename(filename))

    def ajouter_contact(self):
        nom = self.entry_nom.get().strip()
        tel = self.entry_tel.get().strip()
        mail = self.entry_mail.get().strip()
        cat = self.combo_cat.get()

        if not nom:
            messagebox.showwarning("Attention", "Le nom est obligatoire.")
            return

        final_img_path = "None"
        if self.current_image_path:
            try:
                ext = os.path.splitext(self.current_image_path)[1]
                new_filename = f"{nom.replace(' ', '_')}_{len(self.contacts)}{ext}"
                destination = os.path.join(DOSSIER_IMAGES, new_filename)
                shutil.copy(self.current_image_path, destination)
                final_img_path = destination
            except Exception as e:
                print(f"Erreur copie image: {e}")

        new_contact = {"nom": nom, "tel": tel, "mail": mail, "cat": cat, "img": final_img_path}
        self.contacts.append(new_contact)
        self.sauvegarder_contacts_fichier()
        messagebox.showinfo("Succès", "Contact ajouté !")
        self.show_home_frame()

    def supprimer_contact(self, contact_dict):
        if messagebox.askyesno("Confirmer", f"Supprimer {contact_dict['nom']} ?"):
            if contact_dict in self.contacts:
                self.contacts.remove(contact_dict)
                self.sauvegarder_contacts_fichier()
                self.filter_contacts() 

    def filter_contacts(self, event=None):
        """Filtre les contacts selon le texte de la barre de recherche ET la catégorie sélectionnée."""
        query = self.search_var.get().lower()
        selected_cat = self.combo_filter_cat.get()
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 1. Filtrage par recherche (Nom, Mail, Tel)
        matching_contacts = [c for c in self.contacts 
                             if query in c['nom'].lower() 
                             or query in c['mail'].lower()
                             or query in c['tel'].lower()]

        # 2. Filtrage par Catégorie
        if selected_cat != "Tout voir":
            final_contacts = [c for c in matching_contacts if c['cat'] == selected_cat]
        else:
            final_contacts = matching_contacts

        for c in final_contacts:
            self.create_contact_card(c)

    def refresh_contact_list(self):
        """Affiche TOUS les contacts (vide la recherche et remet le filtre à Tout voir)"""
        self.search_var.set("") 
        self.combo_filter_cat.set("Tout voir")
        self.filter_contacts() # Appelle le filtre avec les valeurs réinitialisées

    def create_contact_card(self, c):
        # Cadre principal de la carte
        card = ctk.CTkFrame(self.scrollable_frame, corner_radius=10, fg_color=("white", "gray20"))
        card.pack(fill="x", pady=5)

        # Binding pour le click (Edition) sur le cadre et ses enfants
        card.bind("<Button-1>", lambda e, x=c: self.open_edit_modal(x))
        card.configure(cursor="hand2")

        # Image
        try:
            if c['img'] and c['img'] != "None" and os.path.exists(c['img']):
                my_image = ctk.CTkImage(light_image=Image.open(c['img']), 
                                      dark_image=Image.open(c['img']), 
                                      size=(45, 45))
                img_label = ctk.CTkLabel(card, image=my_image, text="")
            else:
                img_label = ctk.CTkLabel(card, text=c['nom'][:2].upper(), width=45, height=45, fg_color="gray", corner_radius=20)
        except:
             img_label = ctk.CTkLabel(card, text="?", width=45, height=45, fg_color="gray", corner_radius=20)

        img_label.grid(row=0, column=0, rowspan=2, padx=15, pady=10)
        img_label.bind("<Button-1>", lambda e, x=c: self.open_edit_modal(x))

        # Infos
        info_container = ctk.CTkFrame(card, fg_color="transparent")
        info_container.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(10,0))
        
        lbl_nom = ctk.CTkLabel(info_container, text=c['nom'], font=ctk.CTkFont(size=16, weight="bold"))
        lbl_nom.pack(side="left")
        lbl_nom.bind("<Button-1>", lambda e, x=c: self.open_edit_modal(x))

        # Badge Catégorie
        cat_color = "gray"
        if c['cat'] == "Ami": cat_color = "#3B8ED0"
        elif c['cat'] == "Travail": cat_color = "#E04F5F"
        elif c['cat'] == "VIP": cat_color = "#E5B700"
        elif c['cat'] == "Gmail": cat_color = "#555"
        
        lbl_cat = ctk.CTkLabel(info_container, text=f" {c['cat']} ", text_color=cat_color, font=ctk.CTkFont(size=12, weight="bold"))
        lbl_cat.pack(side="left", padx=10)
        lbl_cat.bind("<Button-1>", lambda e, x=c: self.open_edit_modal(x))

        # Ligne 2 : Tel | Mail
        infos_text = f"📞 {c['tel']}  |  ✉ {c['mail']}"
        lbl_infos = ctk.CTkLabel(card, text=infos_text, text_color="gray50", font=ctk.CTkFont(size=12))
        lbl_infos.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0,10))
        lbl_infos.bind("<Button-1>", lambda e, x=c: self.open_edit_modal(x))

        # Actions (Bouton Supprimer)
        card.grid_columnconfigure(2, weight=1)
        btn_del = ctk.CTkButton(card, text="✕", width=30, height=30, fg_color="transparent", text_color="red", hover_color="gray85",
                                command=lambda x=c: self.supprimer_contact(x))
        btn_del.grid(row=0, column=3, rowspan=2, padx=15)

if __name__ == "__main__":
    app = ContactApp()
    app.mainloop()