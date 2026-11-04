"""Causal recorded-trajectory -> calibrated composition -> planning framework.

Only observations and configured assumptions enter inference, never true labels.
"""
from collections import deque
import math
from src.crowd_state import Point,snapshot,validate_zones
from src.mobility_probability import composition,probability
from src.resource_planning import plan,request_probability

class CrowdFramework:
    def __init__(self,zones,detector,roi_contains=None,budget=6,capacity=2,r0=.1,r1=.4,trigger_x=-1.):
        validate_zones(zones);probability(r0);probability(r1)
        self.zones=zones;self.detector=detector;self.prior=probability(detector.training_prior)
        self.roi_contains=roi_contains or (lambda p:any(z.contains(p) for z in zones))
        self.budget=budget;self.capacity=capacity;self.r0=r0;self.r1=r1;self.trigger_x=trigger_x
        self.histories={};self.estimates={};self.attempted=set();self.time=None;self.current=[]
        self.geometry_mismatches=[]

    def ingest_frame(self,time,observations):
        if not math.isfinite(time) or (self.time is not None and time<=self.time):raise ValueError('Frames must advance in time')
        points=[Point(str(pid),float(time),float(x),float(y)) for pid,x,y in observations]
        if len({p.person for p in points})!=len(points):raise ValueError('Duplicate ID in frame')
        if any(not all(math.isfinite(v) for v in [p.x,p.y]) for p in points):raise ValueError('Nonfinite position')
        for p in points:
            history=self.histories.setdefault(p.person,deque(maxlen=101))
            previous=history[-1] if history else None
            if previous and abs(p.time-previous.time-.04)>1e-6:history.clear()
            history.append(p)
            if previous and previous.x<self.trigger_x<=p.x and p.person not in self.attempted:
                self.attempted.add(p.person)
                if len(history)==101:
                    pred=self.detector.predict([(a.x,a.y) for a in history],[a.time for a in history])
                    probability(pred['probability']);probability(pred['raw_score'])
                    self.estimates[p.person]=dict(**pred,source='calibrated_detector',observed_at_s=time)
        self.time=time;self.current=points

    def analyse(self):
        if self.time is None:raise ValueError('Ingest a frame first')
        active=[p for p in self.current if self.roi_contains(p)]
        invalid=[p.person for p in active if not any(z.contains(p) for z in self.zones)]
        if invalid:raise ValueError('Current positions conflict with walkable geometry: '+','.join(invalid))
        history=[p for a in active for p in self.histories[a.person] if self.time-2-1e-10<=p.time<=self.time]
        state=snapshot(history,self.zones,self.time,history=2,max_gap=.040001,crossing_x=self.trigger_x)
        for p in state['occupants']:
            e=self.estimates.get(p['person_id'])
            if e is None:
                e=dict(probability=self.prior,raw_score=self.prior,source='training_prior',observed_at_s=None)
            p.update(wheelchair_probability=e['probability'],raw_detector_score=e['raw_score'],
                probability_source=e['source'],probability_observed_at_s=e['observed_at_s'])
        summaries=[];groups=[]
        for z in state['zones']:
            people=[p for p in state['occupants'] if p['zone']==z['zone']]
            ps=[p['wheelchair_probability'] for p in people]
            summaries.append(dict(**z,**{k:v for k,v in composition(ps).items() if k!='pmf'},
                detected_count=sum(p['probability_source']=='calibrated_detector' for p in people),
                prior_count=sum(p['probability_source']=='training_prior' for p in people)))
            groups.append([request_probability(p,self.r0,self.r1) for p in ps])
        decision=plan(groups,self.budget,self.capacity)
        overall=composition([p['wheelchair_probability'] for p in state['occupants']]);overall.pop('pmf')
        return dict(time_s=self.time,occupants=state['occupants'],zones=summaries,composition=overall,
            detector_coverage=sum(p['probability_source']=='calibrated_detector' for p in state['occupants'])/len(state['occupants']) if state['occupants'] else 0.,
            planning=decision,assumptions=dict(request_rates=[self.r0,self.r1],budget=self.budget,capacity=self.capacity,
                demand='Hypothetical independent requests, not observed service need',count_intervals='Working independent-membership approximation',
                detector='First x=-1 crossing with four seconds of history; cached probability; prior before eligibility',
                generalisation='SiME-domain prototype; no validated age/child recognition or arbitrary-scene transfer'))
