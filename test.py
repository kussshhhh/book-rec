# Import the necessary library
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value

def solve_forecasting_problem(actual_demand, lower_bound=None, upper_bound=None):
    # Number of periods
    T = len(actual_demand)
    
    # Create a linear programming problem
    problem = LpProblem("Forecasting_Error_Minimization", LpMinimize)
    
    # Decision variables
    x = [LpVariable(f"x_{t}", lowBound=0) for t in range(T)]  # Forecasted demand
    e_plus = [LpVariable(f"e_plus_{t}", lowBound=0) for t in range(T)]  # Positive error
    e_minus = [LpVariable(f"e_minus_{t}", lowBound=0) for t in range(T)]  # Negative error
    
    # Objective function: Minimize the sum of absolute errors
    problem += lpSum([e_plus[t] + e_minus[t] for t in range(T)]), "Total_Error"
    
    # Constraints for each period
    for t in range(T):
        # Error constraints
        problem += actual_demand[t] - x[t] <= e_plus[t], f"Pos_Error_Constraint_{t+1}"
        problem += x[t] - actual_demand[t] <= e_minus[t], f"Neg_Error_Constraint_{t+1}"
        
        # Optional bounds on forecasted demand
        if lower_bound:
            problem += x[t] >= lower_bound[t], f"Lower_Bound_{t+1}"
        if upper_bound:
            problem += x[t] <= upper_bound[t], f"Upper_Bound_{t+1}"
    
    # Solve the problem
    problem.solve()
    
    # Extract results
    forecasted_demand = [value(x[t]) for t in range(T)]
    total_error = sum([value(e_plus[t]) + value(e_minus[t]) for t in range(T)])
    
    return forecasted_demand, total_error

# Example usage
actual_demand = [100, 150, 200, 250, 300]  # Actual sales data
lower_bound = [90, 140, 180, 230, 280]     # Optional: Minimum forecast constraint
upper_bound = [110, 160, 220, 270, 320]    # Optional: Maximum forecast constraint

forecasted_demand, total_error = solve_forecasting_problem(actual_demand, lower_bound, upper_bound)

print("Forecasted Demand:", forecasted_demand)
print("Total Forecasting Error:", total_error)