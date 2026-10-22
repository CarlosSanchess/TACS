from models_solution import (
    lac_problem, constraint, term, decision_var,
    lac_has_constraints, lac_has_variables, constraint_has_terms, term_ref_var,
    lac_model
)
from besser.BUML.metamodel.object import Object, Link, LinkEnd, ObjectModel

# Create Objects
lac_obj = Object(name="lac_instance", classifier=lac_problem)

# Decision Variables y1..y4
y1_obj = Object(name="y1", classifier=decision_var)
y1_obj.name = "y1"
y1_obj.bitWidth = 1

y2_obj = Object(name="y2", classifier=decision_var)
y2_obj.name = "y2"
y2_obj.bitWidth = 1

y3_obj = Object(name="y3", classifier=decision_var)
y3_obj.name = "y3"
y3_obj.bitWidth = 1

y4_obj = Object(name="y4", classifier=decision_var)
y4_obj.name = "y4"
y4_obj.bitWidth = 1

# Terms
t1_obj = Object(name="t1", classifier=term)
t1_obj.coef = 2

t2_obj = Object(name="t2", classifier=term)
t2_obj.coef = 3

t3_obj = Object(name="t3", classifier=term)
t3_obj.coef = 5

t4_obj = Object(name="t4", classifier=term)
t4_obj.coef = 6

# Constraint Atom: 2y1 + 3y2 + 5y3 + 6y4 - 8 == 0
c1_obj = Object(name="c1", classifier=constraint)
c1_obj.const = -8
c1_obj.oper = "=="

# Define Links
links_solution = {
    # System -> Variables
    Link(name="link_lac_y1", association=lac_has_variables, connections=[
        LinkEnd(name="lac_problem", object=lac_obj), LinkEnd(name="variables", object=y1_obj)
    ]),
    Link(name="link_lac_y2", association=lac_has_variables, connections=[
        LinkEnd(name="lac_problem", object=lac_obj), LinkEnd(name="variables", object=y2_obj)
    ]),
    Link(name="link_lac_y3", association=lac_has_variables, connections=[
        LinkEnd(name="lac_problem", object=lac_obj), LinkEnd(name="variables", object=y3_obj)
    ]),
    Link(name="link_lac_y4", association=lac_has_variables, connections=[
        LinkEnd(name="lac_problem", object=lac_obj), LinkEnd(name="variables", object=y4_obj)
    ]),
    # System -> Constraint
    Link(name="link_lac_c1", association=lac_has_constraints, connections=[
        LinkEnd(name="lac_problem", object=lac_obj), LinkEnd(name="constraints", object=c1_obj)
    ]),
    # Constraint -> Terms
    Link(name="link_c1_t1", association=constraint_has_terms, connections=[
        LinkEnd(name="constraint", object=c1_obj), LinkEnd(name="terms", object=t1_obj)
    ]),
    Link(name="link_c1_t2", association=constraint_has_terms, connections=[
        LinkEnd(name="constraint", object=c1_obj), LinkEnd(name="terms", object=t2_obj)
    ]),
    Link(name="link_c1_t3", association=constraint_has_terms, connections=[
        LinkEnd(name="constraint", object=c1_obj), LinkEnd(name="terms", object=t3_obj)
    ]),
    Link(name="link_c1_t4", association=constraint_has_terms, connections=[
        LinkEnd(name="constraint", object=c1_obj), LinkEnd(name="terms", object=t4_obj)
    ]),
    # Terms -> Decision Variables
    Link(name="link_t1_y1", association=term_ref_var, connections=[
        LinkEnd(name="terms", object=t1_obj), LinkEnd(name="variable", object=y1_obj)
    ]),
    Link(name="link_t2_y2", association=term_ref_var, connections=[
        LinkEnd(name="terms", object=t2_obj), LinkEnd(name="variable", object=y2_obj)
    ]),
    Link(name="link_t3_y3", association=term_ref_var, connections=[
        LinkEnd(name="terms", object=t3_obj), LinkEnd(name="variable", object=y3_obj)
    ]),
    Link(name="link_t4_y4", association=term_ref_var, connections=[
        LinkEnd(name="terms", object=t4_obj), LinkEnd(name="variable", object=y4_obj)
    ]),
}

# Construct Object Model Instance
solution_instance = ObjectModel(
    name="LACProblemInstance",
    instances={lac_obj, c1_obj, y1_obj, y2_obj, y3_obj, y4_obj, t1_obj, t2_obj, t3_obj, t4_obj},
    links=links_solution
)

if __name__ == "__main__":
    print(f"Solution Instance created: {len(solution_instance.instances)} objects, {len(solution_instance.links)} links.")