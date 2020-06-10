import argparse
import cluster_engine


parser = argparse.ArgumentParser(description="Employee Acct Routing")
parser.add_argument("--ClusterInputFile", type=str, help="Location of input file")
parser.add_argument("--outputLocation", type=str, help="Location of output file")
args = parser.parse_args()

if args.ClusterInputFile is None and args.outputLocation is None:
    print("Both Input and Output Location Arguments are required")
elif args.ClusterInputFile is None or args.outputLocation is None:
    print("Both Input and Output Location Arguments are required")

else:
    input_postal_data = cluster_engine.cluster_input(args.ClusterInputFile)
    cluster_engine.cluster_writer(cluster_engine.cluster_generator(input_postal_data), args.outputLocation)