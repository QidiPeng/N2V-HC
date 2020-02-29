##提取eSNP和eGene所在的模块子图，作为本次迭代过程中使用的网络


import argparse
import pandas as pd
import numpy as np
import networkx as nx
#from collections import Counter

def parse_args():
	parser = argparse.ArgumentParser(description="get subgraph contains node in disease-module")
	parser.add_argument('--network', nargs='?', default='example_data/pre-processing/', help='原始网络存储路径')
	parser.add_argument('--input', nargs='?', default='example_data/level-1/', help='上一次迭代的存储路径')
	parser.add_argument('--output', nargs='?', default='example_data/level-2/', help='本次迭代结果保存路径')
	return parser.parse_args()
##END

args = parse_args()

gg_nodeID = pd.read_csv(args.input+'network.edgelist.nodeID', sep='\t', names=['node_id_x', 'node_id_y']) #[node_id_x, node_id_y]
nodeID2class = pd.read_csv(args.input+'network.pred_label', names=['node_id', 'class'], sep='\t')

####
eGene = pd.read_csv(args.network+'eGene.nodeID2name', sep='\t', names=['node_name', 'node_id'])
eGene = eGene.merge(nodeID2class, left_on='node_id', right_on='node_id')
modulelist = list(set(eGene['class']))
print('eGene occured in %d modules(total %d modules)'%(len(modulelist), max(list(set(nodeID2class['class'])))))
print('module list:', modulelist)

nodelist = []
for label in modulelist:
	nodelist += list(set(nodeID2class.loc[nodeID2class['class'] == label, 'node_id']))
nodelist = pd.DataFrame(list(set(nodelist)), columns = ['node_id'])
print('total %d nodes(%d eGene).'%(nodelist.shape[0], len(set(nodelist['node_id']) & set(eGene['node_id']))))


#gg_nodeID = pd.read_csv(args.network, sep='\t', names=['node_id_x', 'node_id_y']) #[node_id_x, node_id_y]
subgraph = gg_nodeID.merge(nodelist, left_on='node_id_x', right_on='node_id')
subgraph = subgraph.merge(nodelist, left_on='node_id_y', right_on='node_id')
subgraph.columns = ['node_id_x', 'node_id_y', 'node_x', 'node_y']
subgraph = subgraph[['node_id_x', 'node_id_y']]
subgraph.to_csv(args.output+'network.edgelist.nodeID', sep='\t', header=False, index=False)
tmp = set(subgraph['node_id_x']) | set(subgraph['node_id_y'])
print('subgraph has %d nodes(%d eGene) and %d edges.'%(len(set(subgraph['node_id_x']) | set(subgraph['node_id_y'])), len(tmp & set(eGene['node_id'])), subgraph.shape[0]))

