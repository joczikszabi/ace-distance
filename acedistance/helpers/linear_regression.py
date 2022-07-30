import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def regression_f(x, a, b):
    return a * x + b


def linear_regression(X, Y):
    popt, pcov = curve_fit(regression_f, X, Y)
    regression_data = [[x, round(regression_f(x, popt[0], popt[1]))] for x in X]

    x_updated = [node[0] for node in regression_data]
    y_updated = [node[1] for node in regression_data]

    plt.xlim([0, 1920])
    plt.ylim([0, 1080])
    plt.scatter(X, Y)
    plt.scatter(x_updated, y_updated)
    plt.show()

    return regression_data


if __name__ == "__main__":
    linear_regression(sys.argv[1], sys.argv[2])
