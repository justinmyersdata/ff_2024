import pandas as pd
from tkinter import messagebox, ttk
import tkinter as tk


roster_spots = {'QB':2
                ,'WR':4
                ,'TE':2
                ,'RB':2
                ,'KR':1
                ,'DE':1
                }

data = pd.read_csv('data.csv') 
data['position'] = data['Converted'].str[:2]



players_taken = []
def selection_changed(event):

    selection = combo.get()
    messagebox.showinfo(
        title="New Selection",
        message=f"Selected option: {selection}"
    )
    players_taken.append(selection)
    print(players_taken)
    
    spot = data[data['Player']==selection]['position'].tolist()[0]
    roster_spots[spot]-=1

    data = data[data['Player']!=selection]

    create_roster_frames(roster_spots)

def create_roster_frames(roster_spots):
    # Clear existing frames
    for widget in main_window.winfo_children():
        if isinstance(widget, tk.Frame):
            widget.destroy()
    
    # Create new frames for each roster spot
    for roster_spot in roster_spots:
        frame = tk.Frame(master=main_window, relief=tk.FLAT)
        frame.pack(side=tk.LEFT)
        label = tk.Label(master=frame, text=f'{roster_spot}:')
        label.pack()

        frame = tk.Frame(main_window, relief=tk.SUNKEN)
        frame.pack(side=tk.LEFT)
        label = tk.Label(frame, text=f'{roster_spots[roster_spot]}')
        label.pack()


main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Combobox")
combo = ttk.Combobox(values=data['Player'].tolist(),width=20)
combo2 = ttk.Combobox(values=data['Converted'].tolist(),width=20)
combo.bind("<<ComboboxSelected>>", selection_changed)
combo.place(x=50, y=50)
combo2.place(x=50,y=100)

for roster_spot in roster_spots:
    frame = tk.Frame(master=main_window, relief=tk.FLAT)
    frame.pack(side=tk.LEFT)
    label = tk.Label(master=frame, text=f'{roster_spot}:')
    label.pack()

    frame = tk.Frame(main_window, relief=tk.SUNKEN)
    frame.pack(side=tk.LEFT)
    label = tk.Label(frame, text=f'{roster_spots[roster_spot]}')
    label.pack()

main_window.mainloop()