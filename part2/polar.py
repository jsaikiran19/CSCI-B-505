#!/usr/local/bin/python3
#
# Authors: [PLEASE PUT YOUR NAMES AND USER IDS HERE]
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
    # with open('img_file.txt','w') as f:
    #     for item in image_array:
    #         f.write("%s \n" % item)
    # compute edge strength mask -- in case it's helpful. Feel free to use this.
    edge_strength = edge_strength(input_image)
    # print("edge strength",edge_strength.shape)
    # print("==")
    imageio.imwrite('edges.png', uint8(255 * edge_strength / (amax(edge_strength))))

    # You'll need to add code here to figure out the results! For now,
    # just create some random lines.
    # airice_simple = [ image_array.shape[0]*0.25 ] * image_array.shape[1]
    #=======================================================================================
    # Air Ice Simple
    def smoothness(row,prev_row,imageArray=[[]]):
        if abs(row-prev_row)<5:
            return math.log(0.9)
        elif abs(row-prev_row)<10:
            return math.log(0.6)
        elif abs(row-prev_row)<30:
            return math.log(0.1)
        else:
            return math.log(0.001)
    airice_simple = []
    for i in range(len(image_array[0])): # column
        mx = -1000
        pos = 0
        for j in range(len(image_array)): # row
            if i != 0 and abs(airice_simple[i-1]-j) > 10:
                continue
            if mx < edge_strength[j][i]:
                mx = edge_strength[j][i]
                pos = j
        
        airice_simple.append(pos)
    # print(airice_simple)
    # airice_hmm = [ image_array.shape[0]*0.5 ] * image_array.shape[1]
    airice_hmm = []
    parents = [(edge_strength[i][0],image_array[i][0],[i],0) for i in range(len(edge_strength))] # storing the initial pixel values and pos
    res = []
    max_edge_strength = amax(edge_strength,axis=0)
    for i in range(1,len(edge_strength[0])): # traversing in column
        res = [] # to store curr vals and pos
        for j in range(len(edge_strength)): # row
            mxk = -10000
            posk = [0]
            maxprob = 0
            mx_idx = 0
            for k in parents:
                # print(edge_strength[j][i])
                
                a = math.log(1/(1 + abs(j-k[2][-1]))+1e-10) + math.log(edge_strength[j][i]/max_edge_strength[i]+1e-10) +k[3]
                
                if a > mxk:
                    maxprob = k [3]
                    mxk = a
                    posk = k[2]
                    mx_idx = j

                elif a==mxk and abs(j-k[2][-1])<j-mx_idx:
                    mx_idx = k[-2][-1]

            
            res.extend([(edge_strength[j][i],image_array[j][i],posk+[mx_idx],mxk)])
        parents =  res.copy()
    # print(parents[0])
    airice_hmm = max(parents,key=lambda x:x[3])[2]
    print(airice_hmm)


    
    airice_feedback= [ image_array.shape[0]*0.75 ] * image_array.shape[1]
    # ==============================================================================
    # Ice rock Simple
    icerock_simple = []
    for i in range(len(image_array[0])): # column
        mx = -1000
        pos = 0
        for j in range(len(image_array)): # row
            if mx < edge_strength[j][i] and abs(j-airice_simple[i])>10:
                mx = edge_strength[j][i]
                pos = j
        
        icerock_simple.append(pos)

    
    
    #icerock_hmm = [ image_array.shape[0]*0.5 ] * image_array.shape[1]
    icerock_hmm = []
    
    parents = [(edge_strength[i][0],image_array[i][0],[i],0) for i in range(len(edge_strength))] # storing the initial pixel values and pos
    res = []
    # print(max_edge_strength)
    for i in range(1,len(edge_strength[0])): # traversing in column
        res = [] # to store curr vals and pos
        for j in range(airice_hmm[i]+10, len(edge_strength)): # row
            mxk = -10000
            posk = [0]
            maxprob = 0
            mx_idx = 0
            for k in parents:
                
                a = math.log(1/(1 + abs(j - k[2][-1]))+1e-10)+math.log(edge_strength[j][i]/max_edge_strength[i]+1e-10)+k[3]
                

                if a > mxk:
                    maxprob = k [3]
                    mxk = a
                    posk = k[2]
                    mx_idx = j

                elif a==mxk and abs(j-k[2][-1])<j-mx_idx:
                    mx_idx = k[-2][-1]
            
            res.extend([(edge_strength[j][i],image_array[j][i],posk+[mx_idx],mxk)])
        parents =  res.copy()
    # print(parents[0])
    # print(edge_strength)
    icerock_hmm = max(parents,key=lambda x:x[3])[2]
    print(icerock_hmm)
    icerock_feedback= [ image_array.shape[0]*0.75 ] * image_array.shape[1]

    # Now write out the results as images and a text file
    write_output_image("air_ice_output.png", input_image, airice_simple, airice_hmm, airice_feedback, gt_airice)
    write_output_image("ice_rock_output.png", input_image, icerock_simple, icerock_hmm, icerock_feedback, gt_icerock)
    with open("layers_output.txt", "w") as fp:
        for i in (airice_simple, airice_hmm, airice_feedback, icerock_simple, icerock_hmm, icerock_feedback):
            fp.write(str(i) + "\n")