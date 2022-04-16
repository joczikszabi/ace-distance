from helpers.grid.linear_regression import linear_regression


def correct_grid_cols(nodes):
    X = [node[0] for node in nodes if node != []]
    Y = [node[1] for node in nodes if node != []]

    return linear_regression(X, Y)
