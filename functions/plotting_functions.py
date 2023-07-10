#Collection of functions used for plotting in Python


def york_fit(xi, yi, dxi, dyi, ri=0.0, grad_0=1.0, maxIter=1e6):

    """Make a linear bivariate fit to xi, yi data using York et al. (2004).
    This is an implementation of the line fitting algorithm presented in:
    York, D et al., Unified equations for the slope, intercept, and standard
    errors of the best straight line, American Journal of Physics, 2004, 72,
    3, 367-375, doi = 10.1119/1.1632486
    See especially Section III and Table I. The enumerated steps below are
    citations to Section III
    Parameters:
      xi, yi      x and y data points
      dxi, dyi    errors for the data points xi, yi
      ri          correlation coefficient for the weights
      b0          initial guess b
      maxIter     float, maximum allowed number of iterations
    Returns:
      a           y-intercept, y = a + bx
      b           slope
      S           goodness-of-fit estimate
      int_err     standard error of a
      grad_err     standard error of b
    Usage:
    [a, b] = bivariate_fit( xi, yi, dxi, dyi, ri, b0, maxIter)

    From: mikkopitkanen/fit_bivariate.py
    """

    import numpy as np

    # (1) Choose an approximate initial value of b
    grad = grad_0

    # (2) Determine the weights wxi, wyi, for each point.
    wxi = 1.0 / dxi**2.0
    wyi = 1.0 / dyi**2.0

    alphai = (wxi * wyi)**0.5
    grad_diff = 999.0

    # tolerance for the fit, when b changes by less than tol for two
    # consecutive iterations, fit is considered found
    tol = 1.0e-8

    # iterate until b changes less than tol
    iIter = 1
    while (abs(grad_diff) >= tol) & (iIter <= maxIter):

        grad_prev = grad

        # (3) Use these weights wxi, wyi to evaluate Wi for each point.
        Wi = (wxi * wyi) / (wxi + grad**2.0 * wyi - 2.0*grad*ri*alphai)

        # (4) Use the observed points (xi ,yi) and Wi to calculate x_bar and
        # y_bar, from which Ui and Vi , and hence betai can be evaluated for
        # each point
        x_bar = np.sum(Wi * xi) / np.sum(Wi)
        y_bar = np.sum(Wi * yi) / np.sum(Wi)

        Ui = xi - x_bar
        Vi = yi - y_bar

        betai = Wi * (Ui / wyi + grad*Vi / wxi - (grad*Ui + Vi) * ri / alphai)

        # (5) Use Wi, Ui, Vi, and betai to calculate an improved estimate of b
        grad = np.sum(Wi * betai * Vi) / np.sum(Wi * betai * Ui)

        # (6) Use the new b and repeat steps (3), (4), and (5) until successive
        # estimates of b agree within some desired tolerance tol
        grad_diff = grad - grad_prev

        iIter += 1

    # (7) From this final value of b, together with the final x_bar and y_bar,
    # calculate int from
    int = y_bar - grad * x_bar

    # Goodness of fit
    r = np.sum(Wi * (yi - grad*xi - int)**2.0)

    # (8) For each point (xi, yi), calculate the adjusted values xi_adj
    xi_adj = x_bar + betai

    # (9) Use xi_adj, together with Wi, to calculate xi_adj_bar and thence ui
    xi_adj_bar = np.sum(Wi * xi_adj) / np.sum(Wi)
    ui = xi_adj - xi_adj_bar

    # (10) From Wi , xi_adj_bar and ui, calculate grad_err, and then int_err
    # (the standard uncertainties of the fitted parameters)
    grad_err = np.sqrt(1.0 / np.sum(Wi * ui**2))
    int_err = np.sqrt(1.0 / np.sum(Wi) + xi_adj_bar**2 * grad_err**2)


    if iIter <= maxIter:
        return {"grad" : grad, "grad_err" : grad_err, "int" : int, "int_err" : int_err, "r" : r}
    else:
        print("bivariate_fit.py exceeded maximum number of iterations, " +
              "maxIter = {:}".format(maxIter))
        return np.nan, np.nan, np.nan, np.nan

def york_fit_plot(x, y, york_fit):
