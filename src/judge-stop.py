# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import sys


def parse_args():
	parser = argparse.ArgumentParser(description="Determine if the convergence condition is reached.")
	parser.add_argument('--g1', nargs='?', default='example_data/iteration-1/network.edgelist.nodeID', help='Last iteration network file')
	parser.add_argument('--g2', nargs='?', default='example_data/iteration-2/network.edgelist.nodeID', help='This iteration network file')
	return parser.parse_args()
##END

args = parse_args()

gg_1 = pd.read_csv(args.g1, sep='\t', names=['node_x', 'node_y'])
nodelist1 = list(set(set(gg_1['node_x']) | set(gg_1['node_y'])))

gg_2 = pd.read_csv(args.g2, sep='\t', names=['node_x', 'node_y'])
nodelist2 = list(set(set(gg_2['node_x']) | set(gg_2['node_y'])))

if(len(nodelist1) == len(nodelist2)):
    print 'continue iteration ...'
    sys.exit(0) 
else:
    print "constriction"
    sys.exit(1)

