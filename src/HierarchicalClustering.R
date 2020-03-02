
## Description: Hierarchical clustering.
## Input: Node feature.
## Output: Clustering results.
## Dependency: WGCNA, getopt.

library(getopt)
library(dynamicTreeCut)

##read input parameters
spec <- matrix(c("embedding", 'e', 1, "character", "embedding file",
                 "network", 'g', 1, "character", "network edgelist file",
				 "output", 'o',  1, "character", 'output file',
				 "method", "m", 2, "character", "Cut method of hierarchical clustering dendrogram.",
				 "minModuleSize", "s", 20, "integer", "Minimum cluster size.",
				 "deepSplit", "r", 2, "integer", "Rough control over sensitivity to cluster splitting."),
			   byrow=TRUE, ncol=5)
args <- getopt(spec=spec)

if(is.null(args$embedding) || is.null(args$output)){
    print("Please set parameter --embedding and --output.")
    quit()
}

# set default parameters
if(is.null(args$method))
	args$method = "hybrid"
if(is.null(args$minModuleSize))
    args$minModuleSize = 20
if(is.null(args$deepSplit))
	args$deepSplit = 2


# read node feature
feature = read.table(args$embedding)
feature = feature[sort(feature$V1, index.return = TRUE)$ix, ]
gg = read.table(args$network, sep='\t')
nodelabel = union(gg[,1], gg[,2]) 
feature = feature[nodelabel,]
feature = feature[sort(feature$V1, index.return = TRUE)$ix, ]
nodelabel = feature[,1] 
feature = feature[ , -1] 

print("begin hclust")
# Hierarchical Clustering using Euclidean distance and average method.
distance = dist(feature)
tree = hclust(distance, method = "average")

print("begin cut tree")
# cut dendrogram
if(args$method == 'hybrid'){
	dynamicMods = cutreeDynamic(dendro = tree, distM = as.matrix(distance), pamRespectsDendro = FALSE, 
								method = args$method, deepSplit = args$deepSplit, minClusterSize = args$minModuleSize)
}else{
	dynamicMods = cutreeDynamic(dendro = tree, method = args$method, deepSplit = args$deepSplit)
}
table(dynamicMods)

# save results
labels = as.matrix(dynamicMods)
labels = cbind(nodelabel, labels[,1])
write.table(labels, args$output, row.names = FALSE, col.names = FALSE, sep = "\t")


