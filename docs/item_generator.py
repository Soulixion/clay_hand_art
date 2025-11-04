import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import csv

# --- CONFIGURATION ---
ITEMS_FILE = "items.txt"
ITEMS_FOLDER = "items"

# --- FONCTIONS DE LECTURE/ÉCRITURE ---
def load_items():
    items = []
    if os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                items.append(row)
    return items

def save_items(items):
    with open(ITEMS_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Name","Theme","Price","Image","Description"], delimiter=";")
        writer.writeheader()
        writer.writerows(items)

# --- GÉNÉRATION HTML ---
def generate_html(items):
    if not os.path.exists("baseItem.html"):
        messagebox.showerror("Erreur", "Le fichier baseItem.html est introuvable.")
        return

    # --- Génération du fichier texte ---
    txt_file = "items_generated.txt"
    with open(txt_file, "w", encoding="utf-8", newline="") as f:
        f.write("Name;Theme;Price;Image;Description\n")
        for item in items:
            name = item["Name"].strip()
            theme = item["Theme"].strip()
            price = item["Price"].strip().replace(".", ",")
            image = item["Image"].strip()
            description = item.get("Description","").strip().replace("\n"," ").replace("\r"," ")
            f.write(f"{name};{theme};{price};{image};{description}\n")

    # --- Suppression du dossier items pour éviter doublons ---
    if os.path.exists(ITEMS_FOLDER):
        shutil.rmtree(ITEMS_FOLDER)
    os.makedirs(ITEMS_FOLDER)

    # --- Lit le template HTML ---
    with open("baseItem.html", "r", encoding="utf-8") as f:
        base_html = f.read()

    for item in items:
        name = item["Name"].strip()
        theme = item["Theme"].strip()
        price = item["Price"].strip().replace(",", ".")
        folder = item["Image"].strip()
        description = item.get("Description","").strip()

        folder_path = Path(folder)
        all_images = sorted(
            [str(p).replace("\\","/") for p in folder_path.iterdir() if p.suffix.lower() in [".png",".jpg",".jpeg"]]
        ) if folder_path.exists() else []

        menu_image = next((img for img in all_images if "menu.jpg" in img.lower()), None)
        if not menu_image:
            menu_image = next((img for img in all_images if "menu.png" in img.lower()), None)
        if menu_image:
            all_images.remove(menu_image)
            all_images.insert(0, menu_image)
        else:
            menu_image = all_images[0] if all_images else folder

        carousel_html = ""
        if all_images:
            carousel_html = '<div class="carousel">\n'
            for i, img in enumerate(all_images):
                active_class = "active" if img == menu_image else ""
                carousel_html += f'  <div class="carousel-image {active_class}"><img src="../{img}" alt="{name} image {i+1}"></div>\n'
            carousel_html += """
  <button class="prev">&#10094;</button>
  <button class="next">&#10095;</button>
</div>
"""

        description_html = f"<p class='product-description'>{description}</p>" if description else ""
        price_formatted = f"{float(price):.2f}"

        html = base_html
        html = html.replace("{name}", name)
        html = html.replace("{theme}", theme)
        html = html.replace("{price}", price)
        html = html.replace("{price_formatted}", price_formatted)
        html = html.replace("{description_html}", description_html)
        html = html.replace("{carousel_html}", carousel_html)
        html = html.replace("{menu_image}", menu_image)

        safe_name = name.replace(" ", "-")
        output_path = os.path.join(ITEMS_FOLDER, f"{safe_name}.html")

        with open(output_path, "w", encoding="utf-8") as out:
            out.write(html)

        print(f"✅ Généré : {output_path}")

    messagebox.showinfo("Succès", f"Tous les fichiers HTML et le fichier texte '{txt_file}' ont été générés !")

# --- INTERFACE Tkinter ---
class AutocompleteCombobox(ttk.Combobox):
    """ Combobox avec autocomplétion """
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self._handle_keyrelease)

    def _handle_keyrelease(self, event):
        typed = self.get().lower()
        if typed == '':
            data = self._completion_list
        else:
            data = [item for item in self._completion_list if typed in item.lower()]
        self['values'] = data

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des items - Clay_Hand_Art")
        self.root.geometry("950x550")
        self.items = load_items()
        self.current_index = None

        # Frames
        self.frame_menu = tk.Frame(root)
        self.frame_add = tk.Frame(root)
        self.frame_modify = tk.Frame(root)

        self.frame_menu.pack(fill="both", expand=True)
        self.create_menu()
        self.create_add_frame()
        self.create_modify_frame()

    def create_menu(self):
        tk.Label(self.frame_menu, text="Menu Principal", font=("Arial", 20)).pack(pady=40)
        tk.Button(self.frame_menu, text="Ajouter Item", width=30, height=2, command=self.show_add).pack(pady=10)
        tk.Button(self.frame_menu, text="Modifier/Supprimer Item", width=30, height=2, command=self.show_modify).pack(pady=10)
        tk.Button(self.frame_menu, text="Générer HTML", width=30, height=2, bg="#4CAF50", fg="white",
                  command=lambda: generate_html(self.items)).pack(pady=10)

    def create_add_frame(self):
        labels = ["Name","Theme","Price","Image","Description"]
        self.add_entries = {}
        tk.Label(self.frame_add, text="Ajouter Item", font=("Arial", 18)).grid(row=0,column=0,columnspan=3,pady=20)

        for i,label in enumerate(labels):
            tk.Label(self.frame_add,text=label+":", anchor="e").grid(row=i+1,column=0,sticky="e", padx=5, pady=5)
            if label=="Theme":
                self.add_entries[label] = AutocompleteCombobox(self.frame_add, width=50)
                themes = list({it["Theme"] for it in self.items})
                self.add_entries[label].set_completion_list(themes)
            else:
                if label == "Description":
                    self.add_entries[label] = tk.Text(self.frame_add, width=50, height=6)  # beaucoup de place
                else:
                    self.add_entries[label] = tk.Entry(self.frame_add,width=50)
            self.add_entries[label].grid(row=i+1,column=1,padx=5,pady=5)
            if label=="Image":
                tk.Button(self.frame_add,text="Parcourir",command=lambda e=self.add_entries[label]: self.browse_image(e)).grid(row=i+1,column=2)

        tk.Button(self.frame_add,text="Enregistrer",command=self.add_item,width=20).grid(row=6,column=1,pady=10)
        tk.Button(self.frame_add,text="Retour",command=self.show_menu,width=20).grid(row=7,column=1,pady=5)

    def create_modify_frame(self):
        labels = ["Name","Theme","Price","Image","Description"]
        self.listbox_modify = tk.Listbox(self.frame_modify,width=40,height=20)
        self.listbox_modify.grid(row=1,column=0,rowspan=6,padx=10,pady=10)
        self.listbox_modify.bind("<<ListboxSelect>>", self.on_select_modify)
        self.modify_entries = {}
        for i,label in enumerate(labels):
            tk.Label(self.frame_modify,text=label+":").grid(row=i+1,column=1,sticky="e", padx=5, pady=5)
            if label=="Theme":
                self.modify_entries[label] = AutocompleteCombobox(self.frame_modify, width=50)
            else:
                if label == "Description":
                    self.modify_entries[label] = tk.Text(self.frame_modify, width=50, height=6)
                else:
                    self.modify_entries[label] = tk.Entry(self.frame_modify,width=50)
            self.modify_entries[label].grid(row=i+1,column=2,padx=5,pady=5)
            if label=="Image":
                tk.Button(self.frame_modify,text="Parcourir",command=lambda e=self.modify_entries[label]: self.browse_image(e)).grid(row=i+1,column=3)

        tk.Button(self.frame_modify,text="Sauvegarder",command=self.save_modify,width=25).grid(row=6,column=2,pady=5)
        tk.Button(self.frame_modify,text="Supprimer",command=self.delete_item,width=25).grid(row=7,column=2,pady=5)
        tk.Button(self.frame_modify,text="Retour",command=self.show_menu,width=25).grid(row=8,column=2,pady=5)

    # --- Navigation ---
    def show_menu(self):
        self.frame_add.pack_forget()
        self.frame_modify.pack_forget()
        self.frame_menu.pack(fill="both", expand=True)

    def show_add(self):
        self.frame_menu.pack_forget()
        self.frame_modify.pack_forget()
        self.frame_add.pack(fill="both", expand=True)
        for k,e in self.add_entries.items():
            if k == "Description":
                e.delete("1.0", tk.END)
            else:
                e.delete(0, tk.END)
        themes = list({it["Theme"] for it in self.items})
        self.add_entries["Theme"].set_completion_list(themes)

    def show_modify(self):
        self.frame_menu.pack_forget()
        self.frame_add.pack_forget()
        self.frame_modify.pack(fill="both", expand=True)
        self.refresh_modify_list()

    # --- Fonctions ---
    def browse_image(self, entry):
        filename = filedialog.askdirectory(title="Choisir le dossier d'images")
        if filename:
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)
                entry.insert(0, filename)
            else:  # Text widget
                entry.delete("1.0", tk.END)
                entry.insert("1.0", filename)

    def add_item(self):
        item = {}
        for k, e in self.add_entries.items():
            if k == "Description":
                item[k] = e.get("1.0", tk.END).strip()
            else:
                item[k] = e.get()
        if not item["Name"]:
            messagebox.showerror("Erreur","Le champ Name est obligatoire")
            return

        # Vérification des doublons
        if any(it["Name"].strip().lower() == item["Name"].strip().lower() for it in self.items):
            messagebox.showerror("Erreur", f"Un item portant le nom '{item['Name']}' existe déjà !")
            return

        item["Price"] = item["Price"].replace(",",".")
        self.items.append(item)
        save_items(self.items)
        messagebox.showinfo("Succès","Item ajouté !")
        for k,e in self.add_entries.items():
            if k == "Description":
                e.delete("1.0", tk.END)
            else:
                e.delete(0, tk.END)

    def refresh_modify_list(self):
        self.listbox_modify.delete(0, tk.END)
        for it in self.items:
            self.listbox_modify.insert(tk.END,it["Name"])

    def on_select_modify(self,event):
        sel = self.listbox_modify.curselection()
        if sel:
            self.current_index = sel[0]
            item = self.items[self.current_index]
            for k,e in self.modify_entries.items():
                if k == "Description":
                    e.delete("1.0", tk.END)
                    e.insert("1.0", item[k])
                else:
                    e.delete(0, tk.END)
                    e.insert(0,item[k])
            themes = list({it["Theme"] for it in self.items})
            self.modify_entries["Theme"].set_completion_list(themes)

    def save_modify(self):
        if self.current_index is None:
            messagebox.showerror("Erreur","Aucun item sélectionné")
            return
        item = {}
        for k,e in self.modify_entries.items():
            if k == "Description":
                item[k] = e.get("1.0", tk.END).strip()
            else:
                item[k] = e.get()
        item["Price"] = item["Price"].replace(",",".")

        # Vérification des doublons (hors l'item actuel)
        for i, it in enumerate(self.items):
            if i != self.current_index and it["Name"].strip().lower() == item["Name"].strip().lower():
                messagebox.showerror("Erreur", f"Un autre item porte déjà le nom '{item['Name']}' !")
                return

        self.items[self.current_index] = item
        save_items(self.items)
        self.refresh_modify_list()
        messagebox.showinfo("Succès","Modification enregistrée")

    def delete_item(self):
        if self.current_index is None:
            messagebox.showerror("Erreur","Aucun item sélectionné")
            return
        confirm = messagebox.askyesno("Confirmer","Supprimer cet item ?")
        if confirm:
            del self.items[self.current_index]
            save_items(self.items)
            self.refresh_modify_list()
            for k,e in self.modify_entries.items():
                if k == "Description":
                    e.delete("1.0", tk.END)
                else:
                    e.delete(0, tk.END)
            self.current_index = None

# --- Lancement ---
if __name__=="__main__":
    root=tk.Tk()
    app=App(root)
    root.mainloop()
