
import os
import cv2

def load_images(path):
    images = []
    names = []
    for filename in os.listdir(path):
        names.append(filename)
        img = cv2.imread(os.path.join(path, filename))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        images.append(img)
   
    return images, names

def analyse_image(image, show_image):
    img = image.copy()
    img = img[120:950, 375:1700]
    img[:454, 1111:] = (0, 0, 0)

    if show_image:
        cv2.imshow('img',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.GaussianBlur(img, (11,11),0)

    if show_image:
        cv2.imshow('img',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    _, thresholded = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
    canny = cv2.Canny(thresholded, 115, 120)

    if show_image:
        cv2.imshow('img',canny)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    circles = cv2.HoughCircles(canny, cv2.HOUGH_GRADIENT, 1, 80, param1=50, param2=25, minRadius=30, maxRadius=100)

    if circles is not None:
        num_circles = len(circles[0])
        for circle in circles[0,:]:
            x, y, r = circle
            if show_image:
                cv2.circle(image, (int(x+375), int(y+120)), int(r), (0, 0, 255), 5)
        if show_image:
            image_to_show = image.copy()
            image_to_show = cv2.resize(image_to_show, (int(image_to_show.shape[1]/2), int(image_to_show.shape[0]/2)))
            cv2.imshow(f'{num_circles}', image_to_show)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    else:
        num_circles = 0
    return num_circles

if __name__ == "__main__":

    image_path = 'images'
    images, names= load_images(image_path)
    candies = 0
    show_image = True
    candies_best = 0

    for image in images:
        score = analyse_image(image, show_image)
        candies+=score
        if candies>30: show_image = False
        
    print(f"Total number of candies: {candies}")    

