"""Conditional probabilities for a declared metadata channel, not recognition."""
import math


def probability(value):
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Probability must be finite and in [0,1]')
    return value


def posterior(observed, prior, error):
    """P(C=1 | O), assuming a symmetric independent bit-error channel."""
    if observed not in (0,1):
        raise ValueError('Observation must be binary')
    probability(prior); probability(error)
    positive = prior * (1-error if observed else error)
    negative = (1-prior) * (error if observed else 1-error)
    if positive+negative == 0:
        raise ValueError('Observation is impossible under supplied assumptions')
    return positive/(positive+negative)


def count_distribution(probabilities):
    """Poisson-binomial PMF under explicitly assumed independent memberships."""
    pmf = [1.0]
    for p in probabilities:
        probability(p)
        updated = [0.0]*(len(pmf)+1)
        for k,mass in enumerate(pmf):
            updated[k] += mass*(1-p)
            updated[k+1] += mass*p
        pmf = updated
    return pmf


def quantile(pmf, level):
    probability(level)
    cumulative = 0.0
    for k,mass in enumerate(pmf):
        cumulative += mass
        if cumulative >= level-1e-14:
            return k
    return len(pmf)-1


def composition(probabilities, coverage=0.9):
    ps = list(probabilities)
    probability(coverage)
    if coverage == 0:
        raise ValueError('Coverage must be positive')
    pmf = count_distribution(ps)
    tail = (1-coverage)/2
    return dict(observed_count=len(ps), expected_count=sum(ps),
                variance_independence=sum(p*(1-p) for p in ps),
                interval=[quantile(pmf,tail),quantile(pmf,1-tail)],
                nominal_coverage=coverage,pmf=pmf,
                assumption='independent memberships; working approximation after crowd selection')


def zone_composition(state, observations, prior, error, coverage=0.9):
    """Join metadata by active ID; missing observations retain the working prior.

    Extra metadata never creates occupants. No ground-truth labels are accepted.
    """
    probability(prior); probability(error)
    groups = {z['zone']:[] for z in state['zones']}
    missing = {z:0 for z in groups}
    for person in state['occupants']:
        pid,z = person['person_id'],person['zone']
        observed = observations.get(pid)
        if observed is None:
            p = prior
            missing[z] += 1
        else:
            p = posterior(observed,prior,error)
        groups[z].append(p)
    return [dict(zone=z,missing_metadata_count=missing[z],**composition(ps,coverage))
            for z,ps in sorted(groups.items())]
