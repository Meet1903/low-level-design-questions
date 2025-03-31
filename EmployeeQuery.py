class Employee:
    def __init__(self, name, org, experience, ismanager):
        self.name = name
        self.org = org
        self.experience = experience
        self.ismanager = ismanager

    def __repr__(self):
        return (f"Employee(name={self.name}, org={self.org}, "
                f"experience={self.experience}, ismanager={self.ismanager})")

def evaluate_condition(employee, condition):
    """
    Evaluate whether an employee meets the condition.
    condition is a dictionary with keys:
        "field": one of 'org', 'experience', or 'ismanager'
        "operator": one of '==', '>=', '<=', '>', '<'
        "value": the value to compare against
    """
    field = condition["field"]
    op = condition["operator"]
    value = condition["value"]
    
    employee_value = getattr(employee, field)
    
    if op == "==":
        return employee_value == value
    elif op == ">=":
        return employee_value >= value
    elif op == "<=":
        return employee_value <= value
    elif op == ">":
        return employee_value > value
    elif op == "<":
        return employee_value < value
    else:
        raise ValueError(f"Unsupported operator: {op}")

def process_query(employees, query_conditions, query_operator, priority):
    """
    Process the query_conditions against the list of employees.
    
    Parameters:
      employees: list of Employee objects.
      query_conditions: list of dictionaries where each dictionary has keys:
          - "field": the field to query on (org, experience, or ismanager)
          - "operator": a comparison operator ('==', '>=', '<=', '>', '<')
          - "value": value to compare against.
      query_operator: "AND" or "OR" to combine the conditions.
      priority: a list of fields in the order in which the query should be processed.
                Conditions for fields that appear earlier in the list will be applied first.
                
    Returns:
      A list of Employee objects that satisfy the query.
    """
    # Order the conditions by the given priority
    # If a condition's field is not in the priority list, put it at the end.
    def priority_key(cond):
        try:
            return priority.index(cond["field"])
        except ValueError:
            return len(priority)
    
    ordered_conditions = sorted(query_conditions, key=priority_key)
    
    if query_operator.upper() == "AND":
        # Start with all employees, then filter with each condition sequentially.
        filtered_employees = employees
        for condition in ordered_conditions:
            filtered_employees = [
                emp for emp in filtered_employees if evaluate_condition(emp, condition)
            ]
        return filtered_employees

    elif query_operator.upper() == "OR":
        # For OR, collect employees satisfying any condition.
        result_set = set()
        for condition in ordered_conditions:
            for emp in employees:
                if evaluate_condition(emp, condition):
                    result_set.add(emp)
        return list(result_set)
    else:
        raise ValueError("query_operator must be 'AND' or 'OR'")

# Example usage:
if __name__ == "__main__":
    # Sample employee list
    employees = [
        Employee("Alice", "Google", 6, True),
        Employee("Bob", "Amazon", 4, False),
        Employee("Charlie", "Google", 3, False),
        Employee("Diana", "Facebook", 8, True),
        Employee("Eve", "Amazon", 5, True)
    ]
    
    # Define query conditions.
    # For example, we want employees from "Amazon" with experience >= 5 and who are managers.
    query_conditions = [
        {"field": "org", "operator": "==", "value": "Amazon"},
        {"field": "experience", "operator": ">=", "value": 5},
        {"field": "ismanager", "operator": "==", "value": True}
    ]
    
    # Define priority (process org first, then experience, then ismanager)
    priority = ["org", "experience", "ismanager"]
    
    # Process the query using "AND" logic:
    result_and = process_query(employees, query_conditions, "AND", priority)
    print("Results for AND query:", result_and)
    
    # Process the query using "OR" logic:
    result_or = process_query(employees, query_conditions, "OR", priority)
    print("Results for OR query:", result_or)