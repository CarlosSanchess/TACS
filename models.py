# models.py
from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property,
    StringType, IntegerType, BooleanType, Multiplicity,
    BinaryAssociation
)


# 1(Load Balancing)
lb_problem = Class(name="LoadBalancingProblem")
job = Class(name="Job")
machine = Class(name="Machine")

# Attributes (Note: StringType, IntegerType, BooleanType are passed directly without parentheses)
lb_problem.add_attribute(Property(name="balanced", type=BooleanType, is_optional=True))
lb_problem.add_attribute(Property(name="assigned", type=BooleanType, is_optional=True))

job.add_attribute(Property(name="weight", type=IntegerType))
machine.add_attribute(Property(name="load", type=IntegerType, is_derived=True))

# Associations
lb_has_jobs = BinaryAssociation(
    name="lb_has_jobs",
    ends={
        Property(name="problem", type=lb_problem, multiplicity=Multiplicity(0, 1), is_composite=True),
        Property(name="jobs", type=job, multiplicity=Multiplicity(0, "*"))
    }
)

lb_has_machines = BinaryAssociation(
    name="lb_has_machines",
    ends={
        Property(name="problem", type=lb_problem, multiplicity=Multiplicity(0, 1), is_composite=True),
        Property(name="machines", type=machine, multiplicity=Multiplicity(0, "*"))
    }
)

job_assigned_machine = BinaryAssociation(
    name="job_assigned_machine",
    ends={
        Property(name="assigned_jobs", type=job, multiplicity=Multiplicity(0, "*")),
        Property(name="assigned_machine", type=machine, multiplicity=Multiplicity(0, 1))
    }
)

# DomainModel Initialization
problem_model = DomainModel(
    name="LoadBalancingProblemDSL",
    types={lb_problem, job, machine},
    associations={lb_has_jobs, lb_has_machines, job_assigned_machine}
)