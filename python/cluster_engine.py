# Simple Territory Clustering Script for use with Tableau Prep or as standalone
# Author : Hunter Barcello [hbarcello@gmail.com or hbarcello@tableau.com]
# Enrichment for 2020 - based on R Script, format of output slightly different
# For 2019 Tableau Conference "Optimizing Sales Territories with Tableau"
# This is not TabPy compatible at this time, functionality to come in later versions.


import pandas as pd
from sklearn.cluster import KMeans


def cluster_generator(input_tab_df, cluster_factor=0.08, debug=False, round=0):
    target_mean = (input_tab_df['Index'].sum()) / (input_tab_df['Territories'].max())
    if debug:
        print("Target Territory Index is ", "{:.2f}".format(target_mean))
        print(type(target_mean))
        print(input_tab_df.info())
    df_to_cluster = input_tab_df[input_tab_df['Index'] <= (target_mean * 0.70)]
    if debug:
        print("Initial Cluster Filtering Completed...")
        print(df_to_cluster.head())
    df_unique_states = df_to_cluster.State.unique()
    df_fn_output = pd.DataFrame(columns=df_to_cluster.columns)
    df_fn_output['ClusterName'] = ""
    for state in df_unique_states:
        if debug: print("Now Clustering", state)
        current_subset = df_to_cluster[df_to_cluster['State'] == state].copy()
        # Ensure at least 2 clusters per state, more if applicable
        estimated_number_clusters = max(int(current_subset.Index.sum() / target_mean), 2)
        if debug: print(estimated_number_clusters, "Estimated Clusters for", state)
        kmeans = KMeans(n_clusters=estimated_number_clusters)
        state_clusters = kmeans.fit_predict(current_subset[['Latitude', 'Longitude']])
        if debug: print(state_clusters)
        current_subset['ClusterName'] = [state + "." + str(round) + "." + str(c+1) for c in state_clusters]
        clusters_to_breakup = current_subset.groupby('ClusterName').sum()
        clusters_to_breakup = clusters_to_breakup[clusters_to_breakup['Index'] >= target_mean]
        if len(clusters_to_breakup) > 0:
            if debug: print(clusters_to_breakup.index.tolist())
            temporary_cluster_subset = current_subset[current_subset.ClusterName.isin(clusters_to_breakup.index.tolist())]
            # Delete Rows From Temporary Cluster Subset
            current_subset = current_subset.drop(current_subset[current_subset.ClusterName.isin(clusters_to_breakup.index.tolist())].index)
            output_clusters_second_rnd = cluster_generator(temporary_cluster_subset, round=round+1)
            current_subset = pd.concat([current_subset, output_clusters_second_rnd])

        df_fn_output = pd.concat([current_subset, df_fn_output])
    if debug:
        print("----Example Data Output----")
        print(df_fn_output.head())
    return df_fn_output


def cluster_writer(clustered_df_to_write, output_file_loc):
    clustered_df_to_write.to_excel(output_file_loc, sheet_name="main", index_label=False)


def cluster_input(input_file_loc):
    input_df = pd.read_csv(input_file_loc)
    return input_df


if __name__ == "__main__":
    input_file = "./test/example_input_cluster.csv"
    output_file = "./test/example_outputs.xlsx"
    input_data_frame = cluster_input(input_file)
    cluster_writer(cluster_generator(input_data_frame, cluster_factor=0.05, debug=True), output_file)
