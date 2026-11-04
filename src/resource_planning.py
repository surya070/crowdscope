"""Exact finite-budget allocation under independent scenario requests.

Policies accept probabilities only. Evaluation outcomes are supplied separately.
"""
import math
from src.mobility_probability import probability, count_distribution


def allocations(zones,budget):
    if not isinstance(zones,int) or zones<1 or not isinstance(budget,int) or budget<0:
        raise ValueError('Positive zone count and nonnegative integer budget required')
    if zones==1:
        yield (budget,)
    else:
        for first in range(budget+1):
            for tail in allocations(zones-1,budget-first):yield (first,)+tail


def validate(capacity):
    if not isinstance(capacity,int) or capacity<1:
        raise ValueError('Capacity must be a positive integer')


def expected_shortfall(pmf,capacity):
    return sum(mass*max(0,k-capacity) for k,mass in enumerate(pmf))


def request_probability(membership,r0=0.1,r1=0.4):
    probability(membership);probability(r0);probability(r1)
    return r0+(r1-r0)*membership


def plan(zone_probabilities,budget=6,capacity=2,mean_only=False):
    """Exact enumeration; tie within 1e-12 goes to lexicographic first.

    Zone sequence order defines the tie convention. Requests within and between
    zones are independent in this working model. No observations of realised
    requests or latent class are accepted here.
    """
    validate(capacity)
    groups=[list(ps) for ps in zone_probabilities]
    candidates=list(allocations(len(groups),budget))
    distributions=[count_distribution(ps) for ps in groups]
    means=[sum(ps) for ps in groups]
    costs=[[max(0,means[z]-capacity*a) if mean_only else expected_shortfall(distributions[z],capacity*a)
            for a in range(budget+1)] for z in range(len(groups))]
    best=None;best_cost=math.inf
    for allocation in candidates:
        loss=sum(costs[z][a] for z,a in enumerate(allocation))
        if loss<best_cost-1e-12:best,best_cost=allocation,loss
    return dict(allocation=best,expected_loss=best_cost,
                objective='shortfall_of_mean' if mean_only else 'expected_shortfall',
                feasible_allocations=len(candidates))


def realised_shortfall(allocation,demands,capacity=2):
    validate(capacity)
    if len(allocation)!=len(demands) or any(not isinstance(x,int) or x<0 for x in (*allocation,*demands)):
        raise ValueError('Allocation and demand must be matching nonnegative integer vectors')
    return sum(max(0,d-capacity*a) for a,d in zip(allocation,demands))
