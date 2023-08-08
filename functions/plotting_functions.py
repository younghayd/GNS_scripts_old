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

    Adapted from: mikkopitkanen/fit_bivariate.py
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
    bfsl_fit=xi * grad+int
    r_numerator=sum((bfsl_fit-yi)**2)
    ymean=np.mean(yi)
    r_denominator=np.sum((yi - ymean)**2)
    r=1 - r_numerator / r_denominator


    # r = np.sum(Wi * (yi - grad*xi - int)**2.0)/100

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
        return {"grad":grad, "grad_err":grad_err, "int":int, "int_err":int_err, "r":r}
    else:
        print("bivariate_fit.py exceeded maximum number of iterations, " +
              "maxIter = {:}".format(maxIter))
        return np.nan, np.nan, np.nan, np.nan

def fit_plot(df, x, x_err, y, y_err, fit, location, save_path, marker_size, err_bar_size):
    """

    :param x:
    :param y:
    :param fit:
    :param location:
    :param x_lab:
    :param y_lab:
    :return:
    """
    import plotly.express as px
    import plotly.graph_objects as go
    import math
    import plotly.io as pio
    import kaleido

    fig = px.scatter(x = x, y = y,
                     error_x = x_err,
                     error_y = y_err,
                     color=df["site"]
                     ).update_layout(yaxis_title="COxs (ppb)",
                                     xaxis_title="CO<sub>2</sub>ff (ppm)",
                                     title=location.capitalize() + " flasks")

    fig.update_traces(marker={'size': marker_size})

    fig.data[0].error_y.thickness = err_bar_size
    fig.data[1].error_y.thickness = err_bar_size
    fig.data[2].error_y.thickness = err_bar_size
    fig.data[3].error_y.thickness = err_bar_size
    fig.data[4].error_y.thickness = err_bar_size
    fig.data[5].error_y.thickness = err_bar_size
    fig.data[6].error_y.thickness = err_bar_size
    fig.data[0].error_x.thickness = err_bar_size
    fig.data[1].error_x.thickness = err_bar_size
    fig.data[2].error_x.thickness = err_bar_size
    fig.data[3].error_x.thickness = err_bar_size
    fig.data[4].error_x.thickness = err_bar_size
    fig.data[5].error_x.thickness = err_bar_size
    fig.data[6].error_x.thickness = err_bar_size


    fig.add_trace(
        go.Scatter(x=x, y=fit["grad"]*x + fit["int"], name="York fit", line_shape="linear"))

    fig.add_annotation(x=min(x) + 0.05*(max(x) - min(x)), y=1.1*max(y),
                       text="y = " + str(round(fit["grad"], 1)) + "x + " + str(round(fit['int'], 1)),
                       font=dict(size=30),
                       showarrow=False)

    fig.add_annotation(x=min(x) + 0.05*(max(x) - min(x)), y=1*max(y),
                       text="r<sup>2</sup> = " + str(round(fit["r"], 2)),
                       font=dict(size=30),
                       showarrow=False)

    fig.add_annotation(x=min(x) + 0.05*(max(x) - min(x)), y=.89*max(y),
                       text="R<sub>CO</sub> = " + str(round(fit["grad"], 1)) + u" \u00B1 " +
                            str(math.ceil(fit["grad_err"])),
                       font=dict(size=30),
                       showarrow=False)

    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline = False)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True, zeroline = False)

    fig.update_layout(legend_title="",
                      legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
    ))

    fig.layout.template = "presentation"
    fig.show()

    pio.write_image(fig, save_path+location.lower()+"_flasks"+".png", scale=1, width=1400, height=850)

    fig.write_html(save_path+location.lower()+"_flasks"+".html")
