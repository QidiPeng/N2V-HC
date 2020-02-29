

'''
## 描述：将(proxy SNP, eGene)转化到(independent SNP, eGene)；融合eQTL network和gene network；为每个节点赋予一个node_id及label.
## Description: Fusion eQTL network and gene network and convert it to nodeID (node2vec input format).
## Input: 
## Output: 
## Note: Some intermediate files, such as nodeID2name, will be generated, which will be used for subsequent operations.
'''

import argparse
import pandas as pd
import networkx as nx

def parse_args():
	parser = argparse.ArgumentParser(description="数据预处理")
	parser.add_argument('--input', nargs='?', default='example_data/', help='原始数据路径')
	parser.add_argument('--output', nargs='?', default='example_data/pre-processing/', help='结果路径')
	return parser.parse_args()
##END

##Reading parameters.
args = parse_args()
gg = nx.Graph()


## 1. transform (proxy SNP, gene) to (independent SNP, gene).
eqtl_edgelist = pd.read_csv(args.input+'eqtl.edgelist', sep='\t', names=['node_x', 'node_y'])
diseaseSNP = pd.read_csv(args.input+'diseaseSNP', sep='\t', names=['proxySNP', 'indeSNP', 'disease/trait'])
eqtl_edgelist = eqtl_edgelist.merge(diseaseSNP, left_on='node_y', right_on='proxySNP')
eqtl_edgelist = eqtl_edgelist[['node_x', 'indeSNP']]
eqtl_edgelist.columns = ['node_x', 'node_y']
eqtl_edgelist.drop_duplicates(inplace=True)
eqtl_edgelist.to_csv(args.output+'eqtl.edgelist.indeSNP', sep='\t', header=False, index=False)
print('independent eqtl edgelist legnth:', eqtl_edgelist.shape[0])


## 2. merge eQTL network and gene network
## read gene network
gene_edgelist = []
fp = open(args.input+'gene.edgelist', 'r')
for line in fp:
	line = line.strip('\n').split('\t')
	gene_edgelist.append(line)
fp.close()
print('genelist length:', len(gene_edgelist))

## read eQTL network
eqtl_edgelist = []
fp = open(args.output+'eqtl.edgelist.indeSNP', 'r')
for line in fp:
	line = line.strip('\n').split('\t')
	eqtl_edgelist.append(line)
fp.close()
print('eqtllist length:', len(eqtl_edgelist))

## merge network
gg.clear()
gg.add_edges_from(gene_edgelist)
gg.add_edges_from(eqtl_edgelist)
print('network has %d nodes and %d edges'%(len(gg.nodes()), len(gg.edges())))
network_edgelist = pd.DataFrame(gg.edges(), columns=['node_x', 'node_y'])
network_edgelist.to_csv(args.output+'network.edgelist.nodeName', sep='\t', header=False, index=False)


## 3. project node_name to node_id
nodes = pd.DataFrame(gg.nodes(), columns=['node_name'])
nodeID2name = pd.concat([pd.DataFrame(list(range(1, nodes.shape[0]+1, 1)), columns=['node_id']), nodes], axis=1)
nodeID2name.to_csv(args.output+'network.nodeID2name', sep='\t', header=False, index=False)


## 4. transform node_name in network to node_id
network_edgelist = network_edgelist.merge(nodeID2name, left_on='node_x', right_on='node_name')
network_edgelist = network_edgelist.merge(nodeID2name, left_on='node_y', right_on='node_name')
network_edgelist = network_edgelist[['node_id_x', 'node_id_y']]
network_edgelist.to_csv(args.output+'network.edgelist.nodeID', sep='\t', header=False, index=False)


## 5. give each node a class
pred_label = pd.DataFrame(list(range(1, nodes.shape[0]+1, 1)), columns=['node_id'])
pred_label['class'] = 1
pred_label.to_csv(args.output+'network.pred_label', sep='\t', header=False, index=False)


## 6. save eqtl node by node_id and node_name
'''
eqtl_edgelist = pd.DataFrame(eqtl_edgelist, columns=['node_x', 'node_y'])
eqtl_nodelist = list(set(eqtl_edgelist['node_x']) | set(eqtl_edgelist['node_y']))
eqtl_nodelist = pd.DataFrame(eqtl_nodelist, columns=['node_name'])
eqtl_nodelist = nodeID2name.merge(eqtl_nodelist, left_on='node_name', right_on='node_name')
eqtl_nodelist.to_csv(args.output+"eqtl.nodeID2name", sep='\t', header=False, index=False)
print('eqtl_nodelist.shape:', eqtl_nodelist.shape)
'''
eqtl_edgelist = pd.DataFrame(eqtl_edgelist, columns=['node_x', 'node_y'])
eGene = list(set(eqtl_edgelist['node_x']))
eGene = pd.DataFrame(eGene, columns=['node_name'])
eGene = eGene.merge(nodeID2name, left_on='node_name', right_on='node_name')
eGene.to_csv(args.output+'eGene.nodeID2name', sep='\t', header=False, index=False)
print('eGene.shape:', eGene.shape)


