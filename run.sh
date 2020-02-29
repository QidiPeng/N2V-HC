#!bin/bash

#Each line of the input file is separated by '\t'.
#diseaseSNP:[proxySNP, indeSNP, disease]
#eqtl.edgelist:[gene, SNP]
#gene.edgelist:[node_x, node_y]


iteration=10 #迭代次数
dir="example-network/" #目录

##数据预处理：将(proxy SNP,eGene)转化为(independent SNP, eGene)，并做全局embedding
echo "pre-process network data"
pre_dir=$dir"pre-processing/"
mkdir $pre_dir
python3 src/pre-process.py --input $dir --output $pre_dir
python2 node2vec-master/src/main.py --input $pre_dir"network.edgelist.nodeID" --output $pre_dir"network.emb"
sed -i '1d' $pre_dir"network.emb"


##迭代的提取包含eSNP和eGene的子图，并在其上做embedding和hierarchical clustering，并将结果写入文件
new_dir=$pre_dir
for((i = 1; i <= $iteration; i++));
do
echo -e "\n"$i"th iteration"

##目录更新
old_dir=$new_dir
new_dir=$dir"iteration-"$i"/"
mkdir $new_dir

##提取子图
##get subgraph contains node(SNP and gene) in disease module
echo -e "\nextract subgraph."
python3 src/extract-subgraph.py --network $pre_dir --input $old_dir --output $new_dir

##判断是否收敛，收敛则停止
echo -e "\njudge constriction"
if python3 src/judge-stop.py --g1 $old_dir"network.edgelist.nodeID" --g2 $new_dir"network.edgelist.nodeID"; then
	echo "constriction in ${i}th iteration."
	exit 0
else
	echo "continue iteration..."
fi

##层次聚类
##clusting again in subgraph
echo -e "\nhierarchical clustering."
Rscript src/HierarchicalClustering-one-embedding.R -e $pre_dir"network.emb" -g $new_dir"network.edgelist.nodeID" -o $new_dir"network.pred_label" -s 20 -r 2

done

##save result
echo -e "\nsave result."
python3 src/modified-save-result-sorted.py --diseaseSNP $dir"diseaseSNP" --label $new_dir"network.pred_label" --network $pre_dir --output $new_dir"result"

echo -e "\nend"

