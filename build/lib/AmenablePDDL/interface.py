#!/usr/bin/env python3

"""
AmenablePDDL Interface
----------------------

This module provides a high-level interface for loading a PDDL domain and
problem, generating initial states, checking preconditions, binding action
parameters, applying effects, and performing a DFS to find a plan.

This library is designed for professional use, offering a robust interface
for PDDL planning tasks.
"""

from pddl import parse_domain, parse_problem
from pddl.action import Action
from pddl.core import Domain, Problem
from pddl.logic.base import And, Or, Not
from pddl.logic.predicates import Predicate, DerivedPredicate, EqualTo
from pddl.logic.terms import Variable, Constant

from copy import deepcopy
from itertools import product
from typing import Dict, Set, List, Tuple, Optional

class AmenableP:
    """
    A high-level interface for a PDDL domain and problem, providing:
      - Parsing and loading of domain and problem files
      - State representation and manipulation
      - Action parameter binding, precondition checking, and effect application
      - Goal evaluation
      - A demonstration DFS planner
    """

    def __init__(self, domain_file: str, problem_file: str):
        """
        Parse and load the given domain and problem files.
        """
        self.domain_file = domain_file
        self.problem_file = problem_file
        self.domain: Domain = parse_domain(self.domain_file)
        self.problem: Problem = parse_problem(self.problem_file)
        self.initial_state: Set[Predicate] = self._initialize_state(self.problem)
        self.goal_expr = self.problem.goal

    def _initialize_state(self, problem: Problem) -> Set[Predicate]:
        """
        Convert problem.init into a set of ground (positive) Predicates.
        Ignores any Not(...) in the initial state.
        """
        init_state: Set[Predicate] = set()
        for init_el in problem.init:
            if isinstance(init_el, Not):
                continue
            elif isinstance(init_el, Predicate):
                init_state.add(init_el)
        return init_state

    def get_initial_state(self) -> Set[Predicate]:
        """
        Get the set of initial predicates for this problem.
        """
        return self.initial_state

    def is_goal_state(self, state: Set[Predicate]) -> bool:
        """
        Check if 'state' satisfies this problem's goal expression.
        """
        return self._evaluate_condition(self.goal_expr, state, binding={})

    def get_domain_actions(self) -> List[Action]:
        """
        Return a list of the actions defined in the domain.
        """
        return list(self.domain.actions)

    def find_applicable_actions(
        self, state: Set[Predicate]
    ) -> List[Tuple[Action, Dict[Variable, Constant]]]:
        """
        Return a list of (action, binding) pairs applicable in the given state.
        """
        applicable = []
        for action in self.domain.actions:
            bindings_list = self._find_bindings_for_action(action, state)
            for b in bindings_list:
                applicable.append((action, b))
        return applicable

    def apply_action(
        self, action: Action, state: Set[Predicate], binding: Dict[Variable, Constant]
    ) -> Set[Predicate]:
        """
        Produce a new state by applying the action's effects to the given state
        under the specified binding.
        """
        return self._apply_effects(action, state, binding)

    def plan_with_dfs(
        self,
        initial_state: Optional[Set[Predicate]] = None,
        depth_limit: int = 50,
    ) -> Optional[List[Tuple[Action, Dict[Variable, Constant]]]]:
        """
        A simple Depth-First Search planner for the current domain and problem.

        :param initial_state: If None, uses the interface's own initial state.
        :param depth_limit: Maximum depth to search to avoid infinite recursion.
        :return: A plan (list of (action, binding)) if found, or None.
        """
        if initial_state is None:
            initial_state = self.initial_state

        visited_states: Set[frozenset] = set()
        plan = self._dfs(
            state=initial_state,
            plan=[],
            visited=visited_states,
            depth_limit=depth_limit,
        )
        return plan

    def _dfs(
        self,
        state: Set[Predicate],
        plan: List[Tuple[Action, Dict[Variable, Constant]]],
        visited: Set[frozenset],
        depth_limit: int,
    ) -> Optional[List[Tuple[Action, Dict[Variable, Constant]]]]:
        if depth_limit <= 0:
            return None
        if self.is_goal_state(state):
            return plan

        state_key = frozenset(state)
        visited.add(state_key)

        for (action, binding) in self.find_applicable_actions(state):
            new_state = self.apply_action(action, state, binding)
            new_state_key = frozenset(new_state)

            if new_state_key not in visited:
                new_plan = plan + [(action, binding)]
                result = self._dfs(new_state, new_plan, visited, depth_limit - 1)
                if result is not None:
                    return result
        return None

    def _evaluate_condition(
        self,
        expr,
        state: Set[Predicate],
        binding: Dict[Variable, Constant],
    ) -> bool:
        if isinstance(expr, Predicate):
            grounded = self._ground_predicate(expr, binding)
            return grounded in state

        if isinstance(expr, Not):
            return not self._evaluate_condition(expr._arg, state, binding)

        if isinstance(expr, And):
            return all(self._evaluate_condition(subexpr, state, binding) for subexpr in expr.operands)

        if isinstance(expr, Or):
            return any(self._evaluate_condition(subexpr, state, binding) for subexpr in expr.operands)

        if isinstance(expr, DerivedPredicate):
            grounded = self._ground_predicate(expr.predicate, binding)
            return grounded in state

        if isinstance(expr, EqualTo):
            left, right = expr.terms
            left_val = binding[left] if isinstance(left, Variable) else left
            right_val = binding[right] if isinstance(right, Variable) else right
            return left_val == right_val

        return False

    def _check_preconditions(
        self, action: Action, state: Set[Predicate], binding: Dict[Variable, Constant]
    ) -> bool:
        precond_expr = action.precondition
        if precond_expr is None:
            return True
        return self._evaluate_condition(precond_expr, state, binding)

    def _apply_effects(
        self, action: Action, state: Set[Predicate], binding: Dict[Variable, Constant]
    ) -> Set[Predicate]:
        new_state = deepcopy(state)
        eff = action.effect
        if eff is None:
            return new_state

        def add_positive(e) -> None:
            if isinstance(e, Predicate):
                grounded = self._ground_predicate(e, binding)
                new_state.add(grounded)
            elif isinstance(e, Not):
                pass
            elif isinstance(e, And):
                for sub in e.operands:
                    add_positive(sub)
            else:
                pass

        def remove_negative(e) -> None:
            if isinstance(e, Not) and isinstance(e._arg, Predicate):
                grounded = self._ground_predicate(e._arg, binding)
                if grounded in new_state:
                    new_state.remove(grounded)
            elif isinstance(e, And):
                for sub in e.operands:
                    remove_negative(sub)
            else:
                pass

        if hasattr(eff, "positive") and hasattr(eff, "negated"):
            for pos_eff in eff.positive:
                add_positive(pos_eff)
            for neg_eff in eff.negated:
                remove_negative(neg_eff)
        else:
            if isinstance(eff, And):
                for subeff in eff.operands:
                    if isinstance(subeff, Not):
                        remove_negative(subeff)
                    else:
                        add_positive(subeff)
            elif isinstance(eff, Not):
                remove_negative(eff)
            else:
                add_positive(eff)

        return new_state

    def _get_object_candidates(self, param: Variable) -> Set[Constant]:
        all_objects = set(self.problem.objects) | set(self.domain.constants)
        if not param.type_tags:
            return all_objects

        candidates = set()
        for obj in all_objects:
            if obj.type_tag in param.type_tags:
                candidates.add(obj)
        return candidates

    def _find_bindings_for_action(
        self, action: Action, state: Set[Predicate]
    ) -> List[Dict[Variable, Constant]]:
        param_domains: List[Tuple[Variable, List[Constant]]] = []
        for param in action.parameters:
            candidates = self._get_object_candidates(param)
            param_domains.append((param, list(candidates)))

        from itertools import product
        param_vars = [p for (p, _) in param_domains]
        param_candidates_list = [cands for (_, cands) in param_domains]

        all_bindings: List[Dict[Variable, Constant]] = []

        for combo in product(*param_candidates_list):
            binding: Dict[Variable, Constant] = {}
            for pv, obj in zip(param_vars, combo):
                binding[pv] = obj

            if self._check_preconditions(action, state, binding):
                all_bindings.append(binding)

        return all_bindings

    def _ground_predicate(
        self, pred: Predicate, binding: Dict[Variable, Constant]
    ) -> Predicate:
        grounded_terms = []
        for term in pred.terms:
            if isinstance(term, Variable):
                grounded_terms.append(binding[term])
            else:
                grounded_terms.append(term)
        return Predicate(pred.name, *grounded_terms)

if __name__ == "__main__":
    domain_file = "scotty_domain.pddl"
    problem_file = "scotty_problem.pddl"

    interface = AmenablePDDL(domain_file, problem_file)

    init_state = interface.get_initial_state()
    print("\nInitial State:")
    for pred in init_state:
        print("  ", pred)

    print("\nActions:")
    for act in interface.get_domain_actions():
        print("  ", act.name, " parameters=", [v.name for v in act.parameters])

    print("\nRunning DFS plan search...")
    plan = interface.plan_with_dfs(depth_limit=50)
    if plan is None:
        print("No plan found.")
    else:
        print("Plan found:")
        for i, (action, binding) in enumerate(plan, start=1):
            bound_str = " ".join(str(binding[p]) for p in action.parameters)
            print(f"{i}: {action.name} {bound_str}")
