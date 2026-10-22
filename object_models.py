# object_models.py
from models import (
    lb_problem, job, machine,
    lb_has_jobs, lb_has_machines
)
from models_solution import (
    lac_problem, constraint, term, decision_var,
    lac_has_constraints, lac_has_variables, constraint_has_terms, term_ref_var
)
from besser.BUML.metamodel.object import Object, Link, ObjectModel

# 1. PROBLEM OBJECT MODEL
lb_obj = Object(name="lb_instance", classifier=lb_problem)
m1_obj = Object(name="m1", classifier=machine)
m2_obj = Object(name="m2", classifier=machine)

j1_obj = Object(name="j1", classifier=job)
j2_obj = Object(name="j2", classifier=job)
j3_obj = Object(name="j3", classifier=job)
j4_obj = Object(name="j4", classifier=job)

# Set attribute values
j1_obj.set_value(property_name="weight", value=2)
j2_obj.set_value(property_name="weight", value=3)
j3_obj.set_value(property_name="weight", value=5)
j4_obj.set_value(property_name="weight", value=6)

problem_object_model = ObjectModel(
    name="LoadBalancingProblemInstance",
    instances={lb_obj, m1_obj, m2_obj, j1_obj, j2_obj, j3_obj, j4_obj}
)

    # 2. SOLUTION OBJECT MODEL (Linear Constraints)
lac_obj = Object(name="lac_instance", classifier=lac_problem)

# Decision Variables y1..y4
y1_obj = Object(name="y1", classifier=decision_var)
y1_obj.set_value(property_name="name", value="y1")

y2_obj = Object(name="y2", classifier=decision_var)
y2_obj.set_value(property_name="name", value="y2")

y3_obj = Object(name="y3", classifier=decision_var)
y3_obj.set_value(property_name="name", value="y3")

y4_obj = Object(name="y4", classifier=decision_var)
y4_obj.set_value(property_name="name", value="y4")

# Constraint: 2*y1 + 3*y2 + 5*y3 + 6*y4 - 8 = 0
c1_obj = Object(name="c1", classifier=constraint)
c1_obj.set_value(property_name="const", value=-8)
c1_obj.set_value(property_name="oper", value="=")

# Terms
t1_obj = Object(name="t1", classifier=term)
t1_obj.set_value(property_name="coef", value=2)

t2_obj = Object(name="t2", classifier=term)
t2_obj.set_value(property_name="coef", value=3)

t3_obj = Object(name="t3", classifier=term)
t3_obj.set_value(property_name="coef", value=5)

t4_obj = Object(name="t4", classifier=term)
t4_obj.set_value(property_name="coef", value=6)

solution_object_model = ObjectModel(
    name="LACProblemInstance",
    instances={lac_obj, c1_obj, y1_obj, y2_obj, y3_obj, y4_obj, t1_obj, t2_obj, t3_obj, t4_obj}
)

print("Object models successfully constructed.")