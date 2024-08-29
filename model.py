import pandas as pd
import pulp
import re


league_df = pd.read_csv('data.csv')

solver = pulp.PULP_CBC_CMD(msg=False)

#Get position
league_df['position'] = league_df['Converted'].str[:2]

roster_spots = {'QB':2
                ,'WR':4
                ,'TE':2
                ,'RB':2
                ,'KR':1
                ,'DE':1
                }


def optimal_team(league_df,roster_spots):
    salary_cap = 194
    salaries = {}
    points = {}
    for pos in league_df['position'].unique():
        available_pos = league_df[league_df['position']==pos]
        salary = list(available_pos[['Converted','Exp_Cost']].set_index('Converted').to_dict().values())[0]
        point = list(available_pos[['Converted','Points']].set_index('Converted').to_dict().values())[0]
        salaries[pos] = salary
        points[pos] = point
    

    _vars = {k: pulp.LpVariable.dict(k, v, cat="Binary") for k, v in points.items()}

    prob = pulp.LpProblem("Fantasy", pulp.LpMaximize)
    rewards = []
    costs = []
    position_constraints = []
    # Setting up the reward
    for k, v in _vars.items():
        costs += pulp.lpSum([salaries[k][i] * _vars[k][i] for i in v])
        rewards += pulp.lpSum([points[k][i] * _vars[k][i] for i in v])
        prob += pulp.lpSum([_vars[k][i] for i in v]) <= roster_spots[k]
        
    prob += pulp.lpSum(rewards)
    prob += pulp.lpSum(costs) <= salary_cap

    prob.solve(solver)

    #score = str(prob.objective)
    #constraints = [str(const) for const in prob.constraints.values()]

    optimal_roster = []
    for v in prob.variables():
        #score = score.replace(v.name, str(v.varValue))
        #constraints = [const.replace(v.name, str(v.varValue)) for const in constraints]
        if v.varValue != 0:
            print(v.name, "=", v.varValue)
            optimal_roster.append(v)
    
    return optimal_roster
    
    
if __name__=="__main__":

    optimal_team(league_df,roster_spots)