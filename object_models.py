# object_models.py
from models import (
    lb_problem, job, machine,
    lb_has_jobs, lb_has_machines
)
from models_solution import (
    lac_problem, constraint, term, decision_var,
    lac_has_constraints, lac_has_variables, constraint_has_terms, term_ref_var
)
from besser.BUML.metamodel.object import Object, Link, LinkEnd, ObjectModel

# 1. PROBLEM OBJECT MODEL
lb_obj = Object(name="lb_instance", classifier=lb_problem)
lb_obj.name = "LoadBalancing_4Jobs"

m1_obj = Object(name="m1", classifier=machine)
m1_obj.name = "Machine_1"

m2_obj = Object(name="m2", classifier=machine)
m2_obj.name = "Machine_2"

j1_obj = Object(name="j1", classifier=job)
j1_obj.id = "j1"
j1_obj.load = 2

j2_obj = Object(name="j2", classifier=job)
j2_obj.id = "j2"
j2_obj.load = 3

j3_obj = Object(name="j3", classifier=job)
j3_obj.id = "j3"
j3_obj.load = 5

j4_obj = Object(name="j4", classifier=job)
j4_obj.id = "j4"
j4_obj.load = 6

# Create Links (Connecting Objects)
links_problem = {
    # Connect Problem -> Machines
    Link(name="link_lb_m1", association=lb_has_machines, connections=[
        LinkEnd(name="machine_problem", object=lb_obj), LinkEnd(name="machines", object=m1_obj)
    ]),
    Link(name="link_lb_m2", association=lb_has_machines, connections=[
        LinkEnd(name="machine_problem", object=lb_obj), LinkEnd(name="machines", object=m2_obj)
    ]),
    # Connect Problem -> Jobs
    Link(name="link_lb_j1", association=lb_has_jobs, connections=[
        LinkEnd(name="job_problem", object=lb_obj), LinkEnd(name="jobs", object=j1_obj)
    ]),
    Link(name="link_lb_j2", association=lb_has_jobs, connections=[
        LinkEnd(name="job_problem", object=lb_obj), LinkEnd(name="jobs", object=j2_obj)
    ]),
    Link(name="link_lb_j3", association=lb_has_jobs, connections=[
        LinkEnd(name="job_problem", object=lb_obj), LinkEnd(name="jobs", object=j3_obj)
    ]),
    Link(name="link_lb_j4", association=lb_has_jobs, connections=[
        LinkEnd(name="job_problem", object=lb_obj), LinkEnd(name="jobs", object=j4_obj)
    ])
}

problem_object_model = ObjectModel(
    name="LoadBalancingProblemInstance",
    instances={lb_obj, m1_obj, m2_obj, j1_obj, j2_obj, j3_obj, j4_obj},
    links=links_problem
)

# 2. SOLUTION OBJECT MODEL (Linear Constraints)
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

# Linear Terms (coef * variable)
t1_obj = Object(name="t1", classifier=term)
t1_obj.coef = 2

t2_obj = Object(name="t2", classifier=term)
t2_obj.coef = 3

t3_obj = Object(name="t3", classifier=term)
t3_obj.coef = 5

t4_obj = Object(name="t4", classifier=term)
t4_obj.coef = 6

# Constraint Atom: sum(terms) - 8 == 0
c1_obj = Object(name="c1", classifier=constraint)
c1_obj.const = -8
c1_obj.oper = "=="

# Create Solution Links
links_solution = {
    # System -> Variables
    Link(name="link_lac_y1", association=lac_has_variables, connections=[
        LinkEnd(name="variable_problem", object=lac_obj), LinkEnd(name="variables", object=y1_obj)
    ]),
    Link(name="link_lac_y2", association=lac_has_variables, connections=[
        LinkEnd(name="variable_problem", object=lac_obj), LinkEnd(name="variables", object=y2_obj)
    ]),
    Link(name="link_lac_y3", association=lac_has_variables, connections=[
        LinkEnd(name="variable_problem", object=lac_obj), LinkEnd(name="variables", object=y3_obj)
    ]),
    Link(name="link_lac_y4", association=lac_has_variables, connections=[
        LinkEnd(name="variable_problem", object=lac_obj), LinkEnd(name="variables", object=y4_obj)
    ]),
    # System -> Constraint
    Link(name="link_lac_c1", association=lac_has_constraints, connections=[
        LinkEnd(name="constraint_problem", object=lac_obj), LinkEnd(name="constraints", object=c1_obj)
    ]),
    # Constraint -> Terms
    Link(name="link_c1_t1", association=constraint_has_terms, connections=[
        LinkEnd(name="parent_constraint", object=c1_obj), LinkEnd(name="terms", object=t1_obj)
    ]),
    Link(name="link_c1_t2", association=constraint_has_terms, connections=[
        LinkEnd(name="parent_constraint", object=c1_obj), LinkEnd(name="terms", object=t2_obj)
    ]),
    Link(name="link_c1_t3", association=constraint_has_terms, connections=[
        LinkEnd(name="parent_constraint", object=c1_obj), LinkEnd(name="terms", object=t3_obj)
    ]),
    Link(name="link_c1_t4", association=constraint_has_terms, connections=[
        LinkEnd(name="parent_constraint", object=c1_obj), LinkEnd(name="terms", object=t4_obj)
    ]),
    # Terms -> Decision Variables
    Link(name="link_t1_y1", association=term_ref_var, connections=[
        LinkEnd(name="referencing_terms", object=t1_obj), LinkEnd(name="variable", object=y1_obj)
    ]),
    Link(name="link_t2_y2", association=term_ref_var, connections=[
        LinkEnd(name="referencing_terms", object=t2_obj), LinkEnd(name="variable", object=y2_obj)
    ]),
    Link(name="link_t3_y3", association=term_ref_var, connections=[
        LinkEnd(name="referencing_terms", object=t3_obj), LinkEnd(name="variable", object=y3_obj)
    ]),
    Link(name="link_t4_y4", association=term_ref_var, connections=[
        LinkEnd(name="referencing_terms", object=t4_obj), LinkEnd(name="variable", object=y4_obj)
    ]),
}

solution_object_model = ObjectModel(
    name="LACProblemInstance",
    instances={lac_obj, c1_obj, y1_obj, y2_obj, y3_obj, y4_obj, t1_obj, t2_obj, t3_obj, t4_obj},
    links=links_solution
)

if __name__ == "__main__":
    print("Problem Object Model instances:", len(problem_object_model.instances), "links:", len(problem_object_model.links))
    print("Solution Object Model instances:", len(solution_object_model.instances), "links:", len(solution_object_model.links))