import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess


def run_game1():
    subprocess.run(['python', 'music_count.py'])


def run_game2():
    subprocess.run(['python', 'number_fingers.py'])


def run_game3():
    subprocess.run(['python', 'missing_letter.py'])

def run_game4():
    subprocess.run(['python', 'fechar_Abrir.py'])

def run_game5():
    subprocess.run(['python', 'filling_bar.py'])

def run_game6():
    subprocess.run(['python', 'memory_sequence.py'])


def run_game7():
    subprocess.run(['python', 'hand_detection.py'])

def run_game8():
    subprocess.run(['python', 'number_hands.py'])


def show_leaderboard():
    try:
        with open("hand_detection_leaderboard.txt", "r") as file:
            leaderboard_data = file.read()
        
        messagebox.showinfo("Leaderboard - Hand Detection", leaderboard_data)
    except FileNotFoundError:
        messagebox.showwarning("Leaderboard Not Found", "No leaderboard data found!")

# Function to switch back to the theme selection view
def show_themes():
    hide_all_frames()  
    theme_frame.pack(pady=20) 

# Function to show games based on the selected theme
def show_games(theme):
    hide_all_frames()  
    game_frame.pack(pady=20)


    for widget in game_frame.winfo_children():
        widget.destroy()

    # Display games based on the selected theme
    if theme == "Math":
        game_label = tk.Label(game_frame, text="Math Games", font=("Helvetica", 20, "bold"), bg="#ffffff", fg="#003366")
        game_label.pack(pady=10)

        # Add Play button for Hand Detection game
        play_hand_detection_btn = create_button("Play Hand Detection", run_game7, game_frame)
        play_hand_detection_btn.pack(pady=5)

        # Add Leaderboard button for Hand Detection game
        leaderboard_btn = create_button("Leaderboard", show_leaderboard, game_frame)
        leaderboard_btn.pack(pady=5)
        
    elif theme == "Vocabulary":
        game_label = tk.Label(game_frame, text="Vocabulary Games", font=("Helvetica", 20, "bold"), bg="#ffffff", fg="#003366")
        game_label.pack(pady=10)
        create_button("Play missing_letter", run_game3, game_frame).pack(pady=5)
    elif theme == "Fun":
        game_label = tk.Label(game_frame, text="Fun Games", font=("Helvetica", 20, "bold"), bg="#ffffff", fg="#003366")
        game_label.pack(pady=10)
        create_button("Play fechar_Abrir", run_game4, game_frame).pack(pady=5)
        create_button("Play filling_bar", run_game5, game_frame).pack(pady=5)
        create_button("Play music_count", run_game1, game_frame).pack(pady=5)
        create_button("Play memory_sequence", run_game6, game_frame).pack(pady=5)
    elif theme == "Co-op":
        game_label = tk.Label(game_frame, text="Co-op Games", font=("Helvetica", 20, "bold"), bg="#ffffff", fg="#003366")
        game_label.pack(pady=10)
        create_button("Play number_fingers", run_game2, game_frame).pack(pady=5)
        create_button("Play number_hands", run_game8, game_frame).pack(pady=5)

    # Add a "Back" button to go back to the theme selection
    back_button = create_button("Back", show_themes, game_frame)
    back_button.pack(pady=20)

# Function to create a styled button
def create_button(text, command, parent):
    return tk.Button(parent, 
                     text=text, 
                     command=command, 
                     font=("Helvetica", 16, "bold"), 
                     bg="#5c85d6",  
                     fg="white",    
                     activebackground="#003366",  
                     activeforeground="white",    
                     width=15, 
                     height=2, 
                     bd=0,        
                     highlightthickness=0, 
                     relief="flat")  

# Function to hide all frames
def hide_all_frames():
    theme_frame.pack_forget()
    game_frame.pack_forget()

# Create the main window
window = tk.Tk()
window.title("Game Launcher")
window.geometry("600x600")

# Add a background image (Make sure to replace 'background.jpg' with your image file)
bg_image = Image.open("background.jpg")
bg_image = bg_image.resize((600, 600), Image.ANTIALIAS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a label for the background image
bg_label = tk.Label(window, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create frames for themes and games
theme_frame = tk.Frame(window, bg="#ffffff")
game_frame = tk.Frame(window, bg="#ffffff")

# === THEME SELECTION ===
# Title label for theme selection
title_label = tk.Label(theme_frame, text="Choose a Theme", font=("Helvetica", 24, "bold"), bg="#ffffff", fg="#003366")
title_label.pack(pady=20)

# Create buttons for each theme
create_button("Math", lambda: show_games("Math"), theme_frame).pack(pady=10)
create_button("Vocabulary", lambda: show_games("Vocabulary"), theme_frame).pack(pady=10)
create_button("Fun", lambda: show_games("Fun"), theme_frame).pack(pady=10)
create_button("Co-op", lambda: show_games("Co-op"), theme_frame).pack(pady=10)

# Initially show the theme selection
show_themes()


window.mainloop()
