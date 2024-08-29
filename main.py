import pandas as pd
from tkinter import messagebox, ttk
import tkinter as tk
from model import optimal_team

roster_spots = {'QB':2
                ,'WR':4
                ,'TE':2
                ,'RB':2
                ,'KR':1
                ,'DE':1
                }

salary = 194

data = pd.read_csv('data.csv') 
data['position'] = data['Converted'].str[:2]

#Add in variable dictionary
data['variable'] = data['position'] + '_' + data['Converted']

optimal_team_avaialble = optimal_team(data,roster_spots,salary)







players_taken = []
my_team = []
def selection_changed(event):
    #use data from csv through whole function
    global data
    global salary

    #on select show who we selected
    selection = combo.get()
    messagebox.showinfo(
        title="New Selection",
        message=f"Selected option: {selection}"
    )

    #Keep List of players selected
    players_taken.append(selection)
    print(players_taken)

    my_team.append(selection)
    print(my_team)

    #Keep track of roster spots avaialbe
    spot = data[data['Player']==selection]['position'].tolist()[0]
    roster_spots[spot]-=1
    salary-=data[data['Player']==selection]['23_Cost'].tolist()[0]

    if roster_spots[spot]==0:
        data = data[data['position']!=spot]

    #Update roster spots
    create_roster_frames(roster_spots)

    #Remover players from list
    data = data[data['Player']!=selection]
    combo["values"] = data['Player'].tolist()
    optimal_team(data,roster_spots,salary)

    listbox = tk.Listbox(main_window, height = 10, 
                width = 15, 
                bg = "grey",
                activestyle = 'dotbox', 
                font = "Helvetica",
                fg = "yellow")
    optimal_team_avaialble = optimal_team(data,roster_spots,salary)
    for player in optimal_team_avaialble:
        listbox.insert(tk.END, player)
        listbox.pack()

    listbox = tk.Listbox(main_window, height = 10, 
                    width = 15, 
                    bg = "grey",
                    activestyle = 'dotbox', 
                    font = "Helvetica",
                    fg = "yellow")
    for player in my_team:
        listbox.insert(tk.END, player)
    listbox.pack()


def create_roster_frames(roster_spots):
    # Clear existing frames
    for widget in main_window.winfo_children():
        if isinstance(widget, tk.Frame):
            widget.destroy()
        if isinstance(widget, tk.Listbox):
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
combo2 = ttk.Combobox(values=['Yes','No'],width=20)
combo.bind("<<ComboboxSelected>>", selection_changed)
combo.place(x=50, y=50)
combo2.place(x=50, y=25)

for roster_spot in roster_spots:
    frame = tk.Frame(master=main_window, relief=tk.FLAT)
    frame.pack(side=tk.LEFT)
    label = tk.Label(master=frame, text=f'{roster_spot}:')
    label.pack()

    frame = tk.Frame(main_window, relief=tk.SUNKEN)
    frame.pack(side=tk.LEFT)
    label = tk.Label(frame, text=f'{roster_spots[roster_spot]}')
    label.pack()


listbox = tk.Listbox(main_window, height = 10, 
                  width = 15, 
                  bg = "grey",
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg = "yellow")

for player in optimal_team_avaialble:
    listbox.insert(tk.END, player)
listbox.pack()

listbox = tk.Listbox(main_window, height = 10, 
                  width = 15, 
                  bg = "grey",
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg = "yellow")
for player in my_team:
    listbox.insert(tk.END, player)
listbox.pack()

salary_frame = tk.Frame(master=main_window, relief=tk.FLAT)
salary_frame.pack(side=tk.LEFT)
salary_label = tk.Label(master=salary_frame, text=f'{salary}')
salary_label.pack()


main_window.mainloop()