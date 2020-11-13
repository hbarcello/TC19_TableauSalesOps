import cluster_engine as ce
import pandas as pd
from sklearn.cluster import KMeans


def cluster_allocator(user_input_df, n_territories=10, n_iterations=500, decay_rate=0.05):
    # Field Maps from cluster_engine
    # ClusterName | Index | Latitude | Longitude
    allocation_frame = user_input_df.groupby('ClusterName').agg({'Index': ['sum'], 'Latitude': ['mean'],
                                                                 'Longitude': ['mean']}).reset_index()
    print(allocation_frame)
    km = KMeans(n_clusters=n_territories)
    territory_seed = km.fit_predict(allocation_frame[['Latitude', 'Longitude']])
    allocation_frame['Territory'] = territory_seed
    print(allocation_frame)
    territory_target = allocation_frame.Index.sum() / n_territories
    balance_calculator(target=territory_target, territory_data_frame=allocation_frame)
    return allocation_frame


def balance_calculator(target, territory_data_frame):
    # Group by "Territory"
    # Calculate Sum Square Errors of Territory Index - Target
    # Return SSE
    return 0.0


if __name__ == "__main__":
    input_file = "./test/example_input_cluster.csv"
    output_file = "./test/example_outputs.xlsx"
    input_data_frame = ce.cluster_input(input_file)
    input_df = ce.cluster_generator(input_data_frame, cluster_factor=12, debug=False)
    cluster_allocator(user_input_df=input_df)
