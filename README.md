# AmenablePDDL

AmenablePDDL is designed to simplify parsing and planning simple PDDL-defined domains and problems, providing an intuitive interface for implementing common planning algorithms. AmenablePDDL is a wrapper around the PDDL library by Marco Favorito, Francesco Fuggitti, and Christian Muise. 

This interface was developed for Carnegie Mellon University's 16-280 Intelligent Robotic Systems. 

## Table of Contents
- [Installation](#installation)
- [Overview](#overview)
- [Quick Start Example](#quick-start-example)
- [Public Methods](#public-methods)
  - [Constructor](#constructor)
  - [Domain and Problem Access](#domain-and-problem-access)
  - [State and Goal](#state-and-goal)
  - [Action Retrieval](#action-retrieval)
  - [Action Applicability and Application](#action-applicability-and-application)
- [Implementing DFS (Example)](#implementing-dfs-example)
- [Internal Methods (Optional)](#internal-methods-optional)
- [License](#license)

---

## Installation

AmenablePDDL is available through pip. Install it on your machine by running:
```bash
pip install AmenablePDDL
```

---

## Quick Start Example

```python
from AmenablePDDL import AmenableP

# Initialize the interface with domain and problem files
interface = AmenableP("domain.pddl", "problem.pddl")

# Retrieve initial state and available actions
the_initial_state = interface.get_initial_state()
actions = interface.get_domain_actions()

print("Initial State:", the_initial_state)
print("Available Actions:", [action.name for action in actions])
```

This example initializes the AmenablePDDL interface, loads the domain and problem files, and prints out the initial state and available actions.

---

## Public Methods

### Constructor

```python
interface = AmenableP(domain_file, problem_file)
```
- **domain_file**: Path to the PDDL domain file.
- **problem_file**: Path to the PDDL problem file.

### Domain and Problem Access

- `get_domain_actions() -> List[Action]`: Returns a list of `Action` objects defined in the domain.

### State and Goal

- `get_initial_state() -> Set[Predicate]`: Returns the set of positive predicates of the initial state.
- `is_goal_state(state: Set[Predicate]) -> bool`: Checks if a given state satisfies the goal expression.

### Action Retrieval

- `find_applicable_actions(state: Set[Predicate]) -> List[Tuple[Action, Dict[Variable, Constant]]]`: Returns applicable actions with valid bindings in the given state.

### Action Application

- `apply_action(action: Action, state: Set[Predicate], binding: Dict[Variable, Constant]) -> Set[Predicate]`: Applies the specified action with the given binding to the state, returning a new state.

---

## Implementing DFS (Example)

Below is an example of how to implement a Depth-First Search (DFS) planner using AmenablePDDL.

```python
from AmenablePDDL import AmenableP

# Initialize the interface
interface = AmenableP("domain.pddl", "problem.pddl")

# Define a simple DFS function

def dfs(state, plan, visited, depth_limit):
    if depth_limit <= 0:
        return None
    if interface.is_goal_state(state):
        return plan

    visited.add(frozenset(state))

    for action, binding in interface.find_applicable_actions(state):
        new_state = interface.apply_action(action, state, binding)
        state_key = frozenset(new_state)

        if state_key not in visited:
            new_plan = plan + [(action, binding)]
            result = dfs(new_state, new_plan, visited, depth_limit - 1)
            if result is not None:
                return result
    return None

# Run DFS starting from the initial state
visited_states = set()
plan = dfs(interface.get_initial_state(), [], visited_states, depth_limit=50)

if plan:
    print("Plan found:")
    for step, (action, binding) in enumerate(plan, start=1):
        bound_str = " ".join(str(binding[param]) for param in action.parameters)
        print(f"{step}: {action.name} {bound_str}")
else:
    print("No plan found.")
```

This script initializes the AmenablePDDL interface, defines a recursive DFS function leveraging the interface's methods to find applicable actions and apply them, and then searches for a plan with a given depth limit.

---

## Internal Methods (Optional)

AmenablePDDL also provides internal methods for advanced usage:
- `_evaluate_condition(expr, state, binding)`
- `_find_bindings_for_action(action, state)`
- `_apply_effects(action, state, binding)`
- `_ground_predicate(pred, binding)`

These methods are used internally by the public methods, but users can extend the existing methods by forking the repository. 

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


