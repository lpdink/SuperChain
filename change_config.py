import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", required=False, default=None)
parser.add_argument("--node_nums", required=False, default=None)
args = parser.parse_args()

if args.batch_size is not None:
    with open("./resources/config.json", "r") as file:
        dic = json.load(file)
    dic["consensus"]["batch_size"] = int(args.batch_size)
    with open("./resources/config.json", "w") as file:
        json.dump(dic, file, indent=4)

if args.node_nums is not None:
    with open("./resources/consensus_node.json", "r") as file:
        dic = json.load(file)
    dic["nodes_group"][0]["nums"] = int(args.node_nums)
    with open("./resources/consensus_node.json", "w") as file:
        json.dump(dic, file, indent=4)