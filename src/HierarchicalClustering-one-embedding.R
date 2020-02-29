
## Description: Hierarchical clustering.
## Input: Node feature.
## Output: Clustering results.
## Dependency: WGCNA, getopt.

library(getopt)
library(WGCNA)
#library(dynamicTreeCut)
setwd("E:/workplace/ModularProgram-one-embedding/")
getwd()

##read input parameters
spec <- matrix(c("embedding", 'e', 1, "character", "embedding file",
                 "network", 'g', 1, "character", "network edgelist",
				 "output", 'o',  1, "character", 'output file',
				 "method", "m", 2, "character", "Cut method of hierarchical clustering dendrogram.",
				 "minModuleSize", "s", 20, "integer", "Minimum cluster size.",
				 "deepSplit", "r", 2, "integer", "Rough control over sensitivity to cluster splitting.",
				 "plot", 'p', 2, "logical", "Whether plot ot not."),
			   byrow=TRUE, ncol=5)
args <- getopt(spec=spec)

if(is.null(args$embedding) || is.null(args$output)){
    print("Please set parameter --embedding and --output.")
    quit()
}

##set default parameters
if(is.null(args$method))
	args$method = "hybrid"
if(is.null(args$minModuleSize))
    args$minModuleSize = 20
if(is.null(args$deepSplit))
	args$deepSplit = 2
if(is.null(args$plot))
	args$plot = FALSE

##read node feature
feature = read.table(args$embedding)
feature = feature[sort(feature$V1, index.return = TRUE)$ix, ] #sort by node ID
gg = read.table(args$network, sep='\t')
nodelabel = union(gg[,1], gg[,2]) #本次迭代过程中所有节点
feature = feature[nodelabel,]
feature = feature[sort(feature$V1, index.return = TRUE)$ix, ] #sort by node ID
nodelabel = feature[,1] #保存节点编号
feature = feature[ , -1] #delete node ID
#print(nodelabel)

print("begin hclust")
##clusting, using Euclidean distance.
distance = dist(feature)
tree = hclust(distance, method = "average")
#sizeGrWindow(12,9)
#plot(tree, xlab="", sub="", main = "Network clustering on embedding vectors", labels = FALSE, hang = 0.04)

print("begin cut tree")
##cuthierarchical clustering dendrogram
if(args$method == 'hybrid'){
	dynamicMods = cutreeDynamic(dendro = tree, distM = as.matrix(distance), pamRespectsDendro = FALSE, 
								method = args$method, deepSplit = args$deepSplit, minClusterSize = args$minModuleSize)
}else{
	dynamicMods = cutreeDynamic(dendro = tree, method = args$method, deepSplit = args$deepSplit)
}
table(dynamicMods)

##save clustering results
labels = as.matrix(dynamicMods)
labels = cbind(nodelabel, labels[,1])
#colnames(labels) = c("nodeID", "pred_label")
write.table(labels, args$output, row.names = FALSE, col.names = FALSE, sep = "\t")

##plot
if(args$plot == TRUE){
	dynamicColors = labels2colors(dynamicMods)
	table(dynamicColors)
	sizeGrWindow(8,6)
	plotDendroAndColors(tree, dynamicColors, "Dynamic Tree Cut by Hybrid Method", 
						dendroLabels = FALSE, hang = 0.03, addGuide = TRUE, guideHang = 0.05, 
						main = "Gene dendrogram and module colors") 
} #Set "dendroLabels=NULL" to display node names in the diagram.

