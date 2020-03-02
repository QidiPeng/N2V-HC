#!bin/bash

# All input files are separated by '\t', except the result file of node2vec is separated by ' '.
# diseaseSNP file     : [proxySNP, indeSNP, disease]
# eqtl.edgelist file  : [gene, SNP]
# gene.edgelist file  : [node_x, node_y]


iteration=10 #maximum iterations
dir="PD-network/" #data storage directory

echo "pre-process network data"
pre_dir=$dir"network/"
mkdir $pre_dir
# Tag proxy SNPs to independent SNPs and merge network.
python src/pre-process.py --input $dir --output $pre_dir
# Learning node features using node2vec.
python node2vec-master/src/main.py --input $pre_dir"network.edgelist.nodeID" --output $pre_dir"network.emb"
sed -i '1d' $pre_dir"network.emb"


# Iteratively extract module subgraphs containing eGene, and do Hierarchical Clustering on it.
new_dir=$pre_dir
for((i = 1; i <= $iteration; i++));
do
echo -e "\n"$i"th iteration"

# update directory
old_dir=$new_dir
new_dir=$dir"iteration-"$i"/"
mkdir $new_dir

# extract module subgraph
echo -e "\nextract subgraph."
python src/extract-subgraph.py --network $pre_dir --input $old_dir --output $new_dir

# determine if the convergence condition is reached: the number of nodes in the network is no longer changes.
echo -e "\njudge constriction"
if python src/judge-stop.py --g1 $old_dir"network.edgelist.nodeID" --g2 $new_dir"network.edgelist.nodeID"; then
	echo "constriction in ${i}th iteration."
	exit 0
else
	echo "continue iteration..."
fi
##还需要修改，添加迭代次数不等于1

# Hierarchical Clustering using R
echo -e "\nhierarchical clustering."
Rscript src/HierarchicalClustering.R -e $pre_dir"network.emb" -g $new_dir"network.edgelist.nodeID" -o $new_dir"network.pred_label" -s 20 -r 2

done


# Save result
echo -e "\nsave result."
python src/save-result-sorted.py --diseaseSNP $dir"diseaseSNP" --network $pre_dir --label $new_dir"network.pred_label" --output $new_dir"result"

echo -e "\nend"

