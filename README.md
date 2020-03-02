# N2V-HC 
**N2V-HC**: A novel method for disease module identification based on deep representation learning of multi-layer biological networks.

## Introduction


## Input
```
'diseaseSNP'     The relationship between disease and SNP, from left to right is proxy SNP, independent SNP, and disease.
'eqtl.edgelist'  eQTL network, one eQTL information per line, gene and SNP from left to right.
'gene.edgelist'  Human intercome network, two vertices per line, representing one edge.
```

## Output
```
'eGene.nodeID2name'          eGene and its nodeID mapping file.
'eqtl.edgelist.indeSNP'      Each line from left to right is gene and SNP, which represents an eQTL information after converted proxy SNP into its corresponding independent SNP.
'eqtl.nodeID2name'           Gene and SNP nodes and their nodeID in the 'eqtl.edgelist.indeSNP' file.
'network.edgelist.nodeName'  The integrated network, with two nodes(node name) per row, represents one edge.
'network.nodeID2name'        The mapping of node name to node ID in the 'network.edgelist.nodeName'.
'network.emb'                Node2vec result file, the file name can be specified by the user.
'network.edgelist.nodeID'    The integrated network, with two nodes(node ID in 'network.nodeID2name' )per row, represents one edge.
'network.pred_label'         Hierarchical clustering result file, one node(node ID) per line and its module.
'result'                     Converged result files, the file name can be specified by the user. From left to right, are module label, module nodes size, module edges size, disease1_SNP__count, disease1_eGene_count, disease1_SNP, disease1_eGene, ..., other gene.
```

## Example
```
## Hierarchical Clustering
Rscript src/HierarchicalClustering.R -e football/embedding -g football/edgelist -o football/pred_label -s 20 -r 2

## execution script
bash run.sh
```

## Contact
If you need help, please contact *ydwang at hit dot edu dot cn*, *jiajiepeng at nwpu at edu at cn* or *1571608336 at qq at com*.

## Full paper
Full paper has been submitted to **Frontiers in Genetics**
