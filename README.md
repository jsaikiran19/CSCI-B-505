# hvalivet-jagchau-sjella-a3

# Assignment-3 Probability, NLP and Computer Vision

# Part1 - Parts of Speech Tagging

## Training
Traversed through the entire data and created dictionaries for words and its tags to store their frequency. Calculated initial word probabilities and transition probabilities using this dictionary.

## Simple Model
Calculated the probability of each tag for every word in the sentence, and assigned the tag with max probability to that word. If the word is missing (i.e not present in train data)
then assigning the most frequent tag in the training file for that word.

Doing this, is giving an accuracy of 47.50%.

## HMM Viterbi
From the transition probabilites which were calculated in training phase, I am creating HMM chains by summing up the log transition probabilties and emission probabilities at each node. (I used log probabilities because multiplying direct probabilities would have given zero at the end).

And then finally considering a HMM chain, that has the maximum probability. I first tried to handle the missing words by calculating the most probable tag from the previous tag which was giving me an accuracy of 48.55%. Instead, assigning the most frequent tag to the missing word actually improved my accuracy to 53.5%.

Further, I added few grammar rules to the words, so incase a word is missing and it satisfies any of those rules, then that particular tag is assigned to it. After adding grammar rules my accuracy improved to 55.95%.

## Complex 
Took an initial sample of all nouns. And then sampled the tags by considering each tag at a time and keep the rest constant. Calculated probabilities for each sample and stored them in a list. And breaking the loop if it converges (i.e checking if the previous 3 samples resulted in the exact same tags) or after a 100 iterations. And then taking the sample with maximum probability.(which most likely should be last  sample if it converges).

I first assigned a small probaility of 1e-10 if the word is missing, which gave an accuracy of 47.5%. Later, I considered the most frequent tag for the word if its missing, which improved my accuracy to 52.10%.
 


# Part 3 - Reading text

## Initial Probability
Initial Probability is calculated by counting the occurences of a letter as an initial letter and dividing it by the total words in the training data.

## Transition Probability
Transition Probability is calculated by counting transitions between two letters and dividing it by the total occurences of the first letter.

## Emission Probability
Emission Probability is calculated by comparing each pixel in test and training data. After counting matched and unmatched pixels, and considering m% noise, we can calculate it by (1 - m)^matched * m^unmatched

## Simple
For this method, we return the characters with the maximum emission probability for all the given characters. For new words, we have also applied laplace smoothing for the probabilities.

## Viterbi
For Viterbi, we create two tables which are V_table and which_table. Then we populate the first column using the initial and emission probabilities. After that using the populated data and the transition probability, we calculate the remaining values. Using backtracking, we return the most likely path.

