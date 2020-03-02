# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import networkx as nx


def parse_args():
	parser = argparse.ArgumentParser(description="Extract subgraph containing modules which include eGene.")
	parser.add_argument('--network', nargs='?', default='example_data/network/', help='Original network data directory')
	parser.add_argument('--input', nargs='?', default='example_data/iteration-1/', help='Last iteration data directory')
	parser.add_argument('--output', nargs='?', default='example_data/iteration-2/', help='This iteration data directory')
	return parser.parse_args()
##END

args = parse_args()

gg_nodeID = pd.read_csv(args.input+'network.edgelist.nodeID', sep='\t', names=['node_id_x', 'node_id_y']) 
nodeID2class = pd.read_csv(args.input+'network.pred_label', names=['node_id', 'class'], sep='\t')

eGene = pd.read_csv(args.network+'eGene.nodeID2name', sep='\t', names=['node_name', 'node_id'])
eGene = eGene.merge(nodeID2class, left_on='node_id', right_on='node_id')
modulelist = list(set(eGene['class']))
print 'eGene occured in %d modules(total %d modules)'%(len(modulelist), max(list(set(nodeID2class['class']))))
print 'module list:', modulelist

nodelist = []
for label in modulelist:
	nodelist += list(set(nodeID2class.loc[nodeID2class['class'] == label, 'node_id']))
nodelist = pd.DataFrame(list(set(nodelist)), columns = ['node_id'])
print 'total %d nodes(include %d eGene).'%(nodelist.shape[0], len(set(nodelist['node_id']) & set(eGene['node_id'])))

subgraph = gg_nodeID.merge(nodelist, left_on='node_id_x', right_on='node_id')
subgraph = subgraph.merge(nodelist, left_on='node_id_y', right_on='node_id')
subgraph.columns = ['node_id_x', 'node_id_y', 'node_x', 'node_y']
subgraph = subgraph[['node_id_x', 'node_id_y']]
subgraph.to_csv(args.output+'network.edgelist.nodeID', sep='\t', header=False, index=False)
tmp = set(subgraph['node_id_x']) | set(subgraph['node_id_y'])
print 'subgraph has %d nodes(include %d eGene) and %d edges.'%(len(set(subgraph['node_id_x']) | set(subgraph['node_id_y'])), len(tmp & set(eGene['node_id'])), subgraph.shape[0])

