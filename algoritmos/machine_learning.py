from itertools import pairwise
from pathlib import Path

import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn.naive_bayes import CategoricalNB, GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import accuracy_score

from numpy import array, asarray

from algoritmos.naghizade2020.treat_data import Segmented, Stop
from algoritmos.tu2017.region import Region
from algoritmos.tu2017.treat_data import TuTrajectory
from algoritmos.utils import semantic
from algoritmos.utils.io import read_anon_zhang, read_naghizade, read_anon_tu, read_regions
from algoritmos.utils.semantic import SemanticTrajectory, PoiCategory, get_venue_category
from algoritmos.utils.trajetory import create_raw_trajectories, split_trajectories, add_duration, Point
from algoritmos.zhang2015.group import ZhangTrajectory


def decision_tree(training, test):
    clf = tree.DecisionTreeClassifier()

    x, y = training
    clf.fit(x, y)
    # result = clf.predict(x)
    x_test, y_test = test
    y_predicted = clf.predict(x_test)
    print('Tree confusion matrix')
    acc = accuracy_score(y_test, y_predicted)
    print(f'acurácia: {acc}')


def ann(test_set, training_set):
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)

    train_x, train_y = training_set
    clf.fit(train_x, train_y)

    test_x, test_y = test_set
    y_predicted = clf.predict(test_x)
    print('Ann confusion matrix')
    acc = accuracy_score(test_y, y_predicted)
    print(f'acurácia: {acc}')


def bayes(test_set, training_set):
    clf = GaussianNB()
    train_x, train_y = training_set
    clf.fit(train_x, train_y)

    test_x, test_y = test_set
    y_predicted = clf.predict(test_x)
    print('Bayes confusion matrix')
    acc = accuracy_score(test_y, y_predicted)
    print(f'acurácia: {acc}')


def support_vector(test_set, training_set):
    clf = svm.SVC()

    train_x, train_y = training_set
    clf.fit(train_x, train_y)

    test_x, test_y = test_set
    y_predicted = clf.predict(test_x)

    print('Support Vector confusion matrix')
    acc = accuracy_score(test_y, y_predicted)
    print(f'acurácia: {acc}')


def nearest_neighbour(test_set, training_set):
    neigh = KNeighborsClassifier()

    x, y = training_set
    neigh.fit(x, y)

    test_x, test_y = test_set
    y_predicted = neigh.predict(test_x)

    print('Nearest Neighbour confusion matrix')
    acc = accuracy_score(test_y, y_predicted)
    print(f'acurácia: {acc}')


def first(s):
    return next(iter(s))


def construct(trajectories: list[SemanticTrajectory]):
    """
    Adquire a categoria do próximo lugar dado um ponto a partir das trajetórias semanticas fornecidas.
    """
    current = []
    expected = []
    for trajectory in trajectories:
        for p, next_p in pairwise(trajectory.points):
            current.append(int(p.category.value))
            expected.append(int(next_p.category.value))

    current = asarray(current, dtype=int).reshape(-1, 1)
    expected = asarray(expected, dtype=int)
    return current, expected


def build_zhang(trajectories: list[ZhangTrajectory]):
    current = []
    expected = []
    for trajectory in trajectories:
        for p, next_p in pairwise(trajectory.points):
            if isinstance(p, Point):
                cur_p = semantic.generalize_venue_category(p.category)
            else:
                cur_p = p.semantic[0]
            if isinstance(next_p, Point):
                exp_p = semantic.generalize_venue_category(next_p.category)
            else:
                exp_p = next_p.semantic[0]
            current.append(int(cur_p))
            expected.append(int(exp_p))

    current = asarray(current, dtype=int).reshape(-1, 1)
    expected = asarray(expected, dtype=int)
    return current, expected


def build_naghizade(trajectories: list[Segmented]):
    current = []
    expected = []
    for trajectory in trajectories:
        points = [point for point in trajectory.points if isinstance(point, Stop)]
        for p, next_p in pairwise(points):
            current.append(int(p.semantic))
            expected.append(int(next_p.semantic))

    current = asarray(current, dtype=int).reshape(-1, 1)
    expected = asarray(expected, dtype=int)
    return current, expected


def build_tu(trajectories: list[TuTrajectory], regions: dict[int, Region]):
    current = []
    expected = []
    for trajectory in trajectories:
        for p, next_p in pairwise(trajectory.points):
            # cur_regions = [regions[rid] for rid in p.region_id]
            # exp_regions = [regions[rid] for rid in next_p.region_id]

            for creg in p.region_id:
                for ereg in next_p.region_id:
                    current.append(creg)
                    expected.append(ereg)

    current = asarray(current).reshape(-1, 1)
    expected = asarray(expected)
    return current, expected


def build_tu_alternative(trajectories: list[TuTrajectory], regions: dict[int, Region]):
    current = []
    expected = []
    for trajectory in trajectories:
        for p, next_p in pairwise(trajectory.points):
            cur_regions = [regions[rid] for rid in p.region_id]
            exp_regions = [regions[rid] for rid in next_p.region_id]

            for c_reg, e_reg in zip(cur_regions, exp_regions):
                x = unpack_categories(c_reg.categories)
                y = unpack_categories(e_reg.categories)

                for catx, caty in zip(x, y):
                    current.append(catx)
                    expected.append(caty)


    current = asarray(current, dtype=int).reshape(-1, 1)
    expected = asarray(expected, dtype=int)
    return current, expected


def unpack_categories(categories: dict[PoiCategory, int]) -> list[PoiCategory]:
    unpacked = []
    for category, quantity in categories.items():
        for _ in range(quantity):
            unpacked.append(category)

    return unpacked


def classify(x_train, y_train, x_test, y_test):

    # Decision Tree
    decision_tree((x_test, y_test), (x_train, y_train))
    # Naive Bayes
    bayes((x_test, y_test), (x_train, y_train))
    # Neural Network
    ann((x_test, y_test), (x_train, y_train))
    # Support Vector Machines
    support_vector((x_test, y_test), (x_train, y_train))
    # Nearest Neighbour
    nearest_neighbour((x_test, y_test), (x_train, y_train))


def separate(traj, test_part=0.75):
    test_amount = int(len(traj) * test_part)
    train_amount = int(len(traj) * (1 - test_part))
    return traj[:test_amount], traj[train_amount:]


if __name__ == '__main__':
    # NYC não anon
    # print('NYC não anon')
    # dataset_name_nyc = Path(__file__).parent / "../resources/dataset_TSMC2014_NYC.csv"
    # trajectories_nyc = create_raw_trajectories(str(dataset_name_nyc))
    # splitted_nyc = split_trajectories(trajectories_nyc, 3)
    # with_duration_nyc = add_duration(splitted_nyc)
    # semantic_nyc = get_venue_category(with_duration_nyc)

    # test_nyc, train_nyc = separate(semantic_nyc)
    # test_x_nyc, test_y_nyc = construct(test_nyc)
    # train_x_nyc, train_y_nyc = construct(train_nyc)
    # classify(train_x_nyc, train_y_nyc, test_x_nyc, test_y_nyc)

    # zhang NYC
    # print('zhang NYC')
    # zhang_nyc = read_anon_zhang('zhang2015/anonymized.json')
    # test_zhang_nyc, train_zhang_nyc = separate(zhang_nyc)
    # test_x_zhang_nyc, test_y_zhang_nyc = build_zhang(test_zhang_nyc)
    # train_x_zhang_nyc, train_y_zhang_nyc = build_zhang(train_zhang_nyc)
    # classify(train_x_zhang_nyc, train_y_zhang_nyc, test_x_zhang_nyc, test_y_zhang_nyc)

    # naghizade NYC
    # print('naghizade NYC')
    # naghizade_nyc = read_naghizade('naghizade2020/anonymized.json')
    # test_nagh_nyc, train_nagh_nyc = separate(naghizade_nyc)
    # test_x_nagh_nyc, test_y_nagh_nyc = build_naghizade(test_nagh_nyc)
    # train_x_nagh_nyc, train_y_nagh_nyc = build_naghizade(train_nagh_nyc)
    # classify(train_x_nagh_nyc, train_y_nagh_nyc, test_x_nagh_nyc, test_y_nagh_nyc)

    # tu NYC
    # print('tu NYC')
    # tu_nyc = read_anon_tu('tu2017/k2l4t001-anonymized.json')
    # regions_nyc = read_regions('tu2017/regions.json')
    # test_tu_nyc, train_tu_nyc = separate(tu_nyc)
    # test_x_tu_nyc, test_y_tu_nyc = build_tu_alternative(test_tu_nyc, regions_nyc)
    # train_x_tu_nyc, train_y_tu_nyc = build_tu_alternative(train_tu_nyc, regions_nyc)
    # classify(train_x_tu_nyc, train_y_tu_nyc, test_x_tu_nyc, test_y_tu_nyc)

    # TKY não anon
    # print('TKY não anon')
    # dataset_name_tky = Path(__file__).parent / "../resources/dataset_TSMC2014_TKY.csv"
    # trajectories_tky = create_raw_trajectories(str(dataset_name_tky))
    # splitted_tky = split_trajectories(trajectories_tky, 3)
    # with_duration_tky = add_duration(splitted_tky)
    # semantic_tky = get_venue_category(with_duration_tky)

    # test_tky, train_tky = separate(semantic_tky)
    # test_x_tky, test_y_tky = construct(test_tky)
    # train_x_tky, train_y_tky = construct(train_tky)
    # classify(train_x_tky, train_y_tky, test_x_tky, test_y_tky)

    # zhang TKY
    # print('zhang TKY')
    # zhang_tky = read_anon_zhang('zhang2015/anonymized-TKY.json')
    # test_zhang_tky, train_zhang_tky = separate(zhang_tky)
    # test_x_zhang_tky, test_y_zhang_tky = build_zhang(test_zhang_tky)
    # train_x_zhang_tky, train_y_zhang_tky = build_zhang(train_zhang_tky)
    # classify(train_x_zhang_tky, train_y_zhang_tky, test_x_zhang_tky, test_y_zhang_tky)

    # naghizade TKY
    # print('naghizade TKY')
    # naghizade_tky = read_naghizade('naghizade2020/anonymized-TKY.json')
    # test_nagh_tky, train_nagh_tky = separate(naghizade_tky)
    # test_x_nagh_tky, test_y_nagh_tky = build_naghizade(test_nagh_tky)
    # train_x_nagh_tky, train_y_nagh_tky = build_naghizade(train_nagh_tky)
    # classify(train_x_nagh_tky, train_y_nagh_tky, test_x_nagh_tky, test_y_nagh_tky)

    # tu TKY
    tu_tky = read_anon_tu('tu2017/k2l4t001-anonymized-TKY.json')
    regions_tky = read_regions('tu2017/regions-TKY.json')
    test_tu_tky, train_tu_tky = separate(tu_tky)
    test_x_tu_tky, test_y_tu_tky = build_tu_alternative(test_tu_tky, regions_tky)
    train_x_tu_tky, train_y_tu_tky = build_tu_alternative(train_tu_tky, regions_tky)
    classify(train_x_tu_tky, train_y_tu_tky, test_x_tu_tky, test_y_tu_tky)
