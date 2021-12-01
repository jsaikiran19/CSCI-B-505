###################################
# CS B551 Spring 2021, Assignment #3
#
# Submitted By: Sai Kiran Jella (sjella)
#
# (Based on skeleton code by D. Crandall)
#


import random
import math
import copy
import functools
# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:
    # Calculate the log of the posterior probability of a given sentence
    #  with a given part-of-speech labeling. Right now just returns -999 -- fix this!
    parts_of_speech_tags = set(['adj','adv','adp','conj','det','noun','num','pron','prt','verb','x','.'])
    words_dict = {}
    tags_count = {}
    transition_probs = {}
    transition_dict = {}
    emission_probs = {}
    def posterior(self, model, sentence, label):
        if model == "Simple":
            return self.calculate_probability(sentence,label,model)
        elif model == "HMM":
            return self.calculate_probability(sentence,label,model)
        elif model == "Complex":
            return self.calculate_probability(sentence,label,model)
        else:
            print("Unknown algo!")

    # Do the training!
    #
    def train(self, data):
        for words, labels in data:
            for i in range(len(words)):
                if i==0:
                    self.transition_probs['P0'+labels[i]] = self.transition_probs.get('P0'+labels[i],0)+1

                if i<len(words)-1:
                    transition = (labels[i],labels[i+1])
                    if labels[i] not in self.transition_dict:
                        self.transition_dict[labels[i]] = {transition:1}
                    else:
                        self.transition_dict[labels[i]][transition] = self.transition_dict[labels[i]].get(transition,0)+1

                self.tags_count[labels[i]] = self.tags_count.get(labels[i],0)+1


                if words[i] not in self.words_dict:
                    self.words_dict[words[i]] = {labels[i]:1}
                else:
                    self.words_dict[words[i]][labels[i]] = self.words_dict[words[i]].get(labels[i],0) + 1
        for tag in self.transition_dict: 
            for transition in self.transition_dict[tag]:
                self.transition_probs[transition] = self.transition_dict[tag][transition] / sum(self.transition_dict[tag].values())
            self.transition_probs['P0'+tag] = self.transition_probs.get('P0'+tag,0)/len(data)

    # Functions for each algorithm. Right now this just returns nouns -- fix this!
    #
    def simplified(self, sentence):
        res = []
        most_frequent_tag = max(self.tags_count.items(),key=lambda x:x[1])[0]
        for word in sentence:
            if word not in self.words_dict:
                res.append(most_frequent_tag)
            else:
                probs = []
                for tag in self.parts_of_speech_tags:
                    probs.append((self.words_dict[word].get(tag,0)/sum(self.words_dict[word].values()), tag))

                res.append(max(probs,key=lambda x:x[0])[1])
        return res

    def hmm_viterbi(self, sentence):

        def grammar_rules(word):
            if word[-2:]=='ly':
                return 'adv'
                        
            elif word[-2:]=='ed':
                return 'verb'

            elif word[-2:] in ['ar','er','or']:
                return 'noun'

            elif word[-2:] in ['al','ic']:
                return 'adj'

            elif word[-3:] in ['ist','ion','ity']:
                return 'noun'

            elif word[-3:] in ['ful','ous','ish','ive','ian']:
                return 'adj'
            
            elif word[-3:] in ['ate','ify','ize']:
                return 'verb'
            
            elif word[-4:] in ['less']:
                return 'adj'
            
            elif word[-4:] in [ 'ence','ment','ness','ship','tion','sion']:
                return 'noun'

        res = []
        final_tags = ['-']*len(sentence)
        most_frequent_tag = max(self.tags_count.items(),key=lambda x:x[1])[0]
        possible_hmms = list(self.words_dict.get(sentence[0],{most_frequent_tag:1}).keys())
        initial_tag_keys = list(map(lambda x: (x,self.transition_probs['P0'+x]),self.parts_of_speech_tags))
        highesht_probable_initial_tag = max(initial_tag_keys,key=lambda x:x[1])[0]
        
        
        for i, hmm in enumerate(possible_hmms):
            
            P0 = math.log(self.transition_probs['P0'+hmm])
            hmm_chains = [[(hmm,P0)]]
            # combs = []
            def get_maximum_hmm_path(a1,a2):
                l1 = sum(list(map(lambda x: x[1],a1)))
                l2 = sum(list(map(lambda x: x[1],a2)))
                return l1-l2
            
            k = 0
            for j,word in enumerate(sentence[1:]):
                
                parent_chain = []
                highest_probable_tag_from_prev = ''
            
                

                if word not in self.words_dict:
                    n = len(word)
                    if len(word)>3:
                        grammar_word = grammar_rules(word)
                        if grammar_word:
                            final_tags[j+1] = grammar_word
                    if j==0:
                        prev_word_tag = highesht_probable_initial_tag
                    else:
                        prev_word_tag = max(self.words_dict[sentence[j]],key=lambda x:self.words_dict[sentence[j]][x])

                    highest_probable_tag_from_prev = max(self.transition_dict[prev_word_tag],key=lambda x:self.transition_dict[prev_word_tag][x])[1]

                    self.words_dict[word] = {most_frequent_tag:1}

                # print(self.words_dict[word])
                for tag in (self.words_dict[word]):
                    sub_chain = copy.deepcopy(hmm_chains)
                    for chain in sub_chain:
                        log_prob = math.log(self.transition_probs.get((chain[-1][0],tag),1/len(self.transition_probs)))+math.log(self.words_dict[word][tag]/(self.tags_count[tag]))
                        chain.append((tag,log_prob))
                    if sentence[j] in self.words_dict and len(self.words_dict[sentence[j]])>1:
                        sub_chain = [((max(sub_chain,key=functools.cmp_to_key(get_maximum_hmm_path))))]
                    parent_chain+=(sub_chain)
                

                hmm_chains = parent_chain.copy()
                

                k+=1

            res+=(hmm_chains)
        
        
        
        results = []
        for hmm in res:
            results.append((list(map(lambda x: x[0],hmm)),sum(list(map(lambda x:x[1],hmm)))))
        final_hmm = (max(results,key=lambda x:x[1])[0])
        for i in range(len(final_hmm)):
            if final_tags[i]!='-':
                final_hmm[i] = final_tags[i]
        return final_hmm

    
    def calculate_probability(self,sentence,chain, model='Complex'):
        p = 0
        for i,tag in enumerate(chain):
            if model=='Simple':
                p+=math.log(self.words_dict.get(sentence[i],{tag:1e-10}).get(tag,1e-10)/(self.tags_count[tag]))
            elif i==0:
                p+=math.log(self.transition_probs.get('P0'+tag,1e-10))+math.log(self.words_dict.get(sentence[i],{tag:1e-10}).get(tag,1e-10)/(self.tags_count[tag]))
            elif i==1 or model=='HMM':
                p+=math.log(self.transition_probs.get((chain[i-1],tag),1e-10))+math.log(self.words_dict.get(sentence[i],{tag:1e-10}).get(tag,1e-10)/(self.tags_count[tag]))
            elif model=='Complex':
                p+=math.log(self.transition_probs.get((chain[i-2],chain[i-1]),1e-10))+math.log(self.transition_probs.get((chain[i-1],tag),1e-10))+math.log(self.words_dict.get(sentence[i],{tag:1e-10}).get(tag,1e-10)/(self.tags_count[tag]))
        return p

    def complex_mcmc(self, sentence):
        k = 0
        intial_sample = ['noun']*len(sentence)
        gibbs_samples = [(intial_sample,self.calculate_probability(sentence,intial_sample))]
        
        while k<50:
            hmm = gibbs_samples[-1][0]
            mx_prob = -10000
            for i,word in enumerate(hmm):
                
                for tag in self.parts_of_speech_tags:
                    new_hmm = copy.deepcopy(hmm)
                    new_hmm[i] = tag
                    sentence_prob = self.calculate_probability(sentence,new_hmm)
                    if sentence_prob>mx_prob:
                        mx_prob = sentence_prob
                        hmm[i] = tag
            # if k>30:
            gibbs_samples.append((hmm,self.calculate_probability(sentence,hmm)))
            
            #breaking if the previous three hmms resulted in same predictions
            if k> 2 and gibbs_samples[-1][0]==gibbs_samples[-2][0]==gibbs_samples[-3][0]:
                break
            k+=1
            
        return max(gibbs_samples,key=lambda x:x[1])[0]



    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself. 
    # It should return a list of part-of-speech labelings of the sentence, one
    #  part of speech per word.
    #
    def solve(self, model, sentence):
        if model == "Simple":
            return self.simplified(sentence)
        elif model == "HMM":
            return self.hmm_viterbi(sentence)
        elif model == "Complex":
            return self.complex_mcmc(sentence)
        else:
            print("Unknown algo!")

