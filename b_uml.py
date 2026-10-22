from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property,
    StringType, IntegerType, BooleanType, Multiplicity,
    BinaryAssociation
)

# Tipos de dados primitivos
str_type = StringType()
int_type = IntegerType()
bool_type = BooleanType()

problem_model = DomainModel(name="LoadBalancingProblemDSL")

# Definição das classes
lb_problem = Class(name="LoadBalancingProblem")
job = Class(name="Job")
machine = Class(name="Machine")

# Atributos
lb_problem.add_attribute(Property(name="balanced", type=bool_type, is_optional=True))
lb_problem.add_attribute(Property(name="assigned", type=bool_type, is_optional=True))

job.add_attribute(Property(name="weight", type=int_type))

# Atributo derivado /load
machine.add_attribute(Property(name="load", type=int_type, is_derived=True))

# Associações
# LoadBalancingProblem (1) <*>---> (*) Job
lb_has_jobs = BinaryAssociation(
    name="lb_has_jobs",
    ends={
        Property(name="problem", type=lb_problem, multiplicity=Multiplicity(0, 1), is_composite=True),
        Property(name="jobs", type=job, multiplicity=Multiplicity(0, "*"))
    }
)

# LoadBalancingProblem (1) <*>---> (*) Machine
lb_has_machines = BinaryAssociation(
    name="lb_has_machines",
    ends={
        Property(name="problem", type=lb_problem, multiplicity=Multiplicity(0, 1), is_composite=True),
        Property(name="machines", type=machine, multiplicity=Multiplicity(0, "*"))
    }
)

# Job (*) <---> (0..1) Machine
job_assigned_machine = BinaryAssociation(
    name="job_assigned_machine",
    ends={
        Property(name="assigned_jobs", type=job, multiplicity=Multiplicity(0, "*")),
        Property(name="assigned_machine", type=machine, multiplicity=Multiplicity(0, 1))
    }
)

problem_model.add_classes({lb_problem, job, machine})
problem_model.add_associations({lb_has_jobs, lb_has_machines, job_assigned_machine})

