# Simple Territory Clustering Script for use with Tableau Prep or as standalone
# Author : Hunter Barcello [hbarcello@gmail.com or hbarcello@tableau.com]
# Enrichment for 2020 - based on R Script, format of output slightly different
# For 2019 Tableau Conference "Optimizing Sales Territories with Tableau"
# This is not TabPy compatible at this time, functionality to come in later versions.

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import random
pd.options.mode.chained_assignment = None

def cluster_generator(input_tab_df, cluster_factor=12, cluster_field='State', target_territories=8,
                      debug=False, row_unit='Postal', balance_unit='Index', sub_cluster='None', cluster_round=0):

    df_to_cluster = input_tab_df[input_tab_df['Territories'] > 1].copy()
    df_to_pass_through = input_tab_df[input_tab_df['Territories'] <= 1].copy()
    df_to_pass_through['ClusterName'] = df_to_pass_through['State']

    if debug:
        print("Initial Cluster Filtering Completed...")
        print(df_to_cluster.head())
    df_unique_states = df_to_cluster[cluster_field].unique()
    df_fn_output = pd.DataFrame(columns=df_to_cluster.columns)
    df_fn_output['ClusterName'] = ""
    for state in df_unique_states:
        if debug: print("Now Clustering", state)
        current_subset = df_to_cluster[df_to_cluster[cluster_field] == state].copy()
        target_territories = current_subset['Territories'].max()
        cluster_factor = current_subset['Clusters'].max()
        # Ensure at least 2 clusters per state, more if applicable, but no more than total postal codes
        numeric_cluster_maximum = current_subset[row_unit].count() - 1
        target_mean = (current_subset['Index'].sum() / target_territories)
        units_to_skip_clustering = current_subset[current_subset['Index'] > (target_mean * 0.9)]
        units_to_skip_clustering['ClusterName'] = units_to_skip_clustering.loc[:, ['Postal']]
        df_to_pass_through = pd.concat([df_to_pass_through, units_to_skip_clustering])
        current_subset = current_subset[current_subset['Index'] <= (target_mean * 0.9)]

        if debug:
            print("Target Territory Index is ", "{:.2f}".format(target_mean))
            print(type(target_mean))
            print(current_subset.info())

        numeric_cluster_recommendation = min(int(current_subset.Index.sum() / target_mean) * cluster_factor,
                                             numeric_cluster_maximum)
        estimated_number_clusters = max(numeric_cluster_recommendation, 2)
        # If Clusters are greater than unique latitude + longitude combinations, add random digits to end of lat-long
        if current_subset['Latitude'].nunique() < estimated_number_clusters:
            if estimated_number_clusters > current_subset.count()[0]:
                estimated_number_clusters = current_subset.count()[0] - 1
            else:
                for x, row in current_subset.iterrows():
                    current_subset.at[x, 'Latitude'] = row.Latitude + random.randint(1, 9999)/100000.0
                    current_subset.at[x, 'Longitude'] = row.Longitude + random.randint(1, 9999)/100000.0

        if debug: print(estimated_number_clusters, "Estimated Clusters for", state)
        # Only cluster if there is more than one postal code in the group (data quality guard)
        if current_subset[row_unit].count() > 1:
            kmeans = KMeans(n_clusters=estimated_number_clusters)
            state_clusters = kmeans.fit_predict(current_subset[['Latitude', 'Longitude']])
            if debug: print(state_clusters)
            current_subset['ClusterName'] = [state + "." + str(cluster_round) + "." + str(c + 1) for c in
                                             state_clusters]
        else:
            current_subset['ClusterName'] = state + "." + str(cluster_round) + "." + str(current_subset[row_unit])
        clusters_to_breakup = current_subset.groupby('ClusterName').sum()
        clusters_to_breakup = clusters_to_breakup[clusters_to_breakup['Index'] >= target_mean]
        if len(clusters_to_breakup) > 0:
            if debug: print(clusters_to_breakup.index.tolist())
            temporary_cluster_subset = current_subset[
                current_subset.ClusterName.isin(clusters_to_breakup.index.tolist())]
            # Delete Rows From Temporary Cluster Subset
            current_subset = current_subset.drop(
                current_subset[current_subset.ClusterName.isin(clusters_to_breakup.index.tolist())].index)
            output_clusters_second_rnd = cluster_generator(temporary_cluster_subset, cluster_factor=cluster_factor,
                                                           cluster_field=cluster_field,
                                                           target_territories=target_territories, row_unit=row_unit,
                                                           balance_unit=balance_unit,
                                                           cluster_round=cluster_round + 1)
            current_subset = pd.concat([current_subset, output_clusters_second_rnd])

        df_fn_output = pd.concat([current_subset, df_fn_output])
    if debug:
        print("----Example Data Output----")
        print(df_fn_output.head())
    # Take postals that were too large, calculate their postal as their cluster
    # then union back into clustered data
    df_fn_output = pd.concat([df_fn_output, df_to_pass_through])
    return df_fn_output


def cluster_writer(clustered_df_to_write, output_file_loc):
    clustered_df_to_write.to_excel(output_file_loc, sheet_name="main", index_label=False, index=False)
    print("...Output file successfully written")


def cluster_input(input_file_loc):
    input_df = pd.read_csv(input_file_loc)
    print("...Input file successfully read")
    return input_df


if __name__ == "__main__":
    input_file = "./test/example_input_cluster.csv"
    output_file = "./test/example_outputs.xlsx"
    input_data_frame = cluster_input(input_file)
    cluster_writer(cluster_generator(input_data_frame, cluster_factor=12, debug=True), output_file)
