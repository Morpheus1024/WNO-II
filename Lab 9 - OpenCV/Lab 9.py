
import cv2
import math
import numpy as np
import glob

def load_image_os_sys_glob():
    images = []
    images_names = []

    for filename in glob.glob('komb/*'):
        img = cv2.imread(filename)
        if img is not None:
            images.append(img)
            name = filename[:-4]
            images_names.append(name)
    for filename in glob.glob('miecz/cab/*'):
        img = cv2.imread(filename)
        if img is not None:
            images.append(img)
            name = filename[:-4]
            images_names.append(name)
    for filename in glob.glob('srub/driver/*'):
        img = cv2.imread(filename)
        if img is not None:
            images.append(img)
            name = filename[:-4]
            images_names.append(name)
    
    return images, images_names


def operation_on_image(image, image_name):

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _,baseline = cv2.threshold(grey,126,255,cv2.THRESH_TRUNC)

    baseline = cv2.Canny(image=grey, threshold1=10, threshold2=100)

    _,background = cv2.threshold(baseline,100,255,cv2.THRESH_BINARY)
    _,foreground = cv2.threshold(baseline,126,255,cv2.THRESH_BINARY_INV)

    foreground = cv2.bitwise_and(image, image, mask = foreground)

    
    image = foreground
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    image[np.where((image == [255, 255, 255, 255]).all(axis=2))] = [0, 0, 0, 255]


    canny =  cv2.Canny(image=image, threshold1=20, threshold2=250)
    lines = cv2.HoughLinesP(canny, 1, np.pi/90,10, minLineLength=250, maxLineGap=500)

    angle_points = []
    for line1 in lines:
        for x1, y1, x2, y2 in line1:
            for line2 in lines:
                for x3, y3, x4, y4 in line2:
                    if (x2 - x1) != 0 and (x4 - x3) != 0:  # aby uniknąć dzielenia przez zero
                        slope1 = (y2 - y1) / (x2 - x1)  # nachylenie linii 1
                        slope2 = (y4 - y3) / (x4 - x3)  # nachylenie linii 2
                        angle = math.degrees(math.atan(abs((slope2 - slope1) / (1 + slope1 * slope2))))  # oblicz kąt między liniami
                        if 0 < abs(angle) <16:  
                            determinant = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
                            if determinant!=0:
                                intersection_x = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / determinant
                                intersection_y = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / determinant
                                if 0 < intersection_x < image.shape[1] and 0 < intersection_y < image.shape[0]:
                                    angle_points.append([intersection_x,intersection_y])
                                    # cv2.circle(image, (int(intersection_x), int(intersection_y)), 2, (0, 0, 255), -1)

    if len(angle_points):
        points = np.array(angle_points)
        x = points[:,0]
        y = points[:,1]
        aproksymacja = np.polyfit(x,y,1)

        heigth, width = image.shape[:2]
        center = (width//2, heigth//2)

        angle = math.degrees(math.atan(aproksymacja[0]))-90

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        width1 = int(np.sqrt(heigth**2+width**2))
        heigth1 = width1

        rotation_matrix[0,2] += (width1)/2 - center[0]
        rotation_matrix[1,2] += (heigth1)/2 - center[1]

        rotated_image = cv2.warpAffine(image, rotation_matrix, (width1, heigth1))
        rotated_image = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2BGRA)
    else:rotated_image = image

    #znajdź długość obiektu:
    obj_height=0
    obj_width=0
    
    contours, _ = cv2.findContours(rotated_image[:, :, 3], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        obj_height = h
        obj_width = w
    else:
        obj_height = 0
        obj_width = 0
    wymiar = max(obj_height, obj_width)
    wymiar+=10

    croped_image = rotated_image[y:y+wymiar, x:x+wymiar]
    
    cv2.imshow(f'{image_name}', croped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




def main():
    images, images_names= load_image_os_sys_glob()

    new_images_names = [name.replace('/', '') for name in images_names]
    images_names = new_images_names

    for i in range(len(images)):
        operation_on_image(images[i], images_names[i])

if __name__ == '__main__':
    main()



    