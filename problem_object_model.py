from models import (
    lb_problem, job, machine,
    lb_has_jobs, lb_has_machines,
    problem_model
)
from besser.BUML.metamodel.object import Object, Link, LinkEnd, ObjectModel

# Pre-fetch association ends
lb_m_prob_end = next(end for end in lb_has_machines.ends if end.name == "problem")
lb_m_mach_end = next(end for end in lb_has_machines.ends if end.name == "machines")
lb_j_prob_end = next(end for end in lb_has_jobs.ends if end.name == "problem")
lb_j_jobs_end = next(end for end in lb_has_jobs.ends if end.name == "jobs")


def create_load_balancing_instance(instance_name: str, job_loads: list[int]) -> ObjectModel:
    """
    Factory function to create a LoadBalancingProblem ObjectModel instance.
    """
    # 1. Create Problem & Machine Objects
    lb_obj = Object(name=instance_name, classifier=lb_problem)
    lb_obj.name = instance_name

    m1_obj = Object(name="Machine_1", classifier=machine)
    m1_obj.name = "Machine_1"

    m2_obj = Object(name="Machine_2", classifier=machine)
    m2_obj.name = "Machine_2"

    instances = {lb_obj, m1_obj, m2_obj}
    links = set()

    # 2. Add Machine Links
    links.add(Link(name=f"link_m1_{instance_name}", association=lb_has_machines, connections=[
        LinkEnd(name="problem", association_end=lb_m_prob_end, object=lb_obj),
        LinkEnd(name="machines", association_end=lb_m_mach_end, object=m1_obj)
    ]))
    links.add(Link(name=f"link_m2_{instance_name}", association=lb_has_machines, connections=[
        LinkEnd(name="problem", association_end=lb_m_prob_end, object=lb_obj),
        LinkEnd(name="machines", association_end=lb_m_mach_end, object=m2_obj)
    ]))

    # 3. Create Job Objects & Links
    for idx, load in enumerate(job_loads, start=1):
        j_id = f"j{idx}"
        j_obj = Object(name=j_id, classifier=job)
        j_obj.id = j_id
        j_obj.load = load

        instances.add(j_obj)

        links.add(Link(name=f"link_{j_id}_{instance_name}", association=lb_has_jobs, connections=[
            LinkEnd(name="problem", association_end=lb_j_prob_end, object=lb_obj),
            LinkEnd(name="jobs", association_end=lb_j_jobs_end, object=j_obj)
        ]))

    # Instantiate ObjectModel with objects
    model = ObjectModel(
        name=instance_name,
        objects=instances
    )

    # Populate links in-place on the model's links set
    try:
        model.links.update(links)
    except AttributeError:
        model._links = links

    return model


# =====================================================================
# THREE TEST INSTANCES
# =====================================================================

instance_1_tiny = create_load_balancing_instance(
    instance_name="LoadBalancing_Tiny_2Jobs",
    job_loads=[4, 4]
)

# Instance 2: Medium (4 jobs) - Standard problem instance with known solutions
# Loads: [2, 3, 5, 6] -> Total 16 -> Balanced target = 8 per machine.
# Solutions: (2+6=8) and (3+5=8) -> bitstrings '1001' and '0110'
instance_2_medium = create_load_balancing_instance(
    instance_name="LoadBalancing_Medium_4Jobs",
    job_loads=[2, 3, 5, 6]
)

# Instance 3: Unsatisfiable / No Solution (4 jobs, odd total load)
# Loads: [1, 2, 4, 8] -> Total 15 (Odd) -> Impossible to split equally into integers.
# Purpose: Tests Grover algorithm behavior when 0 solutions exist.
instance_3_unsatisfiable = create_load_balancing_instance(
    instance_name="LoadBalancing_Unsatisfiable_4Jobs",
    job_loads=[1, 2, 4, 8]
)

# Default alias for backward compatibility
problem_instance = instance_2_medium

models = [problem_model]


if __name__ == "__main__":
    test_instances = [instance_1_tiny, instance_2_medium, instance_3_unsatisfiable]
    
    print("========== INSTANCE CREATION SUMMARY ==========")
    for inst in test_instances:
        objs = inst.objects if hasattr(inst, "objects") and inst.objects else inst.instances
        jobs = [o for o in objs if o.classifier == job]
        loads = [j.load for j in jobs]
        print(f"Instance: {inst.name:<35} | Jobs: {len(jobs)} | Loads: {loads} | Total Load: {sum(loads)}")