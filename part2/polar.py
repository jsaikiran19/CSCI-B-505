#!/usr/local/bin/python3
#
# Authors: [Harsha Valiveti - hvalivet]
#
# Ice layer finder
# Based on skeleton code by D. Crandall, November 2021
#

from PIL import Image
from numpy import *
from scipy.ndimage import filters
import sys
import imageio
import math
# calculate "Edge strength map" of an image                                                                                                                                      
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale,0,filtered_y)
    return sqrt(filtered_y**2)

# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#
def draw_boundary(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range( int(max(y-int(thickness/2), 0)), int(min(y+int(thickness/2), image.size[1]-1 )) ):
            image.putpixel((x, t), color)
    return image

def draw_asterisk(image, pt, color, thickness):
    for (x, y) in [ (pt[0]+dx, pt[1]+dy) for dx in range(-3, 4) for dy in range(-2, 3) if dx == 0 or dy == 0 or abs(dx) == abs(dy) ]:
        if 0 <= x < image.size[0] and 0 <= y < image.size[1]:
            image.putpixel((x, y), color)
    return image


# Save an image that superimposes three lines (simple, hmm, feedback) in three different colors 
# (yellow, blue, red) to the filename
def write_output_image(filename, image, simple, hmm, feedback, feedback_pt):
    new_image = draw_boundary(image, simple, (255, 255, 0), 2)
    new_image = draw_boundary(new_image, hmm, (0, 0, 255), 2)
    new_image = draw_boundary(new_image, feedback, (255, 0, 0), 2)
    new_image = draw_asterisk(new_image, feedback_pt, (255, 0, 0), 2)
    imageio.imwrite(filename, new_image)



# main program
#
if __name__ == "__main__":

    if len(sys.argv) != 6:
        raise Exception("Program needs 5 parameters: input_file airice_row_coord airice_col_coord icerock_row_coord icerock_col_coord")

    input_filename = sys.argv[1]
    gt_airice = [ int(i) for i in sys.argv[2:4] ]
    gt_icerock = [ int(i) for i in sys.argv[4:6] ]

    # load in image 
    input_image = Image.open(input_filename).convert('RGB')
    image_array = array(input_image.convert('L'))
    # Writing the image_array into a TXT file
    # with open('img_file.txt','w') as f:
    #     for item in image_array:
    #         f.write("%s \n" % item)
    # compute edge strength mask -- in case it's helpful. Feel free to use this.
    edge_strength = edge_strength(input_image)
    imageio.imwrite('edges.png', uint8(255 * edge_strength / (amax(edge_strength))))

    # You'll need to add code here to figure out the results! For now,
    # just create some random lines.
    # airice_simple = [ image_array.shape[0]*0.25 ] * image_array.shape[1]
    #=======================================================================================
    # Air Ice Simple
    airice_simple = []
    for i in range(len(image_array[0])): # traversing in Column
        mx = -1000
        pos = 0
        for j in range(len(image_array)): # traversing in Row
            # Restricting a row if it is greater than 10 rows of previous col row
            if i != 0 and abs(airice_simple[i-1]-j) > 10:
                continue
            
            if mx < edge_strength[j][i]:
                mx = edge_strength[j][i]
                pos = j
        
        airice_simple.append(pos)
    
    # ==============================================================================
    # Ice rock Simple
    icerock_simple = []
    for i in range(len(image_array[0])): # traversing in Column
        mx = -1000
        pos = 0
        # considering row value to be greater than Air Ice
        for j in range(airice_simple[i] + 10, len(image_array)): # traversing in Row
            # Getting maximum
            if mx < edge_strength[j][i]:
                mx = edge_strength[j][i]
                pos = j
        
        icerock_simple.append(pos)
    # ==============================================================================   
    # Air Ice Viterbi
    airice_hmm = []
    parents = [([i],0) for i in range(len(edge_strength))] # storing the initial pixel values and pos
    max_edge_strength = amax(edge_strength,axis=0) # Maximum Edge Strength of each column from the Image
    for i in range(1,len(edge_strength[0])): # traversing in Column
        res = [] # to store curr vals and pos
        for j in range(len(edge_strength)): # traversing in Row
            mxk = -10000
            posk = [0] # Storing the path
            maxprob = 0  # Storing the probability value
            mx_idx = 0 # Storing the index
            
            for k in parents:
                # Calculating the total probability of a row to be choosen
                a = math.log(1/(1 + abs(j-k[0][-1]))+1e-10) + math.log(edge_strength[j][i]/max_edge_strength[i]+1e-10) +k[1]
                
                # Getting maximum, probability to draw the Boundary
                if a > mxk:
                    maxprob = k[1]
                    mxk = a
                    posk = k[0]
                    mx_idx = j
                # If the probabilities are same, then we can choose the row closer from the previous Column
                elif a==mxk and abs(j-k[0][-1])<j-mx_idx:
                    mx_idx = k[0][-1]

            # Updating the parents list to pass on the information to the next Column
            res.extend([(posk+[mx_idx],mxk)])
        parents =  res.copy()

    # Getting path from the Last state(Column) filtering through the maximum elements
    airice_hmm = max(parents,key=lambda x:x[1])[0]
    # ==============================================================================
    # Ice Rock Viterbi
    icerock_hmm = []
    
    parents = [([i],0) for i in range(len(edge_strength))] # storing the initial pixel values and pos
    res = []
    for i in range(1,len(edge_strength[0])): # traversing in Column
        res = [] # to store curr vals and pos
        for j in range(airice_hmm[i]+10, len(edge_strength)): # traversing in Row
            mxk = -10000
            posk = [0] # Storing the path
            maxprob = 0  # Storing the probability value
            mx_idx = 0 # Storing the index
            for k in parents:

                # Calculating the total probability of a row to be choosen 
                a = math.log(1/(1 + abs(j - k[0][-1]))+1e-10)+math.log(edge_strength[j][i]/max_edge_strength[i]+1e-10)+k[1]

                # Getting maximum, probability to draw the Boundary
                if a > mxk:
                    maxprob = k[1]
                    mxk = a
                    posk = k[0]
                    mx_idx = j
                # If the probabilities are same, then we can choose the row closer from the previous Column
                elif a==mxk and abs(j-k[0][-1])<j-mx_idx:
                    mx_idx = k[0][-1]
            # Updating the parents list to pass on the information to the next Column
            res.extend([(posk+[mx_idx],mxk)])
        parents =  res.copy()
    # Getting path from the Last state(Column) filtering through the maximum elements
    icerock_hmm = max(parents,key=lambda x:x[1])[0]
    # ==============================================================================  
    # airice_feedback= [ image_array.shape[0]*0.75 ] * image_array.shape[1]
    # Air Ice Human FeedBack
    airice_feedback = []
    parents = [([i],0) for i in range(len(edge_strength))] # storing the initial pixel values and pos
    for i in range(1,len(edge_strength[0])): # traversing in Column
        res = [] # to store curr vals and pos
        
        for j in range(len(edge_strength)): # traversing in Row
            mxk = -10000
            posk = [0] # Storing the path
            maxprob = 0  # Storing the probability value
            mx_idx = 0 # Storing the index
            
            for k in parents:
                # if the given human feedback in the cur_row and cur_col, then blindly append it to the list
                if gt_airice[0]==j and gt_airice[1]==i:
                    mx_idx = j
                    mxk = 10000 + k[1]
                    posk = k[0]
                    break
                # Smoothness of the pixel transition, by giving weights to transition
                diff = abs(j-k[0][-1])
                val = 1
                if diff <= 1:
                    val = -1
                elif diff <=3:
                    val = 0
                elif diff <= 7:
                    val = 1.5
                elif diff <= 10:
                    val = 8
                else:
                    val = 10000
                
                # Calculating the total probability of a row to be choosen
                a = val * math.log(1/(1 + abs(j-k[0][-1]))+1e-10) + math.log(edge_strength[j][i]/max_edge_strength[i]+1e-10) +k[1]
                
                # Getting maximum, probability to draw the Boundary
                if a > mxk:
                    maxprob = k[1]
                    mxk = a
                    posk = k[0] # path
                    mx_idx = j
                # If the probabilities are same, then we can choose the row closer from the previous Column
                elif a==mxk and abs(j-k[0][-1])<j-mx_idx:
                    mx_idx = k[0][-1]

            # Updating the parents list to pass on the information to the next Column
            res.extend([(posk+[mx_idx],mxk)])
        parents =  res.copy()
    # Getting path from the Last state(Column) filtering through the maximum elements
    airice_feedback = max(parents,key=lambda x:x[1])[0]
    # # ==============================================================================
    # Ice Rock Human FeedBack
    icerock_feedback = []
    parents = [([i],0) for i in range(len(edge_strength))] # storing the initial pixel values and pos
    
    for i in range(1,len(edge_strength[0])): # traversing in column
        res = [] # to store curr vals and pos
        for j in range(airice_feedback[i]+10 ,len(edge_strength)): # row
            mxk = -10000
            posk = [0] # Storing the path
            maxprob = 0  # Storing the probability value
            mx_idx = 0 # Storing the index
            for k in parents:
                # if the given human feedback in the cur_row and cur_col, then blindly append it to the list
                if gt_icerock[0]==j and gt_icerock[1]==i:
                    mx_idx = j
                    mxk = 100000 + k[1]
                    posk = k[0]
                    break
                
                # Smoothness of the pixel transition, by giving weights to transition
                diff = abs(j-k[0][-1])
                val = 1
                if diff <= 1:
                    val = -1
                elif diff <=3:
                    val = 0
                elif diff <= 7:
                    val = 1.5
                elif diff <= 10:
                    val = 8
                else:
                    val = 10000
                
                # Calculating the total probability of a row to be choosen 
                a = val * math.log(1/(1 + abs(j-k[0][-1]))+1e-10) + math.log(edge_strength[j][i]/max_edge_strength[i]+1e-10) +k[1]
                
                # Getting maximum, probability to draw the Boundary
                if a > mxk:
                    maxprob = k[1]
                    mxk = a
                    posk = k[0] # path
                    mx_idx = j
                # If the probabilities are same, then we can choose the row closer from the previous Column
                elif a == mxk and abs(j-k[0][-1])<j-mx_idx:
                    mx_idx = k[0][-1]
            # Updating the parents list to pass on the information to the next Column
            res.extend([(posk+[mx_idx],mxk)])
        parents =  res.copy()
    # Getting path from the Last state(Column) filtering through the maximum elements
    icerock_feedback = max(parents,key=lambda x:x[1])[0]
    # ==============================================================================
    # Now write out the results as images and a text file
    write_output_image("air_ice_output.png", input_image, airice_simple, airice_hmm, airice_feedback, gt_airice)
    write_output_image("ice_rock_output.png", input_image, icerock_simple, icerock_hmm, icerock_feedback, gt_icerock)
    with open("layers_output.txt", "w") as fp:
        for i in (airice_simple, airice_hmm, airice_feedback, icerock_simple, icerock_hmm, icerock_feedback):
            fp.write(str(i) + "\n")