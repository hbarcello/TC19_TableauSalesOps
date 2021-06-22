import argparse
import cluster_engine


parser = argparse.ArgumentParser(description="Command Line Territory Clustering Tool")
parser.add_argument("--input_file", type=str, help="Location of input file")
parser.add_argument("--output_file", type=str, help="Location of output file")
parser.add_argument("--cluster_by", type=str, default='State', help="Field name to iterate over when clustering (often is State)")
parser.add_argument("--target_territories", type=int, default=10, help='How many territories are desired in end state')
parser.add_argument("--row_unit", type=str, default='Postal', help='Row level unit to cluster by (often is postal code)')
parser.add_argument("--index", type=str, default='Index', help='Field that contains metric to balance on')


args = parser.parse_args()

if args.input_file is None and args.output_file is None:
    print("Both Input and Output Location Arguments are required")
elif args.input_file is None or args.output_file is None:
    print("Both Input and Output Location Arguments are required")
else:
    input_postal_data = cluster_engine.cluster_input(args.input_file)
    cluster_engine.cluster_writer(cluster_engine.cluster_generator(input_tab_df=input_postal_data,
                                                                   cluster_field=args.cluster_by,
                                                                   target_territories=args.target_territories,
                                                                   row_unit=args.row_unit, balance_unit=args.index), args.output_file)
