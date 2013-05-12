#!/usr/bin/env python
import subprocess
import re
from collections import defaultdict
import json
import string

subprocess.call("python count_cfg_freq.py parse_train.dat > cfg.counts",shell=True)

words=defaultdict(int)
rarewords=[]

#open the counts
counts=open('cfg.counts','r+')
for line in counts:
    if re.search('UNARYRULE',line):
        split=line.split()
        words[split[3]]+=string.atoi(split[0],base=10)

for key, value in words.iteritems():
    if value < 5 :
        rarewords.append(key)

ParseTrain=open('parse_train.dat','r')
newParseTrain=open('newparse_train.dat','w')

def NodeEnd(lis):
    if lis[1] in rarewords:
        lis[1]='_RARE_'

def traverse(json):
    for elem in json:
        if type(elem) is list:
            if len(elem)==2:
                NodeEnd(elem)
            else:
                traverse(elem)
        else:
           pass

for line in ParseTrain:
    tree=json.loads(line)
    traverse(tree)
    newParseTrain.write(json.dumps(tree))
    newParseTrain.write('\n')

newParseTrain.close()
ParseTrain.close()

subprocess.call("python count_cfg_freq.py newparse_train.dat > parse_train.counts.out",shell=True)
