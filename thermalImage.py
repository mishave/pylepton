import sys
from time import time, sleep
import os
import numpy as np
import cv2
from pylepton.Lepton3 import Lepton3
import signal

def ktoc(val):
  return (val - 27315) / 100.0

def display_temperature(img, val_c, loc, color):
  #val = ktoc(val_c)
  #cv2.putText(img,"{0:.1f} 'C".format(val), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
  x, y = loc

  cv2.line(img, (x - 4, y), (x + 4, y), (255,255,255), 2)
  cv2.line(img, (x, y - 4), (x, y + 4), (255,255,255), 2)
  cv2.line(img, (x - 4, y), (x + 4, y), color, 1)
  cv2.line(img, (x, y - 4), (x, y + 4), color, 1)
  return img

def raw_to_8bit(data):
  cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(data, 8, data)
  return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

def scaleDown(image, scale_pecentage):
    width = int(image.shape[1]*scale_pecentage/100)
    height = int(image.shape[0]*scale_pecentage/100)
    dim = (width,height)
    resize=cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resize


def main(DIR, device, stamp):
    flip_v = True
    app_dir = "/home/pi/CRKDcabinet/appdaemon/www/thermal/"
    
    """
    stamp = "1"
    DIR = '/home/pi/CRKDcabinet/homeassistant/config/www/'
    WEB_DIR = '/home/pi/iow/static/images/'
    device = '/dev/spidev0.0'
    """
    try:
        saveCSV = '{0}{1}.csv'.format(DIR, "CSV_latest")
        webImage = '{0}{1}.png'.format(DIR, "thermal_latest")
        saveImage = '{0}{1}.png'.format(DIR,"Grayscale_latest")
        #testDIR = '{0}2.png'.format(DIR,stamp)
        
        print("Starting")
        for retry in range(2):
            try:
                signal.alarm(5)  # Set the time limit in seconds... Having issues with garbage frames need to think about reset methods
                for i in range(20):
                    with Lepton3(device) as l:
                        a, _ = l.capture()
                        np.savetxt(saveCSV, a.reshape((120, -1)),
                                    delimiter=',', fmt='%s')
                    with open(saveCSV) as  f:
                        count=0
                        for line in f:
                            for word in line.split(','):
                                if word == '0':
                                    count = count + 1
                    print(count)
                    if count == 0:
                        print("Image good")
                        break
                    else:
                        print("bad image - trying again...")
                        time.sleep(0.185)
                signal.alarm(0)  # Reset the alarm
                # Other code here ...
            except Exception as e:
                print(f"An error occurred: {e}. Retrying...")
                continue
            break
                        
        if flip_v:
            cv2.flip(a, 0, a)
        b = a
        a = cv2.resize(a[:,:], (640, 480))
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(a)
        image = raw_to_8bit(a)
        cv2.imwrite(saveImage, image)
        print("Image Saved")    

        """
        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        image = np.uint8(a)
        data = cv2.resize(data[:,:], (640, 480))
        cv2.imwrite(saveImage, image)
        """
        """
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(a)
        print(minVal, maxVal)
        image = display_temperature(image, minVal, minLoc, (255, 0, 0))
        image = display_temperature(image, maxVal, maxLoc, (0, 0, 255))    
        #cv2.imwrite(testDIR, image)
        """
        #Scale image up
        """
        scale_pecentage = 100
        width = int(image.shape[1]*scale_pecentage/100)
        height = int(image.shape[0]*scale_pecentage/100)
        dim = (width,height)
        resize=cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        """
        #Colourise image option 1
        """
        colourise = cv2.merge((resize,resize,resize))
        red = np.full((1,1,3),(0,125,255),np.uint8)
        green = np.full((1,1,3),(125,0,0),np.uint8)
        blue = np.full((1,1,3),(125,0,125),np.uint8)
        lut=np.concatenate((red,blue,green),axis=0)
        lut=cv2.resize(lut,(1,256),interpolation=cv2.INTER_LINEAR)
        colourise=cv2.LUT(colourise,lut)
        """
        #Colourise image option 2
        """
        #Working Code
        colourise = cv2.applyColorMap(image, cv2.COLORMAP_JET)
        cv2.imwrite(webImage, colourise)
        print(saveImage)
        print("complete")
        """
        
        b = cv2.resize(b[:,:], (320, 240))
        minValb, maxValb, minLocb, maxLocb = cv2.minMaxLoc(b)
        maxV = ktoc(maxValb)
        minV = ktoc(minValb)

        #minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(a)
        #print(minVal, maxVal)
        #imageb = display_temperature(image, minVal, minLoc, (255, 0, 0))
        #imageb = display_temperature(image, maxVal, maxLoc, (0, 0, 255))

        print(minV)
        imageb = raw_to_8bit(b)
        imageb = cv2.applyColorMap(imageb, cv2.COLORMAP_JET)
        
        # Put text values of max and min temperature in top right corner
        cv2.putText(imageb, "{0:.1f} C".format(maxV), (imageb.shape[1] - 70, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 0)
        cv2.putText(imageb, "{0:.1f} C".format(minV), (imageb.shape[1] - 70, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 0)
  
        imageMarkedb = display_temperature(imageb, minValb, minLocb, (255, 0, 0))
        imageMarkedb = display_temperature(imageb, maxValb, maxLocb, (0, 0, 255))
        cv2.imwrite(webImage, imageMarkedb)
        print("complete")


        return('{0}.png'.format(stamp),'{0}.csv'.format(stamp), maxV, minV)
    
    except Exception:
        return ("failure", "failure")
        """
        if __name__ == '__main__':
            main()
        """
        pass

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 thermalImage.py <DIR> <device> <stamp>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])

      