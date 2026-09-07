from sage.all import *
import pandas as pd
import numpy as np


def num_upsets(g: DiGraph) -> int:
    """
    Returns how many upsets are in a DiGraph

    Parameters:
    g (DiGraph): The digraph

    Returns:
    upsets (int): How many upsets
    """
    wins_list: list[int] = g.out_degree_sequence()
    upsets: int = 0
    for edge in g.edges(sort=True, labels=False):
        if wins_list[edge[0]] > wins_list[edge[1]]:
            upsets += 1
    return upsets


def max_upsets(n: int) -> int:
    """
    Returns the maximum number of upsets for a round robin tournament graph (RRTG) on n vertcies

    Parameters:
    n (int): The order of the RRTGs being searched

    Returns:
    max (int): The maximum number of upsets of order n
    """
    max_upsets: int = max(map(num_upsets, digraphs.tournaments_nauty(n)))
    return max_upsets


def max_upsets_occurances(n: int) -> tuple[int, int]:
    """
    Returns the maximum number of upsets for a RRTG on n vertcies along with how many graphs have maximal upsets

    Parameters:
    n (int): The order of the RRTGs being searched

    Returns:
    (
        current_max, (int): The maximum number of upsets of order n
        graph_count (int): Then number RRTGs of order n whos upset count is current_max
    )
    """
    current_max: int = 0
    graph_count: int = 0
    for g in digraphs.tournaments_nauty(n):
        g_upsets = num_upsets(g)
        if current_max == g_upsets:
            graph_count += 1
        if current_max < g_upsets:
            current_max = g_upsets
            graph_count = 1
    return (current_max, graph_count)


def max_upsets_graphs(n: int) -> tuple[int, list[DiGraph]]:
    """
    Returns the maximum number of upsets for a RRTG on n vertcies along with all RRTGs with said many upsets

    Parameters:
    n (int): The order of the RRTGs being searched

    Returns:
    (
        current_max, (int): The maximum number of upsets of order n
        graphs (list[DiGraph]): List of all RRTGs of order n whos upset count is current_max
    )
    """
    current_max: int = 0
    graphs: list[DiGraph] = list()
    for g in digraphs.tournaments_nauty(n):
        g_upsets = num_upsets(g)
        if current_max == g_upsets:
            graphs.append(g)
        if current_max < g_upsets:
            current_max = g_upsets
            graphs = [g]
    return (current_max, graphs)


def stats_up_to(n: int) -> pd.DataFrame:
    """
    Returns a pd.DataFrame stats coresponding to all RRTG of order k where 1 <= k <= n

    Parameters:
    n (int) : The inclusive upper bound of the rows

    Returns:
    df_out (pd.DataFrame) : The pd.DataFrame with n many rows where each column coresponds to a stat of RRTGs of order k, where k is the row number
    """
    n += 1  # Make the upper bound incluseive
    upset_table = np.array(
        [
            np.array(
                list(map(num_upsets, digraphs.tournaments_nauty(k))), dtype=np.uint16
            )
            for k in range(1, n)
        ],
        dtype=object,
    )

    upset_var: np.array[np.float64] = map(
        lambda list: np.var(list, dtype=np.float64), upset_table
    )
    upset_mean: np.array[np.float64] = map(
        lambda list: np.mean(list, dtype=np.float64), upset_table
    )
    upset_max: np.uint16 = map(max, upset_table)

    df_out: pd.DataFrame = pd.DataFrame(
        data={
            "Variance": upset_var,
            "Mean": upset_mean,
            "Max": upset_max,
            "Upset Counts": upset_table,
        },
        index=list(range(1, n)),
    )
    return df_out
