"""
Section AC
Topic: Final Project
Group Members: Kairui Huang, Runbo Wang, Danhiel Vu
Date: 03/13/2020
Gets all the respective Jersey City, CitiBike datas and
organizes/reformats it the data for it to compatible
when used from other classes.
"""
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier

import seaborn as sns
import matplotlib.pyplot as plt

sns.set()


def decision_tree_classifier(filtered_data, max_depth=20):
    """
    Fits and predicts the end station name using
    the decision tree classifier. Prints out
    the accuracy score and feature importances
    of the model.

    @param filtered_data | filtered Citi Bike trip data.
    """
    X = filtered_data.loc[:, filtered_data.columns != 'endstationname']
    X = pd.get_dummies(X)
    y = filtered_data['endstationname']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = DecisionTreeClassifier(max_depth)

    model.fit(X_train, y_train)
    print(accuracy_score(y_test, model.predict(X_test)))
    print(dict(zip(X, model.feature_importances_)))


def plot_dtc_accuracy(filtered_data):
    """
    Plots the decision tree classifiers training
    and test accuracy over a max depth.

    @param filtered_data | filtered Citi Bike trip data.
    """
    X = filtered_data.loc[:, filtered_data.columns != 'endstationname']
    X = pd.get_dummies(X)
    y = filtered_data['endstationname']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                        random_state=1)

    data = []
    for i in range(1, 102, 10):
        model = DecisionTreeClassifier(max_depth=i, random_state=1)
        model.fit(X_train, y_train)
        print(i)

        y_train_pred = model.predict(X_train)
        train_acc = accuracy_score(y_train, y_train_pred)

        y_test_pred = model.predict(X_test)
        test_acc = accuracy_score(y_test, y_test_pred)

        data.append({'max depth': i, 'train accuracy': train_acc,
                    'test accuracy': test_acc})

    data = pd.DataFrame(data)
    sns.relplot(kind='line', x='max depth', y='train accuracy', data=data)
    plt.savefig('train_dtc.png')
    sns.relplot(kind='line', x='max depth', y='test accuracy', data=data)
    plt.savefig('test_dtc.png')


def mlp_classifier(filtered_data):
    """
    Fits and predicts the end station name using
    the MLPClassifier model. Print out the
    training, testing, and accuracy score of the model.

    @param filtered_data | filtered Citi Bike trip data.
    """
    X = filtered_data.loc[:, filtered_data.columns != 'endstationname']
    X = pd.get_dummies(X)
    X = X.astype('int8')
    y = filtered_data['endstationname']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                        random_state=1)

    mlp = MLPClassifier(hidden_layer_sizes=(150, 150, 150), random_state=1)

    mlp.fit(X_train, y_train)
    print('Training score', mlp.score(X_train, y_train))
    print('Testing score', mlp.score(X_test, y_test))
    print('Accuracy score', accuracy_score(y_test, mlp.predict(X_test)))


def tune_hyperparameters(filtered_data):
    """
    Print out the training set and test set score results
    of different hyperparameters for the MLPClassifier.

    @param filtered_data | filtered Citi Bike trip data.
    """
    X = filtered_data.loc[:, filtered_data.columns != 'endstationname']
    X = pd.get_dummies(X)
    y = filtered_data['endstationname']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    learning_rates = [0.01, 0.5, 1.0]
    sizes = [(10,), (50,), (10, 10, 10, 10), (100, 100, 100), (150, 150, 150)]
    for learning_rate in learning_rates:
        for size in sizes:
            print(f'Learning Rate {learning_rate}, Size {size}')
            mlp = MLPClassifier(hidden_layer_sizes=size, max_iter=10,
                                random_state=1,
                                learning_rate_init=learning_rate)
            mlp.fit(X_train, y_train)
            print("    Training set score: %f" % mlp.score(X_train, y_train))
            print("    Test set score: %f" % mlp.score(X_test, y_test))


def filter_data(data):
    """
    Filters the Citi Bike trip data.

    @param data | Citi Bike trip data.
    """
    filtered_data = data.loc[:, ['Season', 'month', 'Peak', 'gender', 'Period',
                                 'age', 'usertype', 'endstationname',
                                 'startstationid']]
    return filtered_data


def main():
    """
    Calls the machine learning models.
    """
    data = pd.read_csv('filtered_bike_data.csv')
    filtered_data = filter_data(data)

    decision_tree_classifier(filtered_data)
    # plot_dtc_accuracy(filtered_data, 20)
    # neural_network(filtered_data)
    # tune_hyperparameters(filtered_data)


if __name__ == '__main__':
    main()
