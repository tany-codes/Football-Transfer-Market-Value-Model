"""Reusable seaborn/matplotlib chart helpers."""
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


def median_value_bar(df, group_col, title, figsize=(8, 4.5), sort_by_value=True):
    """Horizontal bars of the median market value per group, labelled with the value and group size (n).

    sort_by_value=False keeps the groups in their natural order (e.g. height bands), first group on top.
    """
    g = df.groupby(group_col, observed=True)["market_value_in_eur"].agg(median="median", n="size")
    if sort_by_value:
        g = g.sort_values("median")
    else:
        g = g.iloc[::-1]  # barh draws the first row at the bottom
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(g.index, g["median"])
    ax.bar_label(
        bars,
        labels=[f"€{m / 1e6:.1f}M  (n={n})" for m, n in zip(g["median"], g["n"])],
        padding=4,
    )
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x / 1e6:g}M"))
    ax.margins(x=0.2)
    ax.set(xlabel="Median market value (EUR)", ylabel="", title=title)
    return fig, ax
