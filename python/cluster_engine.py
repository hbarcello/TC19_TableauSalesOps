# Simple Territory Clustering Script for use with Tableau Prep or as standalone
# Author : Hunter Barcello [hbarcello@gmail.com or hbarcello@tableau.com]
# Enrichment for 2020 - based on R Script, format of output slightly different
# For 2019 Tableau Conference "Optimizing Sales Territories with Tableau"
# This is not TabPy compatible at this time, functionality to come in later versions.


import pandas as pd
from sklearn.cluster import KMeans


def cluster_generator(input_tab_df, cluster_factor=12, debug=False, round=0):
    target_mean = (input_tab_df['Index'].sum()) / (input_tab_df['Territories'].max())
    if debug:
        print("Target Territory Index is ", "{:.2f}".format(target_mean))
        print(type(target_mean))
        print(input_tab_df.info())
    df_to_cluster = input_tab_df[input_tab_df['Index'] <= (target_mean * 0.65)]
    df_to_pass_through = input_tab_df[input_tab_df['Index'] > (target_mean * 0.65)]
    df_to_pass_through['ClusterName'] = df_to_pass_through['Postal']
    if debug:
        print("Initial Cluster Filtering Completed...")
        print(df_to_cluster.head())
    df_unique_states = df_to_cluster.State.unique()
    df_fn_output = pd.DataFrame(columns=df_to_cluster.columns)
    df_fn_output['ClusterName'] = ""
    for state in df_unique_states:
        if debug: print("Now Clustering", state)
        current_subset = df_to_cluster[df_to_cluster['State'] == state].copy()
        # Ensure at least 2 clusters per state, more if applicable, but no more than total postal codes
        numeric_cluster_maximum = current_subset['Postal'].count() - 1
        numeric_cluster_recommendation = min(int(current_subset.Index.sum() / target_mean) * cluster_factor,
                                             numeric_cluster_maximum)
        estimated_number_clusters = max(numeric_cluster_recommendation, 2)
        if debug: print(estimated_number_clusters, "Estimated Clusters for", state)
        # Only cluster if there is more than one postal code in the group (data quality guard)
        if current_subset['Postal'].count() > 1:
            kmeans = KMeans(n_clusters=estimated_number_clusters)
            state_clusters = kmeans.fit_predict(current_subset[['Latitude', 'Longitude']])
            if debug: print(state_clusters)
            current_subset['ClusterName'] = [state + "." + str(round) + "." + str(c + 1) for c in state_clusters]
        else:
            current_subset['ClusterName'] = state + "." + str(round) + "." + current_subset['Postal']
        clusters_to_breakup = current_subset.groupby('ClusterName').sum()
        clusters_to_breakup = clusters_to_breakup[clusters_to_breakup['Index'] >= target_mean]
        if len(clusters_to_breakup) > 0:
            if debug: print(clusters_to_breakup.index.tolist())
            temporary_cluster_subset = current_subset[
                current_subset.ClusterName.isin(clusters_to_breakup.index.tolist())]
            # Delete Rows From Temporary Cluster Subset
            current_subset = current_subset.drop(
                current_subset[current_subset.ClusterName.isin(clusters_to_breakup.index.tolist())].index)
            output_clusters_second_rnd = cluster_generator(temporary_cluster_subset, round=round + 1, debug=True)
            current_subset = pd.concat([current_subset, output_clusters_second_rnd])
        if not df_fn_output.empty:
            df_fn_output = pd.concat([current_subset, df_fn_output])
        else:
            df_fn_output = current_subset

    if debug:
        print("----Example Data Output----")
        print(df_fn_output.head())
    # Take postal codes that were too large, calculate their postal as their cluster
    # then union back into clustered data
    df_fn_output = pd.concat([df_fn_output, df_to_pass_through])
    return df_fn_output


def cluster_writer(clustered_df_to_write, output_file_loc):
    clustered_df_to_write.to_excel(output_file_loc, sheet_name="main", index_label=False, index=False)


def cluster_input(input_file_loc):
    input_df = pd.read_csv(input_file_loc)
    return input_df


if __name__ == "__main__":
    input_file = "./test/example_input_cluster.csv"
    output_file = "./test/example_outputs.xlsx"
    input_data_frame = cluster_input(input_file)
    cluster_writer(cluster_generator(input_data_frame, cluster_factor=12, debug=True), output_file)
