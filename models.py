# models.py
from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property,
    StringType, IntegerType, BooleanType, Multiplicity,
    BinaryAssociation, Constraint
)


# 1(Load Balancing)
lb_problem = Class(name="LoadBalancingProblem")
job = Class(name="Job")
machine = Class(name="Machine")

# Attributes 
lb_problem.add_attribute(Property(name="name", type=StringType))
lb_problem.add_attribute(Property(name="balanced", type=BooleanType, is_optional=True))
lb_problem.add_attribute(Property(name="assigned", type=BooleanType, is_optional=True))

job.add_attribute(Property(name="id", type=StringType))
job.add_attribute(Property(name="load", type=IntegerType))

machine.add_attribute(Property(name="name", type=StringType))
machine.add_attribute(Property(name="total_load", type=IntegerType, is_derived=True))

# Associations
lb_has_jobs = BinaryAssociation(
    name="lb_has_jobs",
    ends={
        Property(name="problem", type=lb_problem, multiplicity=Multiplicity(1, 1), is_composite=True),
        Property(name="jobs", type=job, multiplicity=Multiplicity(2, "*"))
    }
)

lb_has_machines = BinaryAssociation(
    name="lb_has_machines",
    ends={
        Property(name="problem", type=lb_problem, multiplicity=Multiplicity(1, 1), is_composite=True),
        Property(name="machines", type=machine, multiplicity=Multiplicity(2, 2))
    }
)

# Result mapping for part II
job_assigned_machine = BinaryAssociation(
    name="job_assigned_machine",
    ends={
        Property(name="assigned_jobs", type=job, multiplicity=Multiplicity(0, "*")),
        Property(name="assigned_machine", type=machine, multiplicity=Multiplicity(0, 1))
    }
)

# OCL constraints
ocl_positive_load = Constraint(
    name="PositiveJobLoad",
    context=job,
    expression="self.load > 0",
    language="OCL"
)

ocl_unique_job_id = Constraint(
    name="UniqueJobIDs",
    context=lb_problem,
    expression="self.jobs->isUnique(j | j.id)",
    language="OCL"
)

ocl_exactly_two_machines = Constraint(
    name="ExactlyTwoMachines",
    context=lb_problem,
    expression="self.machines->size() == 2",
    language="OCL"
)

# DomainModel Initialization
problem_model = DomainModel(
    name="LoadBalancingProblemDSL",
    types={lb_problem, job, machine},
    associations={lb_has_jobs, lb_has_machines, job_assigned_machine},
    constraints={ocl_positive_load, ocl_unique_job_id, ocl_exactly_two_machines}
)