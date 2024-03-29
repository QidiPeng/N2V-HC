
'''
## Description: Save results in a certain format.
## Input: The correspondence between SNP and disease, clustering results (representing nodes with nodeID), 
##		  and mapping files between nodeID and node name.
## Output: A file, each line is a cluster result, including SNP node count, gene node count, SNP nodes, and gene nodes in the cluster.
'''

import argparse
import pandas as pd
import scipy.stats as stats
import statsmodels.stats.multitest

def parse_args():
	parser = argparse.ArgumentParser(description="Save Result.")
	parser.add_argument('--diseaseSNP', nargs='?', default='example_data/diseaseSNP', help='疾病与SNP的关系，从左至右依次为[proxySNP,indeSNP,disease]三列')
	parser.add_argument('--label', nargs='?', default='example_data/level-1/network.pred_label', help='预测的cluster文件')
	parser.add_argument('--network', nargs='?', default='example_data/pre-processing/', help='原始网络路径')
	parser.add_argument('--output', nargs='?', default='example_data/level-1/result', help='结果保存路径')
	return parser.parse_args()
##END

args = parse_args()

gg = pd.read_csv(args.network+'network.edgelist.nodeName', sep='\t', names=['node_name_x', 'node_name_y', 'type'])
#eqtl_network = gg.loc[gg['type']=='eqtl', ['node_name_x', 'node_name_y']]
#eqtl_network.columns = ['gene', 'snp']
eqtl_network = pd.read_csv(args.network+'eqtl.edgelist.indeSNP', sep='\t', names=['gene', 'snp'])
nodeID2name = pd.read_csv(args.network+"network.nodeID2name", sep='\t', names=['node_id', 'node_name'])
nodeLabels = pd.read_csv(args.label, sep='\t', names=['node_id', 'class'])
nodeLabels = nodeID2name.merge(nodeLabels, left_on='node_id', right_on='node_id') #[node_id, node_name, class]
#nodeLabels.sort_values(['class', 'node_name'], ascending=[1,1], inplace=True) #sort
diseaseSNP = pd.read_csv(args.diseaseSNP, sep='\t', names=['proxySNP', 'indeSNP', 'disease/trait'])

gg_snpset = set(diseaseSNP['indeSNP']) #independent SNP node
gg_geneset = set(nodeID2name['node_name']) - gg_snpset #gene node
diseaselist = list(set(diseaseSNP['disease/trait'])) #disease
labellist = list(set(nodeLabels['class'])) #labels
num_gg_nodeset= len(set(nodeID2name['node_name']))
num_eGene = len(set(eqtl_network['gene']))
print(num_gg_nodeset, num_eGene)
#PD_familial = pd.read_csv(args.network+'PD-familial', names=['gene'])
#PD_familial = set(PD_familial['gene'])
#print(len(set(PD_familial)), PD_familial)


##set colnums:[module_no, module_size, module_edges, dis1_SNP_count, dis1_eGene_count, dis1_SNP, dis1_eGene, ..., gene]
result = pd.DataFrame(columns=['module_nodes_count', 'module_edges_count', 'density'])
for disease in diseaselist:
	result[disease+'_SNP_count'] = 0
	result[disease+'_eGene_count'] = 0
	result[disease+'_SNP'] = ''
	result[disease+'_eGene'] = ''
result['gene'] = ''
result['p-value'] = 1
result['oddsratio'] = ''
#result['PD-familial-count'] = 0
#result['PD-familial'] = ''

#geneID2symbol = pd.read_csv('gene-ID2symbol', sep='\t', names=['gene_id', 'gene_symbol'])
##calculate for each label
for label in labellist:
	module_nodes = pd.DataFrame(nodeLabels.loc[nodeLabels['class'] == label, 'node_name'])
	module_snpset = list(set(module_nodes['node_name']) & gg_snpset)
	module_geneset = list(set(module_nodes['node_name']) & gg_geneset)
	module = module_nodes.merge(gg, left_on='node_name', right_on='node_name_x')
	module = module_nodes.merge(module, left_on='node_name', right_on='node_name_y')
	module.columns = ['node_name_x', 'node_name_y', 'node_name_xx', 'node_name_yy', 'type']
	module = module[['node_name_x', 'node_name_y']] #module（只含有module节点的子图）

	#each row
	temp = [module_nodes.shape[0], module.shape[0], module.shape[0]/(module_nodes.shape[0]*(module_nodes.shape[0]-1)/2)] #module的节点集大小，边集大小
	for disease in diseaselist:
		disease_snpset = pd.DataFrame(diseaseSNP.loc[diseaseSNP['disease/trait'] == disease, 'indeSNP'])
		disease_eqtl = eqtl_network.merge(disease_snpset, left_on='snp', right_on='indeSNP')
		disease_geneset = set(disease_eqtl['gene'])
		disease_snpset = set(disease_snpset['indeSNP'])
#		disease_module_snpset = list(disease_snpset & set(module_snpset))
		disease_module_genelist = list(disease_geneset & set(module_geneset))
		tmp = pd.DataFrame(disease_module_genelist, columns=['gene'])
		disease_module_snplist = tmp.merge(eqtl_network,  left_on='gene', right_on='gene')
		disease_module_snplist = list(set(disease_module_snplist['snp']))
		temp += [len(disease_module_snplist), len(disease_module_genelist), ",".join(disease_module_snplist), ",".join(disease_module_genelist)]
	temp += [",".join(module_geneset)] #module gene set
	fisher_test_matrix = [[len(disease_module_genelist), num_eGene-len(disease_module_genelist)], [module_nodes.shape[0]-len(disease_module_genelist), num_gg_nodeset-num_eGene-module_nodes.shape[0]+len(disease_module_genelist)]]
	oddsratio, pvalue = stats.fisher_exact(fisher_test_matrix)
#	temp += [pvalue, oddsratio, len(set(module_geneset) & PD_familial), ",".join(list(set(module_geneset) & PD_familial))]
	temp += [pvalue, oddsratio]
	print(label, ' : ', fisher_test_matrix)
	result = pd.concat([result, pd.DataFrame([temp], columns=result.columns)]) #insert row

fdr = statsmodels.stats.multitest.multipletests(result['p-value'], method = 'fdr_bh', is_sorted = False)
result['FDR'] = fdr[1]

##save result
result.sort_values(['p-value'], ascending=[1], inplace=True) #sort
result.insert(0, 'label', list(range(1, result.shape[0]+1, 1))) #insert col
result.to_csv(args.output, sep='\t', index=False, header=True) 

