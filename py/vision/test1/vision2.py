
import socket

import gevent

import cv2.cv as cv

import cv2
import numpy as np
import itertools
import sys

import traceback

import time

def findKeyPoints(img, template, distance=200):
    detector = cv2.FeatureDetector_create("SIFT")
    descriptor = cv2.DescriptorExtractor_create("SIFT")

    skp = detector.detect(img)
    skp, sd = descriptor.compute(img, skp)

    tkp = detector.detect(template)
    tkp, td = descriptor.compute(template, tkp)

    flann_params = dict(algorithm=1, trees=4)
    flann = cv2.flann_Index(sd, flann_params)
    idx, dist = flann.knnSearch(td, 1, params={})
    del flann

    dist = dist[:,0]/2500.0
    dist = dist.reshape(-1,).tolist()
    idx = idx.reshape(-1).tolist()
    indices = range(len(dist))
    indices.sort(key=lambda i: dist[i])
    dist = [dist[i] for i in indices]
    idx = [idx[i] for i in indices]
    skp_final = []
    for i, dis in itertools.izip(idx, dist):
        if dis < distance:
            skp_final.append(skp[i])

    flann = cv2.flann_Index(td, flann_params)
    idx, dist = flann.knnSearch(sd, 1, params={})
    del flann

    dist = dist[:,0]/2500.0
    dist = dist.reshape(-1,).tolist()
    idx = idx.reshape(-1).tolist()
    indices = range(len(dist))
    indices.sort(key=lambda i: dist[i])
    dist = [dist[i] for i in indices]
    idx = [idx[i] for i in indices]
    tkp_final = []
    for i, dis in itertools.izip(idx, dist):
        if dis < distance:
            tkp_final.append(tkp[i])

    return skp_final, tkp_final

def drawKeyPoints(img, template, skp, tkp, num=-1):
    h1, w1 = img.shape[:2]
    h2, w2 = template.shape[:2]
    nWidth = w1+w2
    nHeight = max(h1, h2)
    hdif = (h1-h2)/2
    newimg = np.zeros((nHeight, nWidth, 3), np.uint8)
    newimg[hdif:hdif+h2, :w2] = template
    newimg[:h1, w2:w1+w2] = img

    maxlen = min(len(skp), len(tkp))
    if num < 0 or num > maxlen:
        num = maxlen
    for i in range(num):
        pt_a = (int(tkp[i].pt[0]), int(tkp[i].pt[1]+hdif))
        pt_b = (int(skp[i].pt[0]+w2), int(skp[i].pt[1]))
        cv2.line(newimg, pt_a, pt_b, (255, 0, 0))
    return newimg


def match():
    img = cv2.imread("box_in_scene2.png")#sys.argv[1])
    temp = cv2.imread("box4.png")#sys.argv[2])
    try:
    	dist = int(sys.argv[3])
    except IndexError:
    	dist = 200
    try:
    	num = int(sys.argv[4])
    except IndexError:
    	num = -1
    skp, tkp = findKeyPoints(img, temp, dist)
    newimg = drawKeyPoints(img, temp, skp, tkp, num)
    cv2.imshow("image", newimg)
    cv2.waitKey(0)
    
    
def main():

    logo = cv2.imread("cctv2.png")#sys.argv[2])
    print type(logo)
    cv.NamedWindow("VIDEO", 1)
    
    # rtsp://cam_address:554/live.sdp
    capture = cv.CaptureFromCAM(0)
    #capture = cv.CaptureFromFile("rtsp://192.168.2.58:554")
    #capture = cv2.VideoCapture("rtsp://192.168.1.10:34567")
    
    #capture =cv2.VideoCapture("rtsp://192.168.2.58:554")
    c = 0
    print dir(traceback)
    while True:
        
        """
        v = int(time.time())
        #print v
        
        if v & 6 !=0:
            continue
        """
        #img = cv.QueryFrame(capture)
        
        
        ret, img_p = capture.read()
        
        #mat=cv.GetMat(img)
        #img_p = np.asarray(mat)

        newimg = img_p
        #mat=cv.GetMat(img)
        #img_p = np.asarray(mat)
        
        #img_p  = cv.CreateImage(cv.GetSize(img),cv.IPL_DEPTH_8U,1)
        
        #print dir(img)
        
        """
        im_gray  = cv.CreateImage(cv.GetSize(img),cv.IPL_DEPTH_8U,1)
        cv.CvtColor(img,im_gray,cv.CV_RGB2GRAY)
        
        
        # Sobel operator
        dstSobel = cv.CreateMat(im_gray.height, im_gray.width, cv.CV_32FC1)
        # Sobel(src, dst, xorder, yorder, apertureSize = 3)
        cv.Sobel(im_gray,dstSobel,1,1,3)
        """
        try:
            
            v = int(time.time())
            
            if v % 3 ==0:
                
                if c == 0:
                    c = 1
                    skp, tkp = findKeyPoints(img_p, logo, 15)

                    newimg = drawKeyPoints(img_p, logo, skp, tkp, -1)
                    print(len(tkp))
                cv2.imshow("VIDEO", newimg)
                
            else:
                c = 0
                cv2.imshow("VIDEO", newimg)                
                
            """    
            
            #print v
            
            
        
                    skp, tkp = findKeyPoints(img_p, logo, 15)

                    newimg = drawKeyPoints(img_p, logo, skp, tkp, -1)
                    print(len(tkp))
                cv2.imshow("camera", newimg)
            else:
                c = 0
                cv2.imshow("camera", newimg)
            """
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            gevent.sleep(0.01)
            continue
        #cv.ShowImage('camera', newimg)
        
        
        # image smoothing and subtraction
    #    imageBlur = cv.CreateImage(cv.GetSize(im_gray), im_gray.depth, im_gray.nChannels)
    #    # filering the original image
    #    # Smooth(src, dst, smoothtype=CV_GAUSSIAN, param1=3, param2=0, param3=0, param4=0)
    #    cv.Smooth(im_gray, imageBlur, cv.CV_BLUR, 11, 11)
    #    diff = cv.CreateImage(cv.GetSize(im_gray), im_gray.depth, im_gray.nChannels)
    #    # subtraction (original - filtered)
    #    cv.AbsDiff(im_gray,imageBlur,diff)
    #    cv.ShowImage('camera', diff)
        
        if cv.WaitKey(10) == 27:
            break
            
        #gevent.sleep(0.5)
        
    cv.DestroyWindow("camera")
    
    
    
if __name__ == "__main__":
    
    main()