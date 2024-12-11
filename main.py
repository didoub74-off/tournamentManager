import random
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import csv

# Global variables
noms = []
scores = {}
number_of_rounds_randoms = 1
number_of_rounds = 0
notebook = None
save = {}
def create_round():

    global noms, notebook, number_of_rounds_randoms, number_of_rounds

    if not noms:
        messagebox.showwarning("Pas de participants", "Please upload a CSV file with participant names first.")
        return

    round_type = messagebox.askquestion("Type de manche", "Voulez vous créer une manche aléatoire? (Cliquez 'Non' pour une manche classée)")

    frame = ttk.Frame(notebook)

    total_result_index = notebook.index("end") - 1

    round_number = notebook.index("end")

    if round_type == "yes":
        number_of_rounds_randoms += 1
        notebook.insert(total_result_index, frame, text=f"Manche aléatoire {number_of_rounds_randoms}")
        shuffled_participants = noms[:]
        random.shuffle(shuffled_participants)
        create_matchup_frame(frame, shuffled_participants, f"Manche aléatoire {number_of_rounds_randoms}")


    else:
        number_of_rounds += 1

        notebook.insert(total_result_index, frame, text=f"Manche classement {number_of_rounds}")
        create_seeding_button(frame, round_number)

def load_file():

    global noms
    file_path = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    if not file_path:
        messagebox.showwarning("No File Selected", "Please select a valid file.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            noms = [row[0] for row in reader if row]
        if len(noms) < 4:
            messagebox.showerror("Error", "The file must contain at least 4 names.")
            return

        create_matchup_sheets()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the file: {e}")

def delete_view(frame, label):
    global scores, notebook

    notebook.forget(frame)

    for key in list(scores.keys()):
        if key[0] == label:
            del scores[key]

def get_number_of_rounds():
    global number_of_rounds_randoms, number_of_rounds

    try:
        while True:
            number_of_rounds_randoms = int(simpledialog.askstring(
                "Input Required",
                "Enter the number of rounds with random matchups:"
            ))
            if number_of_rounds_randoms > 0:
                break
            messagebox.showerror("Invalid Input", "Please enter a positive number.")

        while True:
            number_of_rounds = int(simpledialog.askstring(
                "Input Required",
                "Enter the number of rounds for top vs top matchups:"
            ))
            if number_of_rounds > 0:
                break
            messagebox.showerror("Invalid Input", "Please enter a positive number.")

        create_matchup_sheets()
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def create_matchup_sheets():
    global noms, scores, number_of_rounds_randoms, number_of_rounds, notebook
    notebook = ttk.Notebook(root)

    frame = ttk.Frame(notebook)
    notebook.add(frame, text=f"Manche aléatoire 1")

    shuffled_participants = noms[:]
    random.shuffle(shuffled_participants)

    create_matchup_frame(frame, shuffled_participants, f"Manche aléatoire 1")


    total_scores_frame = ttk.Frame(notebook)
    notebook.add(total_scores_frame, text="Scores totaux")
    create_total_scores_frame(total_scores_frame)

    notebook.bind("<<NotebookTabChanged>>", lambda event: update_total_scores(event, notebook))
    notebook.pack(expand=True, fill='both')


def create_matchup_frame(frame, participants, label):
    global scores, number_of_rounds_randoms

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas_frame = ttk.Frame(canvas)

    canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    tk.Label(canvas_frame, text=label, font=("Arial", 14, "bold")).pack(pady=10)

    groups = [participants[i:i + 4] for i in range(0, len(participants), 4)]

    for group_index, group in enumerate(groups):
        group_frame = tk.Frame(canvas_frame)
        group_frame.pack(pady=10, padx=10, fill='x', anchor="center")

        tk.Label(group_frame, text=f"Terrain n°{group_index + 1}:", font=("Arial", 12)).grid(row=0, column=0, sticky='w', padx=5)
        for i, name in enumerate(group):
            tk.Label(group_frame, text=name).grid(row=i + 1, column=0, sticky='w', padx=5)
            entry = tk.Entry(group_frame, width=10)
            entry.grid(row=i + 1, column=1, padx=5)
            scores[(label, name)] = entry

    delete_button = tk.Button(canvas_frame, text="Delete View", command=lambda: delete_view(frame, label))
    delete_button.pack(pady=20, anchor="center")

    canvas_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def create_seeding_button(frame, round_number):
    global number_of_rounds
    tk.Label(frame, text=f"Manche classement n° {number_of_rounds}", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Button(
        frame,
        text="Effectuer le tirage classement",
        command=lambda: generate_seeded_matchups(frame, round_number)
    ).pack(pady=10)


def generate_seeded_matchups(frame, round_number):
    global noms, scores
    totals = {}
    for key, entry in scores.items():
        if not isinstance(key, tuple) or len(key) != 2:
            continue
        label, name = key
        score = entry.get().strip()
        if not score.isdigit():
            score = 0
        else:
            score = int(score)
        totals[name] = totals.get(name, 0) + score

    sorted_participants = sorted(totals.keys(), key=lambda x: totals[x], reverse=True)

    for widget in frame.winfo_children():
        widget.destroy()

    create_matchup_frame(frame, sorted_participants, f"Seeded Round {round_number}")


def create_total_scores_frame(frame):
    global scores

    tk.Label(frame, text="Score totaux", font=("Arial", 16, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("Name", "Score"), show="headings", height=20)
    tree.heading("Name", text="Name")
    tree.heading("Score", text="Total Score")
    tree.column("Name", anchor="w", width=150)
    tree.column("Score", anchor="center", width=100)
    tree.pack(pady=10, fill="both", expand=True)

    style = ttk.Style()
    style.configure("Treeview", rowheight=25, font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

    scores['total_scores_tree'] = tree


def calculate_total_scores():
    global scores
    totals = {}
    for key, entry in scores.items():
        if not isinstance(key, tuple) or len(key) != 2:
            continue
        label, name = key
        score = entry.get().strip()
        if not score.isdigit():
            score = 0
        else:
            score = int(score)
        totals[name] = totals.get(name, 0) + score
    return totals


def update_total_scores(event, notebook):
    """
    Update the Total Scores tab dynamically when selected.
    """
    global scores
    selected_tab = notebook.tab(notebook.select(), "text")
    if selected_tab == "Scores totaux":
        totals = calculate_total_scores()
        tree = scores['total_scores_tree']

        print(totals)

        for row in tree.get_children():
            tree.delete(row)

        if totals:
            max_score = max(totals.values())
            min_score = min(totals.values())
            score_range = max_score - min_score if max_score != min_score else 1

            for name, score in sorted(totals.items(), key=lambda x: x[1], reverse=True):
                intensity = int(255 * (score - min_score) / score_range)
                color = f"#{255 - intensity:02x}{intensity:02x}00"

                tree.insert("", "end", values=(name, score), tags=(color,))
                tree.tag_configure(color, background=color, foreground="black")

def on_close():
    if messagebox.askokcancel("Quitter", "Voulez-vous quitter le gestionnaire?"):
        if messagebox.askyesno("Confirmer", "Êtes-vous sûr de vouloir quitter ? Les données non sauvegardées seront perdue."):
            root.destroy()

def toggle_fullscreen(event):
    current_state = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not current_state)

def create_new_user():

    new_user_name = simpledialog.askstring("Nouveau participant", "Entrez le nom du nouveau participant")

    if new_user_name:
        noms.append(new_user_name)
        messagebox.showinfo("Nouveau participant", f"Le participant {new_user_name} a été ajouté avec succès. Il sera inclus dès la prochaine manche.")
    else:
        messagebox.showwarning("Aucun nom", "Veuillez entrer un nom valide.")

root = tk.Tk()
root.title("Gestionnaire de tournoi")

root.bind("<Escape>", toggle_fullscreen)

label = tk.Label(root, text="Bienvenue dans le générateur de matchs de tournoi", font=("Arial", 16, "bold"))
label.pack(pady=10)

label2 = tk.Label(root, text="Veuillez charger un fichier CSV contenant les noms des participants.", font=("Arial", 12))
label2.pack(pady=10)

label3 = tk.Label(root, text="Ce programme a été créé par Darlann Banache en 2024", font=("Arial", 10))
label3.pack(pady=0)

label4 = tk.Label(root, text="Pour alterner entre plein-écran et fenêtré, appuyez sur la touche échap (esc)", font=("Arial", 10))
label4.pack(pady=0)

upload_button = tk.Button(root, text="Envoyer le fichier de participants (format CSV)", command=load_file)
upload_button.pack(pady=20)

create_round_button = tk.Button(root, text="Créer une nouvelle manche", command=create_round)
create_round_button.pack(pady=20)

new_user_button = tk.Button(root, text="Ajouter un nouveau participant", command=create_new_user)
new_user_button.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", on_close)
root.attributes("-fullscreen", True)
root.mainloop()

