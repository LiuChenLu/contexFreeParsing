#!/usr/bin/env python
from __future__ import division
from collections import defaultdict
import subprocess
import json
import string
import cProfile

#a context free grammar based on data in filename
class Dataset():
    def __init__(self, filename):
        # set of non terminal symbols (e.g. NP,verb,noun)
        self.N=defaultdict(int)
        # set of terminal symobls (e.g. the dog, ran, chick)
        self.Sig=defaultdict(int)
        # start symbol
        self.S='SBARQ'
        # set of unary rules (e.g. noun -> dog)
        self.UR=defaultdict(int)
        #set of binary rules (e.g. NP->adjective noun)
        self.BR=defaultdict(int)

        #build a contex free gramar from the given tree bank
        counts=open(filename,'r')
        #now to fill in the skeleton of context free grammar
        for line in counts:
            r = line.split()
            n = int(r[0])
            rule_type,rule = r[1], tuple(r[2:])
            if rule_type=='NONTERMINAL':
                self.N[rule[0]]=n # string.atoi(n,base=10)
            elif rule_type=='UNARYRULE' :
                self.UR[rule]=n
                self.Sig[rule[1]]+=n
            elif rule_type=='BINARYRULE':
                self.BR[rule]=n
            else:
                pass
        counts.close()

        #these are punctuations we make note of
        self.punc=['?','.','``','<','<<',':',',']
        self.fakepunc=['U.S.','St.','<s']
        # TODO

    def probXYY(self,X,Y1,Y2):
        """
        probXYY(X,Y1,Y2) finds 
        probability(X->Y1 Y2)=count(X->Y1 Y2)/count(X)"""
        top=self.BR[X,Y1,Y2]
        bottom=self.N[X]
        if bottom==0:
            return 0
        else:
            return top/bottom

    def probXw(self,X,w):
        """probXw(X,w) finds probability(X->w)=count(X->W)/count(X)"""
        top=self.UR[X,w]
        bottom=self.N[X]
        if bottom==0:
            return 0
        else:
            return top/bottom


class CKY():
    def __init__(self, data):
        self.data = data
        self.dynamicbp=defaultdict(list)
        self.dynamicpi=defaultdict(int)
        self.dynamictf=defaultdict(lambda:False)

    def parse(self,sentence):
        """
        parse takes a sentence and returns the most likely parse based
        on contex free gramar
        """
        self.dynamicbp=defaultdict(list)
        self.dynamicpi=defaultdict(int)
        self.dynamictf=defaultdict(lambda:False)

        #use isinstance(sentence,"str") LOOKUP
        if type(sentence)==str:
            sentencelist=sentence.split() 
            #an artificial condition says that there is a space separating 
            #punctuation from other words
            sentencelist=map(lambda x: '_RARE_' if self.data.Sig[x]==0 else x,
                             sentencelist)
            newpi,newbp = self.findRules(i=0, 
                                         j=len(sentencelist)-1,
                                         sentence=sentencelist)
            return newbp
        else:
            print("error, your sentence is not a string \
                    and you smell like a monkey's butt")
            
    def findRules(self,
                  i=None,       #start, int
                  j=None,       #end, int
                  sentence=None,#list of strings
                  overrule=None #over arching rule
                 ):
        """
        internal helper function to cky. findRules finds the 
        appropriate binary or uniary rules to send to recursivePi. 
        Mutually recursive with recursivePi
        """

        maxpi=0
        maxbp=[]
        if i==j:
            if overrule==None:
                relevantUR=[elem for elem in self.data.UR if elem[1]==sentence[i]]
            else:
                relevantUR=[(overrule,sentence[i])]
            for rule in relevantUR:
                newpi,newbp=self.recursivePi(i,j,rule,sentence)
                if newpi>maxpi:
                    maxpi=newpi
                    maxbp=newbp
        else:
            if overrule==None:
                relevantBR=self.data.BR
            else:
                relevantBR=[elem for elem in self.data.BR if elem[0]==overrule]

            for rule in relevantBR:
                newpi,newbp=self.recursivePi(i,j,rule,sentence)
                if newpi>maxpi:
                    maxpi=newpi
                    maxbp=newbp
                self.dynamictf[i,j,rule]=True
                self.dynamicpi[i,j,rule]=maxpi
                self.dynamicbp[i,j,rule]=maxbp
        return maxpi,maxbp

    def recursivePi(self,i,j,rule,sentence):
        """internal helper function to cky. it iterates through all
        positions, looking for the maximal application of rule to 
        segment i to j of sentence. mutually recursive with findRules
        """
        if self.dynamictf[i,j,rule]:
            maxpi=self.dynamicpi[i,j,rule]
            maxbp=self.dynamicbp[i,j,rule]
        else:
            if i==j:
                maxpi=self.data.probXw(*rule)
                maxbp=list(rule)
            else:
                maxpi=0
                maxbp=[]
                newpi=0
                for pos in range(i,j):
                    lpi,lbp=self.findRules(i=i,j=pos,
                                           sentence=sentence,
                                           overrule=rule[1])
                    rpi,rbp=self.findRules(i=pos+1,j=j,
                                           sentence=sentence,
                                           overrule=rule[2])
                    #print rule,lbp,rbp
                    newpi = lpi*rpi*self.data.probXYY(*rule)
                    if newpi>maxpi:
                        maxpi=newpi
                        maxbp=[rule[0],lbp,rbp]
            self.dynamicpi[i,j,rule]=maxpi
            self.dynamicbp[i,j,rule]=maxbp
            self.dynamictf[i,j,rule]=True
        return maxpi,maxbp

if __name__=="__main__":
#    dataset=Dataset('parse_train.counts.out')
#    parser = CKY(dataset)
#    print parser.parse("When was the _RARE_ invented ?")
    #cProfile.run ('parser.parse("When was the _RARE_ invented ?")')

    import sys
    countfile=sys.argv[1]
    sentencefile=sys.argv[2]

    dataset=Dataset(countfile)
    parser=CKY(dataset)

    sentences=open(sentencefile,'r')
    for sentence in sentences:
        print parser.parse(sentence)
