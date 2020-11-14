import cluster_engine as ce
import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
import itertools
import numpy as np
from scipy.spatial import cKDTree
from operator import itemgetter
import random
import math

debug = False


def cluster_allocator(user_input_df, n_territories=9, starting_temperature=1500, decay_rate=.5, iterations=50000):
    # Field Maps from cluster_engine
    # ClusterName | Index | Latitude | Longitude
    allocation_frame = user_input_df.groupby('ClusterName').agg({'Index': 'sum', 'Latitude': 'mean',
                                                                 'Longitude': 'mean'}).reset_index()

    print(allocation_frame)
    # settings for annealing
    initial_temp = starting_temperature
    final_temp = 1
    current_temp = initial_temp
    km = KMeans(n_clusters=n_territories)
    territory_seed = km.fit_predict(allocation_frame[['Latitude', 'Longitude']])
    allocation_frame['Territory'] = territory_seed
    territory_target = allocation_frame.Index.sum() / n_territories
    best_sse = balance_calculator(target=territory_target, territory_data_frame=allocation_frame)
    print(f"Seeding SSE is {best_sse}")
    print(f"Beginning Annealing...")
    while iterations > 0:
        config_to_eval = swap_neighbors(allocation_frame, get_neighbors(allocation_frame))
        # print(current_temp, " Current Temperature")
        # print(balance_calculator(territory_target, config_to_eval))
        incumbent_sse = balance_calculator(territory_target, config_to_eval)
        if incumbent_sse <= best_sse:
            best_sse = incumbent_sse
            print(f"New Optimum, new best SSE is {best_sse}")
            allocation_frame = config_to_eval
            best_frame = config_to_eval # Stash the best dataframe seen so far to export to CSV
        # elif (math.e ** -(incumbent_sse - best_sse) / current_temp) >= random.randint(0,40):
        # Trying to work on how to create a reasonable probability decay curve, but this is a placeholder.
        elif random.randint(0,40) == 0:
            print("Trying a random config")
            allocation_frame = config_to_eval

        current_temp = current_temp * decay_rate
        iterations -= 1
        if iterations % 100 == 0: print(iterations, " iterations left")
    # TODO Drop Index from allocation_frame before joining
    # TODO  Drop Territories from user_input_df before joining
    final_frame = pd.merge(left=user_input_df, right=best_frame, how="left", on='ClusterName')
    return final_frame


def balance_calculator(target, territory_data_frame):
    balance_grouped = territory_data_frame.groupby('Territory').agg({'Index': 'sum'}).reset_index()
    balance_grouped['Target'] = target
    balance_grouped['SquaredError'] = (balance_grouped['Target'] - balance_grouped['Index']) ** 2
    return balance_grouped['SquaredError'].sum()


def get_neighbors(territory_data_frame):
    neighbor_df = gpd.GeoDataFrame(territory_data_frame, geometry=gpd.points_from_xy(territory_data_frame.Longitude,
                                                                                     territory_data_frame.Latitude))
    # Select Random Territory to give a cluster, must have more than 1 cluster
    territory_count = neighbor_df.groupby('Territory').count().reset_index()
    territory_count = territory_count[territory_count['Index'] > 1]
    territory_select = random.choice(territory_count['Territory'].to_list())
    # Create DataFrames to Receive and Give
    receiving_df = neighbor_df.loc[neighbor_df['Territory'] != territory_select]
    giving_df = neighbor_df.loc[neighbor_df['Territory'] == territory_select]
    distance_output = (ckdnearest( giving_df, receiving_df))
    # TODO LOGIC NEEDS TO GO HERE TO MAKE SURE TERRITORIES ARE NOT REDUCED PAST 0
    swap_to_make = distance_output.loc[distance_output['dist'].idxmin()]
    return swap_to_make[4], swap_to_make[6]


def swap_neighbors(territory_data_frame, new_territory_num):
    if debug: print(f"Swapping Cluster {new_territory_num[1]} to Territory {new_territory_num[0]}")
    territory_data_frame.loc[(territory_data_frame['ClusterName'] == new_territory_num[1]), 'Territory'] = new_territory_num[0]
    return territory_data_frame


def ckdnearest(gdfA, gdfB, gdfB_cols=['ClusterName']):
    # resetting the index of gdfA and gdfB here.
    gdfA = gdfA.reset_index(drop=True)
    gdfB = gdfB.reset_index(drop=True)
    A = np.concatenate(
        [np.array(geom.coords) for geom in gdfA.geometry.to_list()])
    B = [np.array(geom.coords) for geom in gdfB.geometry.to_list()]
    B_ix = tuple(itertools.chain.from_iterable(
        [itertools.repeat(i, x) for i, x in enumerate(list(map(len, B)))]))
    B = np.concatenate(B)
    ckd_tree = cKDTree(B)
    dist, idx = ckd_tree.query(A, k=1)
    idx = itemgetter(*idx)(B_ix)
    gdf = pd.concat(
        [gdfA, gdfB.loc[idx, gdfB_cols].reset_index(drop=True),
         pd.Series(dist, name='dist')], axis=1)
    return gdf


if __name__ == "__main__":
    input_file = "./test/example_input_cluster.csv"
    input_data_frame = ce.cluster_input(input_file)
    input_df = ce.cluster_generator(input_data_frame, cluster_factor=20, debug=False)
    cluster_allocator(user_input_df=input_df).to_csv("./test_output_data.csv")
