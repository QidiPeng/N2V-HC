##判断是否已经收敛

import argparse
import pandas as pd
import sys

def parse_args():
	parser = argparse.ArgumentParser(description="判断是否已经收敛")
	parser.add_argument('--g1', nargs='?', default='example_data/level-1/network.edgelist.nodeID', help='上一次聚类结果')
	parser.add_argument('--g2', nargs='?', default='example_data/level-2/network.edgelist.nodeID', help='下一次聚类结果')
	return parser.parse_args()
##END

args = parse_args()

gg_1 = pd.read_csv(args.g1, sep='\t', names=['node_x', 'node_y'])
nodelist1 = list(set(set(gg_1['node_x']) | set(gg_1['node_y'])))

gg_2 = pd.read_csv(args.g2, sep='\t', names=['node_x', 'node_y'])
nodelist2 = list(set(set(gg_2['node_x']) | set(gg_2['node_y'])))

if(len(nodelist1) == len(nodelist2)):
    print('constriction')
    sys.exit(0) #表示成功
else:
    print("havn't constriction")
    sys.exit(1) #表示失败


