import skmob
from skmob.privacy import attacks
from skmob.core.trajectorydataframe import TrajDataFrame

from algoritmos.utils.io import write as write_json, read_regions
from algoritmos.utils import processed
from algoritmos.utils.io import read_anon_zhang, read_naghizade, read_anon_tu
from skmob.io.file import write
from algoritmos.utils.trajetory import process


def location_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
    """
    In a location attack the adversary knows the coordinates of the locations visited by an individual and matches them
    against trajectories.
    """
    # TODO: Location attack
    at = attacks.LocationAttack(knowledge_length=2)
    r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def loc_sequence_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
    # TODO: Location Sequence Attack
    """
    In a location sequence attack the adversary knows the coordinates of locations visited by an individual and
    the order in which they were visited and matches them against trajectories.
    """
    at = attacks.LocationSequenceAttack(knowledge_length=2)
    r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def loc_time_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
    # TODO: Location Time Attack
    """
    In a location time attack the adversary knows the coordinates of locations visited by an individual and the time
    in which they were visited and matches them against trajectories. The precision at which to consider the temporal
    information can also be specified.
    """
    at = attacks.LocationTimeAttack(knowledge_length=2)
    r = at.assess_risk(trajectories, show_progress=True)

    # change the time granularity of the attack
    # at.time_precision = "Month"
    # r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def unique_loc_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
    # TODO: Unique Location Attack
    """
    In a unique location attack the adversary knows the coordinates of unique locations visited by an individual,
    and matches them against frequency vectors. A frequency vector, is an aggregation on trajectory
    data showing the unique locations visited by an individual and the frequency with which he visited those locations.
    """
    at = attacks.UniqueLocationAttack(knowledge_length=2)
    r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def loc_frequency_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
    # TODO: Location Frequency Attack
    """
    In a location frequency attack the adversary knows the coordinates of the unique locations visited by an individual
    and the frequency with which he visited them, and matches them against frequency vectors. A frequency vector,
    is an aggregation on trajectory data showing the unique locations visited by an individual and the frequency
    with which he visited those locations. It is possible to specify a tolerance level for the matching of the frequency.
    """
    at = attacks.LocationFrequencyAttack(knowledge_length=2)
    r = at.assess_risk(trajectories, show_progress=True)

    # change the tolerance with witch the frequency is matched
    # at.tolerance = 0.5
    # r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def loc_probability_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
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
    r = at.assess_risk(trajectories, show_progress=True)

    # change the tolerance with witch the frequency is matched
    # at.tolerance = 0.5
    # r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def loc_proportion_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
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
    r = at.assess_risk(trajectories, show_progress=True)

    # change the tolerance with witch the frequency is matched
    # at.tolerance = 0.5
    # r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def homework_eval(trajectories: TrajDataFrame) -> TrajDataFrame:
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
    r = at.assess_risk(trajectories, show_progress=True)

    # inspect probability of reidentification for each background knowledge instance
    # r = at.assess_risk(trajectories, targets=[1, 2], force_instances=True)
    return r


def eval_trajectories():
    # nyc_trajectories = process('../resources/dataset_TSMC2014_NYC.csv', False)
    # attacks_eval('nyc', nyc_trajectories)

    # nyc_trajectories_filtered = process('../resources/dataset_TSMC2014_NYC.csv')
    # attacks_eval('nyc-filtered', nyc_trajectories_filtered)

    # tky_trajectories = process('../resources/dataset_TSMC2014_NYC.csv', False)
    # attacks_eval('tky', tky_trajectories)

    # tky_trajectories_filtered = process('../resources/dataset_TSMC2014_NYC.csv')
    # attacks_eval('tky-filtered', tky_trajectories_filtered)

    # naghizade_dataframe = processed.naghizade(read_naghizade('naghizade2020/anonymized.json'))
    # attacks_eval('naghizade', naghizade_dataframe)

    # naghizade_dtf = processed.naghizade(read_naghizade('naghizade2020/anonymized-TKY.json'))
    # attacks_eval('naghizade-TKY', naghizade_dtf)

    # zhang_dataframe = processed.zhang(read_anon_zhang('zhang2015/anonymized.json'))
    # attacks_eval('zhang', zhang_dataframe)

    # zhang_dataframe = processed.zhang(read_anon_zhang('zhang2015/anonymized-TKY.json'))
    # attacks_eval('zhang-TKY', zhang_dataframe)

    # regions_nyc = read_regions('tu2017/regions.json')
    # tu_dtf = processed.tu(read_anon_tu('tu2017/k2l4t001-anonymized.json'), regions_nyc)
    # attacks_eval('tu', tu_dtf)

    regions_tky = read_regions('tu2017/regions-TKY.json')
    tu_dtf = processed.tu(read_anon_tu('tu2017/k2l4t001-anonymized-TKY.json'), regions_tky)
    attacks_eval('tu-TKY', tu_dtf)



def attacks_eval(name: str, trajectories: TrajDataFrame) -> None:
    print(f'Evaluating {name}!')

    print(f'Location Attack')
    location = location_eval(trajectories)
    write(location, f'{name}-location.json')

    print(f'Location Sequence Attack')
    sequence = loc_sequence_eval(trajectories)
    write(sequence, f'{name}-sequence.json')

    print(f'Time Attack')
    time = loc_time_eval(trajectories)
    write(time, f'{name}-time.json')

    print(f'Unique Location Attack')
    unique = unique_loc_eval(trajectories)
    write(unique, f'{name}-unique.json')

    print(f'Frequency Attack')
    frequency = loc_frequency_eval(trajectories)
    write(frequency, f'{name}-frequency.json')

    print(f'Probability Attack')
    probability = loc_probability_eval(trajectories)
    probability.columns = probability.columns.str.strip()
    # write(probability, f'{name}-probability.json')
    write_json(probability.to_json(), f'{name}-probability.json')

    print(f'Proportion Attack')
    proportion = loc_proportion_eval(trajectories)
    proportion.columns = proportion.columns.str.strip()
    write(proportion, f'{name}-proportion.json')

    print(f'Home Work Attack')
    homework = homework_eval(trajectories)
    homework.columns = homework.columns.str.strip()
    write(homework, f'{name}-homework.json')


if __name__ == '__main__':
    eval_trajectories()
