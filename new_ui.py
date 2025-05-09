import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from model import optimal_team

class FantasyDraftUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fantasy Football Draft Optimizer")
        self.root.geometry("800x600")
        
        # Initialize data
        self.data = pd.read_csv('data.csv')
        self.data['position'] = self.data['Converted'].str[:2]
        self.data['variable'] = self.data['position'] + '_' + self.data['Converted']
        
        # Initialize roster spots and salary cap
        self.roster_spots = {
            'QB': 2,
            'WR': 4,
            'TE': 2,
            'RB': 2,
            'KR': 1,
            'DE': 1
        }
        self.salary_cap = 194
        self.remaining_salary = self.salary_cap
        self.my_team = []
        self.removed_players = []  # Track players removed from draft pool
        self.action_history = []  # Track actions for undo
        
        # Create main layout
        self.create_layout()
        
        # Initialize displays
        self.update_displays()

    def create_layout(self):
        # Create main frames
        self.left_frame = ttk.Frame(self.root, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.root, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create components
        self.create_roster_display()
        self.create_player_selection()
        self.create_team_displays()
        self.create_salary_display()
        self.create_undo_button()

    def create_roster_display(self):
        # Roster spots frame
        roster_frame = ttk.LabelFrame(self.left_frame, text="Roster Spots", padding="10")
        roster_frame.pack(fill=tk.X, pady=5)
        
        # Create roster spots display
        self.roster_labels = {}
        for position in self.roster_spots:
            frame = ttk.Frame(roster_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=f"{position}:").pack(side=tk.LEFT)
            self.roster_labels[position] = ttk.Label(frame, text=str(self.roster_spots[position]))
            self.roster_labels[position].pack(side=tk.LEFT, padx=5)

    def create_player_selection(self):
        # Player selection frame
        selection_frame = ttk.LabelFrame(self.right_frame, text="Player Selection", padding="10")
        selection_frame.pack(fill=tk.X, pady=5)
        
        # Position filter
        filter_frame = ttk.Frame(selection_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Filter by Position:").pack(side=tk.LEFT)
        self.position_var = tk.StringVar(value="ALL")
        self.position_combo = ttk.Combobox(filter_frame, textvariable=self.position_var, 
                                    values=["ALL"] + list(self.roster_spots.keys()))
        self.position_combo.pack(side=tk.LEFT, padx=5)
        self.position_combo.bind("<<ComboboxSelected>>", self.filter_players)
        
        # Player selection
        self.player_var = tk.StringVar()
        self.player_combo = ttk.Combobox(selection_frame, textvariable=self.player_var, width=30)
        self.player_combo.pack(fill=tk.X, pady=5)
        
        # Bind Enter key for search
        self.player_combo.bind('<Return>', self.search_players)
        self.player_combo.bind("<<ComboboxSelected>>", self.on_player_selected)
        
        # Update player list
        self.update_player_list()

    def create_team_displays(self):
        # Teams frame
        teams_frame = ttk.Frame(self.left_frame)
        teams_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create four columns for different player lists
        # Column 1: My Team
        current_team_frame = ttk.LabelFrame(teams_frame, text="My Roster", padding="10")
        current_team_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.current_team_listbox = tk.Listbox(current_team_frame, height=10, width=30)
        self.current_team_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Column 2: Optimal Team Suggestion
        optimal_frame = ttk.LabelFrame(teams_frame, text="Optimal Team Suggestion", padding="10")
        optimal_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.optimal_listbox = tk.Listbox(optimal_frame, height=10, width=30)
        self.optimal_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Column 3: Remaining Players (sorted by points)
        remaining_frame = ttk.LabelFrame(teams_frame, text="Remaining Players (by Points)", padding="10")
        remaining_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.remaining_listbox = tk.Listbox(remaining_frame, height=10, width=30)
        self.remaining_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Column 4: Removed Players
        removed_frame = ttk.LabelFrame(teams_frame, text="Removed from Draft", padding="10")
        removed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.removed_listbox = tk.Listbox(removed_frame, height=10, width=30)
        self.removed_listbox.pack(fill=tk.BOTH, expand=True)

    def create_salary_display(self):
        # Salary frame
        salary_frame = ttk.LabelFrame(self.left_frame, text="Salary Cap", padding="10")
        salary_frame.pack(fill=tk.X, pady=5)
        
        # Create a frame for salary information
        salary_info_frame = ttk.Frame(salary_frame)
        salary_info_frame.pack(fill=tk.X)
        
        # Total cap
        total_cap_frame = ttk.Frame(salary_info_frame)
        total_cap_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(total_cap_frame, text="Total Cap:").pack()
        self.total_cap_label = ttk.Label(total_cap_frame, text=f"${self.salary_cap}")
        self.total_cap_label.pack()
        
        # Money spent
        spent_frame = ttk.Frame(salary_info_frame)
        spent_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(spent_frame, text="Money Spent:").pack()
        self.spent_label = ttk.Label(spent_frame, text=f"${self.salary_cap - self.remaining_salary}")
        self.spent_label.pack()
        
        # Money remaining
        remaining_frame = ttk.Frame(salary_info_frame)
        remaining_frame.pack(side=tk.LEFT, padx=10)
        ttk.Label(remaining_frame, text="Money Remaining:").pack()
        self.salary_label = ttk.Label(remaining_frame, text=f"${self.remaining_salary}")
        self.salary_label.pack()

    def create_undo_button(self):
        # Create undo button frame
        undo_frame = ttk.Frame(self.left_frame)
        undo_frame.pack(fill=tk.X, pady=5)
        
        self.undo_button = ttk.Button(undo_frame, text="Undo Last Action", command=self.undo_last_action)
        self.undo_button.pack(side=tk.LEFT)
        
        # Initially disable the button
        self.undo_button.state(['disabled'])

    def update_player_list(self):
        # Filter players based on position
        position = self.position_var.get()
        
        # Debug prints
        print("\nCurrent state:")
        print(f"My team: {self.my_team}")
        print(f"Removed players: {self.removed_players}")
        print(f"Position filter: {position}")
        
        # Get available players (not in my team and not removed)
        available_players = self.data[
            (~self.data['Player'].isin(self.my_team)) & 
            (~self.data['Player'].isin(self.removed_players))
        ].copy()
        print(f"Available players before position filter: {len(available_players)}")
        
        # Filter out positions with no remaining spots
        available_positions = [pos for pos, spots in self.roster_spots.items() if spots > 0]
        available_players = available_players[available_players['position'].isin(available_positions)]
        print(f"Available players after removing filled positions: {len(available_players)}")
        
        if position != "ALL":
            available_players = available_players[available_players['position'] == position]
            print(f"Available players after position filter: {len(available_players)}")
        
        # Sort players by projected points
        available_players = available_players.sort_values('Points', ascending=False)
        
        # Debug print the final list
        print("\nAvailable players:")
        for _, player in available_players.iterrows():
            print(f"- {player['Player']} ({player['position']}): {player['Points']} points")
        print()
        
        # Update position filter dropdown to only show available positions
        self.position_var.set("ALL")  # Reset to ALL
        self.position_combo['values'] = ["ALL"] + available_positions
        
        self.player_combo['values'] = available_players['Player'].tolist()
        self.player_var.set('')  # Clear selection

    def filter_players(self, event=None):
        self.update_player_list()

    def on_player_selected(self, event):
        selected_player = self.player_var.get()
        if not selected_player:
            return
            
        # Get player info
        player_info = self.data[self.data['Player'] == selected_player].iloc[0]
        position = player_info['position']
        cost = player_info['23_Cost']
        points = player_info['Points']
        
        # Create dialog for player action
        dialog = tk.Toplevel(self.root)
        dialog.title("Player Action")
        dialog.geometry("300x200")
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add player info
        info_frame = ttk.Frame(dialog, padding=10)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text=f"Player: {selected_player}", font=('Helvetica', 10, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text=f"Position: {position}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Salary: ${cost}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Projected Points: {points:.1f}").pack(anchor='w')
        
        # Add message
        msg = f"What would you like to do with {selected_player}?"
        ttk.Label(dialog, text=msg, padding=10).pack()
        
        # Add buttons
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Add to Team", 
                  command=lambda: self.add_to_team(selected_player, position, cost, dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove from Draft Pool", 
                  command=lambda: self.remove_from_pool(selected_player, dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def update_displays(self):
        # Update roster spots
        for position, label in self.roster_labels.items():
            label.config(text=str(self.roster_spots[position]))
        
        # Update salary displays
        self.total_cap_label.config(text=f"${self.salary_cap}")
        self.spent_label.config(text=f"${self.salary_cap - self.remaining_salary}")
        self.salary_label.config(text=f"${self.remaining_salary}")
        
        # Update current team display
        self.current_team_listbox.delete(0, tk.END)
        for player in self.my_team:
            self.current_team_listbox.insert(tk.END, player)
        
        # Update remaining players display (sorted by points)
        self.remaining_listbox.delete(0, tk.END)
        remaining_players = self.data[
            (~self.data['Player'].isin(self.my_team)) & 
            (~self.data['Player'].isin(self.removed_players))
        ].sort_values('Points', ascending=False)
        
        for _, player in remaining_players.iterrows():
            display_text = f"{player['Player']} ({player['position']}) - {player['Points']:.1f} pts"
            self.remaining_listbox.insert(tk.END, display_text)
        
        # Update removed players display
        self.removed_listbox.delete(0, tk.END)
        for player in self.removed_players:
            player_info = self.data[self.data['Player'] == player].iloc[0]
            display_text = f"{player} ({player_info['position']}) - {player_info['Points']:.1f} pts"
            self.removed_listbox.insert(tk.END, display_text)
        
        # Create a copy of the data for optimization
        optimization_data = self.data.copy()
        
        # Remove players that are in my_team or removed_players
        optimization_data = optimization_data[
            (~optimization_data['Player'].isin(self.my_team)) & 
            (~optimization_data['Player'].isin(self.removed_players))
        ]
        
        # Update optimal team suggestion
        self.optimal_listbox.delete(0, tk.END)
        optimal_team_suggestion = optimal_team(optimization_data, self.roster_spots, self.remaining_salary)
        
        # Print optimal team to console and update display
        print("\nOptimal Team Suggestion:")
        for player in optimal_team_suggestion:
            print(f"- {player}")
            player_info = self.data[self.data['Player'] == player].iloc[0]
            display_text = f"{player} ({player_info['position']}) - {player_info['Points']:.1f} pts"
            self.optimal_listbox.insert(tk.END, display_text)
        print()
        
        # Update player list
        self.update_player_list()

    def search_players(self, event):
        # Get the current text in the combo box
        search_text = self.player_var.get().lower()
        
        # Get all available players
        available_players = self.data[~self.data['Player'].isin(self.my_team)].copy()
        
        # Filter out positions with no remaining spots
        available_positions = [pos for pos, spots in self.roster_spots.items() if spots > 0]
        available_players = available_players[available_players['position'].isin(available_positions)]
        
        # Apply position filter if one is selected
        position = self.position_var.get()
        if position != "ALL":
            available_players = available_players[available_players['position'] == position]
        
        # Filter players based on search text
        if search_text:
            filtered_players = available_players[
                available_players['Player'].str.lower().str.contains(search_text)
            ]
        else:
            filtered_players = available_players
        
        # Sort by points and update the combo box
        filtered_players = filtered_players.sort_values('Points', ascending=False)
        self.player_combo['values'] = filtered_players['Player'].tolist()
        
        # Show dropdown with results
        if len(filtered_players) > 0:
            self.player_combo.event_generate('<Down>')

    def undo_last_action(self):
        if not self.action_history:
            return
            
        # Get the last action
        last_action = self.action_history.pop()
        action_type = last_action['type']
        player = last_action['player']
        position = last_action['position']
        cost = last_action['cost']
        
        if action_type == 'add':
            # Remove from team
            self.my_team.remove(player)
            self.roster_spots[position] += 1
            self.remaining_salary += cost
        elif action_type == 'remove':
            # Add back to draft pool
            self.removed_players.remove(player)
        
        # Update displays
        self.update_displays()
        
        # Show confirmation
        messagebox.showinfo("Undo", f"Undid last action: {action_type} {player}")
        
        # Update undo button state
        self.undo_button.state(['!disabled'] if self.action_history else ['disabled'])

    def add_to_team(self, player, position, cost, dialog):
        # Check if we can afford the player
        if cost > self.remaining_salary:
            messagebox.showerror("Error", "Cannot afford this player!")
            dialog.destroy()
            return
            
        # Check if we have roster spots available
        if self.roster_spots[position] <= 0:
            messagebox.showerror("Error", f"No {position} spots remaining!")
            dialog.destroy()
            return
            
        # Add player to team
        self.my_team.append(player)
        self.roster_spots[position] -= 1
        self.remaining_salary -= cost
        
        # Add to action history
        self.action_history.append({
            'type': 'add',
            'player': player,
            'position': position,
            'cost': cost
        })
        
        # Update displays
        self.update_displays()
        
        # Enable undo button
        self.undo_button.state(['!disabled'])
        
        # Show confirmation
        messagebox.showinfo("Success", f"Added {player} to your team!")
        dialog.destroy()

    def remove_from_pool(self, player, dialog):
        # Add player to removed list
        self.removed_players.append(player)
        
        # Add to action history
        self.action_history.append({
            'type': 'remove',
            'player': player,
            'position': self.data[self.data['Player'] == player]['position'].iloc[0],
            'cost': self.data[self.data['Player'] == player]['23_Cost'].iloc[0]
        })
        
        # Update displays
        self.update_displays()
        
        # Enable undo button
        self.undo_button.state(['!disabled'])
        
        # Show confirmation
        messagebox.showinfo("Success", f"Removed {player} from draft pool!")
        dialog.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FantasyDraftUI(root)
    root.mainloop() 