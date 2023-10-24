import skmob
from skmob.privacy import attacks
from skmob.core.trajectorydataframe import TrajDataFrame

from algoritmos.utils import processed
from algoritmos.utils.io import read_anon_zhang, read_naghizade
from algoritmos.utils.trajetory import process


def location_eval(trajectories: TrajDataFrame):
    """
    In a location attack the adversary knows the coordinates of the locations visited by an individual and matches them
    against trajectories.
    """
    # TODO: Location attack
    at = attacks.LocationAttack(knowledge_length=2)
    r = at.assess_risk(trajectories)
    print(r)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def loc_sequence_eval(trajectories: TrajDataFrame):
    # TODO: Location Sequence Attack
    """
    In a location sequence attack the adversary knows the coordinates of locations visited by an individual and
    the order in which they were visited and matches them against trajectories.
    """
    at = attacks.LocationSequenceAttack(knowledge_length=2)
    r = at.assess_risk(trajectories)

    # inspect probability of reidentification for each background knowledge instance
    r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def loc_time_eval(trajectories: TrajDataFrame):
    # TODO: Location Time Attack
    """
    In a location time attack the adversary knows the coordinates of locations visited by an individual and the time
    in which they were visited and matches them against trajectories. The precision at which to consider the temporal
    information can also be specified.
    """
    at = attacks.LocationTimeAttack(knowledge_length=2)
    r = at.assess_risk(trajectories)

    # change the time granularity of the attack
    at.time_precision = "Month"
    r = at.assess_risk(trajectories)

    # inspect probability of reidentification for each background knowledge instance
    r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def unique_loc_eval(trajectories: TrajDataFrame):
    # TODO: Unique Location Attack
    """
    In a unique location attack the adversary knows the coordinates of unique locations visited by an individual,
    and matches them against frequency vectors. A frequency vector, is an aggregation on trajectory
    data showing the unique locations visited by an individual and the frequency with which he visited those locations.
    """
    at = attacks.UniqueLocationAttack(knowledge_length=2)
    r = at.assess_risk(trajectories)

    # inspect probability of reidentification for each background knowledge instance
    r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def loc_frequency_eval(trajectories: TrajDataFrame):
    # TODO: Location Frequency Attack
    """
    In a location frequency attack the adversary knows the coordinates of the unique locations visited by an individual
    and the frequency with which he visited them, and matches them against frequency vectors. A frequency vector,
    is an aggregation on trajectory data showing the unique locations visited by an individual and the frequency
    with which he visited those locations. It is possible to specify a tolerance level for the matching of the frequency.
    """
    at = attacks.LocationFrequencyAttack(knowledge_length=2)
    r = at.assess_risk(trajectories)

    # change the tolerance with witch the frequency is matched
    at.tolerance = 0.5
    r = at.assess_risk(trajectories)

    # inspect probability of reidentification for each background knowledge instance
    r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def loc_probability_eval(trajectories: TrajDataFrame):
    # TODO: Location Probability Attack
    """
    In a location probability attack the adversary knows the coordinates of the unique
     locations visited by an individual and the probability with which he visited them,
    and matches them against probability vectors.
    A probability vector, is an aggregation on trajectory data showing the unique locations
    visited by an individual and the probability with which he visited those locations.
    It is possible to specify a tolerance level for the matching of the probability.
    """
    at = attacks.LocationProbabilityAttack(knowledge_length=2)
    r = at.assess_risk(trajectories)

    # change the tolerance with witch the frequency is matched
    at.tolerance = 0.5
    r = at.assess_risk(trajectories)

    # inspect probability of reidentification for each background knowledge instance
    r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def loc_proportion_eval(trajectories: TrajDataFrame):
    # TODO: Location Proportion Attack
    """
    In a location proportion attack the adversary knows the coordinates of the unique 
    locations visited by an individual and the relative proportions between their 
    frequencies of visit, and matches them against frequency vectors.
    A frequency vector is an aggregation on trajectory data showing the unique 
    locations visited by an individual and the frequency with which he visited
    those locations.
    It is possible to specify a tolerance level for the matching of the proportion.
    """
    at = attacks.LocationProportionAttack(knowledge_length=2)
    r = at.assess_risk(trajectories)

    # change the tolerance with witch the frequency is matched
    at.tolerance = 0.5
    r = at.assess_risk(trajectories)

    # inspect probability of reidentification for each background knowledge instance
    r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def homework_eval(trajectories: TrajDataFrame):
    # TODO: Homework Attack
    """
    In a home and work attack the adversary knows the coordinates of
    the two locations most frequently visited by an individual, and 
    matches them against frequency vectors.
    A frequency vector is an aggregation on trajectory data showing 
    the unique locations visited by an individual and the frequency
    with which he visited those locations.
    This attack does not require the generation of combinations to build
    the possible instances of background knowledge.
    """
    at = attacks.HomeWorkAttack()
    r = at.assess_risk(trajectories)

    # inspect probability of reidentification for each background knowledge instance
    r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)


def experiments():
    # Não anonimizada (zhang)
    print('processing non anon')
    z_trajectories = process('../resources/dataset_TSMC2014_NYC.csv')

    # naghizade = read
    zhang_t = read_anon_zhang('zhang2015/anonymized.json')
    dataframe = processed.zhang(zhang_t)
    print('evaluating zhang')
    location_eval(dataframe)
    print('evaluating not anon')
    location_eval(z_trajectories)


def expr_naghizade():
    z_trajectories = process('../resources/dataset_TSMC2014_NYC.csv', False)
    naghizade_t = read_naghizade('naghizade2020/anonymized.json')


if __name__ == '__main__':
    # experiments()
    expr_naghizade()
