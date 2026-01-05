# CLAUDE.md - AI Assistant Guide for Fantasy Football 2024 Optimizer

## Project Overview

This is a **Fantasy Football Draft Optimizer** web application that helps users build optimal fantasy football teams within salary cap constraints using linear programming optimization.

**Tech Stack:**
- **Backend:** Flask (Python 3.9.18)
- **Optimization:** PuLP (linear programming solver)
- **Data Processing:** Pandas, NumPy
- **Frontend:** HTML, Bootstrap 5, vanilla JavaScript
- **Deployment:** Render (Gunicorn WSGI server)

**Purpose:** Provides real-time optimal team suggestions based on player statistics, remaining salary cap, and roster constraints.

---

## Repository Structure

```
ff_2024/
├── app.py                  # Main Flask application with API endpoints
├── model.py                # Linear programming optimization logic
├── data.csv                # Player statistics (Points, Cost, Position)
├── ff_eda.ipynb            # Exploratory Data Analysis notebook
├── templates/
│   └── index.html          # Frontend UI (Bootstrap + JavaScript)
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment configuration
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation

```

---

## Core Components

### 1. app.py (Flask Application)
**Location:** `/home/user/ff_2024/app.py`

**Key Responsibilities:**
- Initialize Flask app and load player data from CSV
- Serve the main UI via `/` route
- Provide `/api/initial_data` endpoint for initial player list, roster spots, and salary cap
- Handle `/api/optimal_team` POST requests to calculate optimal team suggestions

**Important Variables:**
- `roster_spots`: Dictionary defining position requirements
  ```python
  {'QB': 2, 'WR': 4, 'TE': 2, 'RB': 2, 'KR': 1, 'DE': 1}
  ```
- `salary_cap`: Total budget (194)
- `data`: Pandas DataFrame with player statistics

**Data Processing:**
- Extracts position from `Converted` column (first 2 characters)
- Creates `variable` column: `position + '_' + Converted` (e.g., "QB_QB01")

**API Endpoints:**

#### GET /api/initial_data
Returns all available players with their stats, roster requirements, and salary cap.

#### POST /api/optimal_team
**Request Body:**
```json
{
  "my_team": ["Player Name 1", "Player Name 2"],
  "removed_players": ["Player Name 3"],
  "remaining_salary": 150
}
```
**Response:**
```json
{
  "optimal_team": [
    {"name": "Player Name", "position": "QB", "points": 450.5, "cost": 50}
  ]
}
```

### 2. model.py (Optimization Engine)
**Location:** `/home/user/ff_2024/model.py`

**Key Function:** `optimal_team(league_df, roster_spots, salary)`

**Algorithm:** Binary Linear Programming (0-1 Knapsack variant)
- **Objective:** Maximize total fantasy points
- **Constraints:**
  1. Position limits (e.g., max 2 QBs, 4 WRs)
  2. Salary cap constraint
  3. Binary selection (each player selected 0 or 1 times)

**How It Works:**
1. Creates binary decision variables for each player
2. Sets up objective function: Sum of (player_points × selected)
3. Adds constraints for position limits and salary cap
4. Solves using PuLP's CBC solver
5. Returns list of player names in optimal roster

**Important:** Returns empty list `[]` if no optimal solution found.

### 3. data.csv (Player Database)
**Location:** `/home/user/ff_2024/data.csv`

**Schema:**
- `Converted`: Player ID (e.g., "QB01", "WR15")
- `Points`: Projected fantasy points (float)
- `Exp_Cost`: Expected cost/salary (int)
- `23_Cost`: 2023 actual cost (int)
- `Max_Cost`: Maximum cost (int)
- `Player`: Player full name (string)

**Positions:** QB, WR, TE, RB, KR, DE

### 4. templates/index.html (Frontend UI)
**Location:** `/home/user/ff_2024/templates/index.html`

**Features:**
- Bootstrap 5 responsive design
- Four main sections:
  1. **Salary Info Dashboard:** Shows roster points, expected points, cap, spent, remaining
  2. **Roster Spots Tracker:** Visual display of remaining spots per position
  3. **My Roster:** User's selected players
  4. **Optimal Team:** AI-suggested optimal additions
  5. **Available Players:** Searchable, filterable player list
  6. **Removed Players:** Players user doesn't want to consider

**JavaScript Functionality:**
- Fetches initial data on page load
- Manages player selection/removal with drag-and-drop or clicks
- Calls `/api/optimal_team` when roster changes
- Updates all displays in real-time

### 5. ff_eda.ipynb (Analysis Notebook)
**Location:** `/home/user/ff_2024/ff_eda.ipynb`

**Purpose:** Exploratory Data Analysis and optimization algorithm prototyping

**Contents:**
- Data loading and inspection
- Position-based grouping
- PuLP optimization testing
- Constraint verification
- Results visualization

---

## Development Workflows

### Local Development

**Start the application:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask development server
python app.py
# Access at http://localhost:5000
```

**Testing changes:**
1. Modify backend logic in `app.py` or `model.py`
2. Flask auto-reloads in debug mode
3. Refresh browser to see changes

### Data Updates

**To update player statistics:**
1. Edit `data.csv` with new player data
2. Maintain schema: `Converted,Points,Exp_Cost,23_Cost,Max_Cost,Player`
3. Ensure position prefixes in `Converted` match roster_spots keys
4. Restart Flask app to reload data

### Frontend Changes

**Modify UI:**
1. Edit `/home/user/ff_2024/templates/index.html`
2. Changes appear immediately on page refresh
3. JavaScript is inline in the HTML file

### Optimization Algorithm Changes

**Modifying constraints or objective:**
1. Edit `optimal_team()` function in `model.py`
2. Test in `ff_eda.ipynb` first for validation
3. Update `app.py` if function signature changes

### Deployment to Render

**Configuration:** `render.yaml`
```yaml
services:
  - type: web
    name: ff-2024
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

**Process:**
1. Push changes to main branch
2. Render automatically deploys via webhook
3. Build command installs dependencies
4. Start command runs Gunicorn (production WSGI server)

---

## Key Conventions & Best Practices

### Code Style

**Python:**
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Keep functions focused and single-purpose
- Add comments for complex logic (especially in optimization)

**Data Handling:**
- Always use `.copy()` when modifying DataFrames to avoid side effects
- Validate input data before optimization
- Handle edge cases (empty rosters, insufficient salary)

### Error Handling

**Current State:**
- Limited error handling in place
- Optimization returns `[]` if infeasible

**Best Practices for Adding Features:**
- Validate JSON payloads in Flask routes
- Check for missing players in data before optimization
- Return meaningful error messages to frontend
- Log errors for debugging

### Testing Approach

**Recommended Testing Strategy:**
1. **Unit Tests:** Test `optimal_team()` with known inputs
2. **Integration Tests:** Test API endpoints with sample payloads
3. **Data Validation:** Ensure CSV data integrity
4. **Optimization Tests:** Verify constraints are respected

**Example Test Cases:**
- Empty roster → Returns full optimal team
- Over salary cap → Returns feasible solution or empty list
- All positions filled → Returns empty optimal team
- Invalid player names → Handles gracefully

### Performance Considerations

**Optimization Performance:**
- PuLP solver is fast for current dataset size (~300 players)
- Complexity is O(n) for n players with CBC solver
- No caching implemented (each request recalculates)

**Potential Optimizations:**
- Cache optimization results for identical inputs
- Use faster solver (CPLEX, Gurobi) for larger datasets
- Pre-filter obviously suboptimal players

### Git Workflow

**Branch Strategy:**
- Main branch: production-ready code
- Feature branches: `claude/feature-name-XXXXX`
- Always develop on designated feature branch

**Commit Messages:**
- Use descriptive messages: "Add position filter to player list"
- Avoid vague messages: "fix stuff", "updates"

**Before Committing:**
- Test locally with `python app.py`
- Verify optimization logic in notebook if changed
- Check that requirements.txt is up-to-date

---

## Common Tasks for AI Assistants

### Adding a New Position

1. Update `roster_spots` dictionary in both `app.py` and `model.py`
2. Add players with new position prefix to `data.csv`
3. Update frontend position filter in `index.html`
4. Test optimization with new constraints

### Modifying Salary Cap

1. Change `salary_cap` variable in `app.py:21`
2. Update frontend display in `index.html` (optional)
3. No changes needed in `model.py` (accepts salary as parameter)

### Adding New Player Attributes

1. Add column to `data.csv`
2. Update data loading in `app.py` if needed for API
3. Modify frontend to display new attribute
4. Update optimization logic if attribute affects selection

### Debugging Optimization Issues

**Common Problems:**
1. **Returns empty list:**
   - Check salary constraint isn't too restrictive
   - Verify all positions have available players
   - Ensure roster_spots matches data positions

2. **Incorrect optimal team:**
   - Verify Points column has correct values
   - Check constraint logic in `model.py:48`
   - Test in notebook with print statements

3. **Performance issues:**
   - Profile with larger datasets
   - Consider pre-filtering low-value players
   - Check solver status: `pulp.LpStatus[prob.status]`

### Frontend Enhancements

**Current Architecture:**
- Vanilla JavaScript (no framework)
- Bootstrap for styling
- Inline JavaScript in HTML

**Adding Features:**
- Player statistics modal: Add Bootstrap modal component
- Export roster: Use `JSON.stringify()` and download
- Save/load rosters: Use localStorage or backend endpoint
- Sorting options: Add event listeners to column headers

---

## Important Notes for AI Assistants

### What NOT to Change

1. **CSV Schema:** Changing column names breaks data loading
2. **Position Codes:** Two-letter prefixes are hardcoded (QB, WR, TE, RB, KR, DE)
3. **API Contract:** Frontend expects specific JSON structure
4. **Solver Choice:** PuLP's CBC solver is free and sufficient

### Security Considerations

**Current State:**
- No authentication/authorization
- No input sanitization on player names
- Single-user application design

**If Adding Multi-User Support:**
- Sanitize all user inputs
- Add CSRF protection
- Implement session management
- Validate roster data server-side

### Data Privacy

- No personal user data stored
- Player statistics are public fantasy football data
- No tracking or analytics implemented

### Deployment Notes

**Render Specifics:**
- Python version locked to 3.9.18
- Uses Gunicorn in production (not Flask dev server)
- Environment variables set via Render dashboard
- Static files served by Flask (no CDN)

**Scaling Considerations:**
- Current setup handles single-instance deployment
- For high traffic: Add caching layer (Redis)
- Database migration: Move from CSV to PostgreSQL
- Consider WebSocket for real-time updates

---

## Troubleshooting Guide

### Application Won't Start

**Check:**
1. All dependencies installed: `pip install -r requirements.txt`
2. `data.csv` exists and is valid CSV format
3. Python version 3.9+ installed
4. No port conflicts on 5000 (or specified port)

### Optimization Returns Empty Team

**Debug Steps:**
1. Check remaining_salary > minimum cost player
2. Verify remaining_roster_spots has openings
3. Print `optimization_data` to see available players
4. Check solver status in model.py

### Frontend Not Updating

**Checklist:**
1. Check browser console for JavaScript errors
2. Verify API endpoints returning correct JSON
3. Clear browser cache
4. Check network tab for failed requests

### CSV Data Issues

**Validation:**
1. Ensure no empty cells in required columns
2. Points and costs must be numeric
3. Converted codes must follow pattern: `POSITION##`
4. Player names must be unique

---

## Future Enhancement Ideas

**Backend:**
- Add player injury status and game schedule data
- Implement multiple optimization strategies (balanced, risky, etc.)
- Add historical performance tracking
- Create player comparison features

**Frontend:**
- Add data visualizations (charts for points/cost efficiency)
- Implement undo/redo for roster changes
- Add roster export to CSV/PDF
- Create mobile-responsive design improvements

**Optimization:**
- Multi-week optimization (consider bye weeks)
- Add correlation analysis for player performance
- Implement Monte Carlo simulations for risk analysis
- Support for different scoring formats (PPR, standard, etc.)

**Infrastructure:**
- Add database for persistent rosters
- Implement user accounts and saved teams
- Add API rate limiting
- Create automated testing suite

---

## Quick Reference

### File Locations
- Main app: `app.py:1`
- Optimization: `model.py:26`
- Roster constraints: `app.py:13-20`
- Frontend: `templates/index.html:1`

### Key Variables
- `roster_spots`: Position requirements dict
- `salary_cap`: Total budget (194)
- `data`: Player DataFrame with all statistics

### API Endpoints
- GET `/`: Main UI
- GET `/api/initial_data`: Player list & config
- POST `/api/optimal_team`: Get optimal suggestions

### Data Columns
- `Converted`: Player ID
- `Points`: Fantasy points projection
- `Exp_Cost`: Player cost
- `Player`: Full name

---

## Questions & Support

**For Development Questions:**
1. Check this CLAUDE.md first
2. Review code comments in app.py and model.py
3. Test changes in ff_eda.ipynb notebook
4. Check Flask and PuLP documentation

**Common Issues:**
- Optimization not working → Check constraints in model.py
- UI not updating → Check JavaScript console
- Data not loading → Verify data.csv format
- Deployment issues → Check render.yaml configuration

---

*Last Updated: 2026-01-05*
*Repository: ff_2024*
*Python Version: 3.9.18*
*Framework: Flask 2.3.3*
