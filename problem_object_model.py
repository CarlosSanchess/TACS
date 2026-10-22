from models import (
    lb_problem, job, machine,
    lb_has_jobs, lb_has_machines,
    problem_model
)
from besser.BUML.metamodel.object import Object, Link, LinkEnd, ObjectModel

# Create Objects
lb_obj = Object(name="LoadBalancing_4Jobs", classifier=lb_problem)
lb_obj.name = "LoadBalancing_4Jobs"

m1_obj = Object(name="Machine_1", classifier=machine)
m1_obj.name = "Machine_1"

m2_obj = Object(name="Machine_2", classifier=machine)
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

# Define Links
links_problem = {
    Link(name="link_lb_m1", association=lb_has_machines, connections=[
        LinkEnd(name="problem", object=lb_obj), LinkEnd(name="machines", object=m1_obj)
    ]),
    Link(name="link_lb_m2", association=lb_has_machines, connections=[
        LinkEnd(name="problem", object=lb_obj), LinkEnd(name="machines", object=m2_obj)
    ]),
    Link(name="link_lb_j1", association=lb_has_jobs, connections=[
        LinkEnd(name="problem", object=lb_obj), LinkEnd(name="jobs", object=j1_obj)
    ]),
    Link(name="link_lb_j2", association=lb_has_jobs, connections=[
        LinkEnd(name="problem", object=lb_obj), LinkEnd(name="jobs", object=j2_obj)
    ]),
    Link(name="link_lb_j3", association=lb_has_jobs, connections=[
        LinkEnd(name="problem", object=lb_obj), LinkEnd(name="jobs", object=j3_obj)
    ]),
    Link(name="link_lb_j4", association=lb_has_jobs, connections=[
        LinkEnd(name="problem", object=lb_obj), LinkEnd(name="jobs", object=j4_obj)
    ]),
}

# Construct Object Model Instance
problem_instance = ObjectModel(
    name="LoadBalancingProblemInstance",
    instances={lb_obj, m1_obj, m2_obj, j1_obj, j2_obj, j3_obj, j4_obj},
    links=links_problem
)

if __name__ == "__main__":
    print(f"Problem Instance created: {len(problem_instance.instances)} objects, {len(problem_instance.links)} links.")


    models = [problem_model]