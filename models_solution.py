# models_solution.py
from besser.BUML.metamodel.structural import (
    DomainModel, Class, Property,
    StringType, IntegerType, Multiplicity,
    BinaryAssociation
)

# 2. SOLUTION DSL (Linear Arithmetic Constraints)
lac_problem = Class(name="LACProblem")
constraint = Class(name="Constraint")
term = Class(name="Term")
decision_var = Class(name="DecisionVariable")

# Attributes
constraint.add_attribute(Property(name="const", type=IntegerType))
constraint.add_attribute(Property(name="oper", type=StringType))

term.add_attribute(Property(name="coef", type=IntegerType))

decision_var.add_attribute(Property(name="name", type=StringType))
decision_var.add_attribute(Property(name="value", type=IntegerType, is_optional=True))

# Associations
lac_has_constraints = BinaryAssociation(
    name="lac_has_constraints",
    ends={
        Property(name="lac_problem", type=lac_problem, multiplicity=Multiplicity(0, 1), is_composite=True),
        Property(name="constraints", type=constraint, multiplicity=Multiplicity(0, "*"))
    }
)

lac_has_variables = BinaryAssociation(
    name="lac_has_variables",
    ends={
        Property(name="lac_problem", type=lac_problem, multiplicity=Multiplicity(0, 1), is_composite=True),
        Property(name="variables", type=decision_var, multiplicity=Multiplicity(0, "*"))
    }
)

constraint_has_terms = BinaryAssociation(
    name="constraint_has_terms",
    ends={
        Property(name="constraint", type=constraint, multiplicity=Multiplicity(0, 1), is_composite=True),
        Property(name="terms", type=term, multiplicity=Multiplicity(0, "*"))
    }
)

term_ref_var = BinaryAssociation(
    name="term_ref_var",
    ends={
        Property(name="terms", type=term, multiplicity=Multiplicity(0, "*")),
        Property(name="variable", type=decision_var, multiplicity=Multiplicity(1, 1))
    }
)

lac_model = DomainModel(
    name="LACProblemDSL",
    types={lac_problem, constraint, term, decision_var},
    associations={lac_has_constraints, lac_has_variables, constraint_has_terms, term_ref_var}
)