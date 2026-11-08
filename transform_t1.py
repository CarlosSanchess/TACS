from besser.BUML.metamodel.object import Object, Link, LinkEnd, ObjectModel

from problem_object_model import problem_instance
from models import (
    lb_problem,
    job,
    machine,
    lb_has_jobs
)

from models_solution import (
    lac_problem,
    constraint,
    term,
    decision_var,
    lac_has_constraints,
    lac_has_variables,
    constraint_has_terms,
    term_ref_var
)


def get_job_id(job_obj):
    for slot in job_obj.slots:
        if slot.attribute.name == "id":
            return slot.value.value
    return job_obj.name


def transform_t1(source_model):
    """
    Transform a LoadBalancingProblem ObjectModel into a
    Linear Arithmetic Constraints (LAC) ObjectModel.

    For each job i:
        - Create one binary decision variable y_i.
        - Create one term with coefficient 2 * job.load.

    Create the constraint:

        2 * sum(job.load * y_i) - total_load == 0

    This is equivalent to requiring equal loads on two machines.
    """

    # STEP 1: Find the problem object

    problem_objects = [
        obj for obj in source_model.instances
        if obj.classifier == lb_problem
    ]

    if len(problem_objects) != 1:
        raise ValueError(
            "Expected exactly one LoadBalancingProblem."
        )

    source_problem = problem_objects[0]

    # STEP 2: Find the machines

    machines = [
        obj for obj in source_model.instances
        if obj.classifier == machine
    ]

    if len(machines) != 2:
        raise ValueError(
            "A load-balancing problem must have exactly two machines."
        )

    # STEP 3: Find jobs through their association

    jobs = []

    for link in source_model.links:

        if link.association == lb_has_jobs:

            problem_end = next(
                c.object for c in link.connections
                if c.name == "problem"
            )

            if problem_end == source_problem:

                job_end = next(
                    c.object for c in link.connections
                    if c.name == "jobs"
                )

                jobs.append(job_end)

    if len(jobs) < 2:
        raise ValueError(
            "A load-balancing problem must contain at least two jobs."
        )

    # STEP 4: Validate the jobs

    jobs.sort(key=get_job_id)

    job_ids = [get_job_id(j) for j in jobs]

    if len(job_ids) != len(set(job_ids)):
        raise ValueError("Job IDs must be unique.")

    for j in jobs:

        if j.load <= 0:
            raise ValueError(
                f"Job {get_job_id(j)} must have a positive load."
            )

    # STEP 5: Calculate total workload

    total_load = sum(j.load for j in jobs)

    print(f"Number of jobs: {len(jobs)}")
    print(f"Total workload: {total_load}")

    # STEP 6: Create the main LAC problem object

    lac_obj = Object(
        name="LAC_LoadBalancing",
        classifier=lac_problem
    )

    instances = {lac_obj}
    links = set()

    variables = {}
    terms = {}

    # End definitions for solution associations
    lac_var_prob_end = next(e for e in lac_has_variables.ends if e.name == "lac_problem")
    lac_var_vars_end = next(e for e in lac_has_variables.ends if e.name == "variables")
    lac_const_prob_end = next(e for e in lac_has_constraints.ends if e.name == "lac_problem")
    lac_const_const_end = next(e for e in lac_has_constraints.ends if e.name == "constraints")
    const_terms_c_end = next(e for e in constraint_has_terms.ends if e.name == "constraint")
    const_terms_t_end = next(e for e in constraint_has_terms.ends if e.name == "terms")
    term_ref_t_end = next(e for e in term_ref_var.ends if e.name == "terms")
    term_ref_v_end = next(e for e in term_ref_var.ends if e.name == "variable")

    # STEP 7: Create one decision variable per job

    for j in jobs:
        j_id = get_job_id(j)
        variable = Object(
            name=f"y_{j_id}",
            classifier=decision_var
        )

        variable.name = f"y_{j_id}"
        variable.bitWidth = 1

        variables[j_id] = variable
        instances.add(variable)

        links.add(
            Link(
                name=f"link_lac_{j_id}",
                association=lac_has_variables,
                connections=[
                    LinkEnd(
                        name="lac_problem",
                        association_end=lac_var_prob_end,
                        object=lac_obj
                    ),
                    LinkEnd(
                        name="variables",
                        association_end=lac_var_vars_end,
                        object=variable
                    )
                ]
            )
        )

    # STEP 8: Create one term per job

    for j in jobs:
        j_id = get_job_id(j)
        term_obj = Object(
            name=f"term_{j_id}",
            classifier=term
        )

        term_obj.coef = 2 * j.load

        terms[j_id] = term_obj
        instances.add(term_obj)

    # STEP 9: Create the equality constraint

    constraint_obj = Object(
        name="equal_machine_loads",
        classifier=constraint
    )

    constraint_obj.const = -total_load
    constraint_obj.oper = "=="

    instances.add(constraint_obj)

    links.add(
        Link(
            name="link_lac_constraint",
            association=lac_has_constraints,
            connections=[
                LinkEnd(
                    name="lac_problem",
                    association_end=lac_const_prob_end,
                    object=lac_obj
                ),
                LinkEnd(
                    name="constraints",
                    association_end=lac_const_const_end,
                    object=constraint_obj
                )
            ]
        )
    )

    
    # STEP 10: Connect constraint -> terms -> decision variables

    for j in jobs:
        j_id = get_job_id(j)
        term_obj = terms[j_id]
        variable = variables[j_id]

        links.add(
            Link(
                name=f"link_constraint_{j_id}",
                association=constraint_has_terms,
                connections=[
                    LinkEnd(
                        name="constraint",
                        association_end=const_terms_c_end,
                        object=constraint_obj
                    ),
                    LinkEnd(
                        name="terms",
                        association_end=const_terms_t_end,
                        object=term_obj
                    )
                ]
            )
        )

        links.add(
            Link(
                name=f"link_term_{j_id}",
                association=term_ref_var,
                connections=[
                    LinkEnd(
                        name="terms",
                        association_end=term_ref_t_end,
                        object=term_obj
                    ),
                    LinkEnd(
                        name="variable",
                        association_end=term_ref_v_end,
                        object=variable
                    )
                ]
            )
        )

    # STEP 11: Build the output LAC object model

    solution_model = ObjectModel(
        name="Generated_LAC_Model",
        objects=instances
    )

    return solution_model

# Inspection function

def inspect_lac_model(model):
    """Print the contents and relationships of a generated LAC model."""

    from models_solution import (
        lac_problem,
        decision_var,
        constraint,
        term,
        lac_has_variables,
        lac_has_constraints,
        constraint_has_terms,
        term_ref_var,
    )

    def get_connected_object(link, end_name):
        """Find the object connected at a named association end."""
        for connection in link.connections:
            if connection.name == end_name:
                return connection.object
        return None

    # 1. Identify objects by their classifiers
    lac_objects = [
        obj for obj in model.instances
        if obj.classifier == lac_problem
    ]

    variables = [
        obj for obj in model.instances
        if obj.classifier == decision_var
    ]

    constraints = [
        obj for obj in model.instances
        if obj.classifier == constraint
    ]

    terms = [
        obj for obj in model.instances
        if obj.classifier == term
    ]

    print("\n========== LAC MODEL INSPECTION ==========")

    print(f"\nTotal objects: {len(model.instances)}")
    print(f"Total links: {len(model.links)}")

    print("\n1. LAC PROBLEM")
    for obj in lac_objects:
        print(f"   Name: {obj.name}")

    # 2. Display decision variables
    print("\n2. DECISION VARIABLES")

    variables.sort(key=lambda v: v.name)

    for variable in variables:
        print(
            f"   {variable.name}: "
            f"bitWidth={variable.bitWidth}, "
            f"value={getattr(variable, 'value', None)}"
        )

    # 3. Display constraints and their terms
    print("\n3. CONSTRAINTS")

    for constraint_obj in constraints:
        print(f"\n   Constraint: {constraint_obj.name}")
        print(f"   Operator: {constraint_obj.oper}")
        print(f"   Constant: {constraint_obj.const}")

        constraint_terms = []

        for link in model.links:
            if link.association == constraint_has_terms:
                connected_constraint = get_connected_object(
                    link, "constraint"
                )

                if connected_constraint == constraint_obj:
                    connected_term = get_connected_object(
                        link, "terms"
                    )

                    if connected_term is not None:
                        constraint_terms.append(connected_term)

        # Sort terms for consistent output
        constraint_terms.sort(key=lambda t: t.name)

        print("   Terms:")

        equation_parts = []

        for term_obj in constraint_terms:
            linked_variable = None

            for link in model.links:
                if link.association == term_ref_var:
                    connected_term = get_connected_object(
                        link, "terms"
                    )

                    if connected_term == term_obj:
                        linked_variable = get_connected_object(
                            link, "variable"
                        )
                        break

            if linked_variable is not None:
                print(
                    f"      {term_obj.name}: "
                    f"coefficient={term_obj.coef}, "
                    f"variable={linked_variable.name}"
                )

                equation_parts.append(
                    f"{term_obj.coef}*{linked_variable.name}"
                )
            else:
                print(
                    f"      {term_obj.name}: "
                    f"coefficient={term_obj.coef}, "
                    f"NO VARIABLE LINK FOUND"
                )

        equation = " + ".join(equation_parts)
        equation += f" {constraint_obj.const:+d} "

        print(f"\n   Reconstructed equation:")
        print(f"   {equation} {constraint_obj.oper} 0")

    # 4. Display the associations
    print("\n4. ASSOCIATIONS")

    association_counts = {}

    for link in model.links:
        association_name = link.association.name
        association_counts[association_name] = (
            association_counts.get(association_name, 0) + 1
        )

    for association_name, count in sorted(
        association_counts.items()
    ):
        print(f"   {association_name}: {count} links")

    print("\nObject classifiers:")

    print(f"\nTotal BESSER objects: {len(model.instances)}")

    model_elements = [
        obj for obj in model.instances
        if obj.classifier in (
            lac_problem,
            decision_var,
            constraint,
            term
        )
    ]

    print(f"Actual model elements: {len(model_elements)}")
    
    print("\n========== END OF INSPECTION ==========\n")

# STEP 12: Execute T1 when this file runs directly

if __name__ == "__main__":

    result = transform_t1(problem_instance)

    print("\nT1 transformation completed successfully.")

    print(f"Generated objects: {len(result.instances)}")
    print(f"Generated links: {len(result.links)}")

    print("\nExpected equation:")

    print(
        " + ".join(
            f"{2 * j.load}*y_{get_job_id(j)}"
            for j in sorted(
                [
                    obj for obj in problem_instance.instances
                    if obj.classifier == job
                ],
                key=get_job_id
            )
        )
        + f" - {sum(j.load for j in problem_instance.instances if j.classifier == job)} == 0"
    )

    inspect_lac_model(result)


