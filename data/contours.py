import cv2

print('enter filename: ', end='')
name = input()
#print('enter contour to display: ', end='')
#c = int(input())
# -1 passed into drawContours() will draw all contours on the image
c = -1

# these colors are used for when OpenCV displays contours and the rectangle around the word
contour_color_rgb = (0,255,75)
rectangle_color_rgb = (255, 0, 0)
thickness = 2

# change this to change how much whitespace we have around our word
padding_px = 25

img = cv2.imread('./' + name)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, im = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY_INV)
contours, hierarchy = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
img = cv2.drawContours(img, contours, c, contour_color_rgb, thickness)

max_x = contours[0][0][0][0]
min_x = contours[0][0][0][0]
max_y = contours[0][0][0][1]
min_y = contours[0][0][0][1]

for contour in contours:
    for row in contour:
        for point in row:
            x, y = point
            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y

max_x += padding_px
min_x -= padding_px
max_y += padding_px
min_y -= padding_px

cv2.rectangle(img, (max_x, max_y), (min_x, min_y), rectangle_color_rgb, thickness)
cropped_img = img[min_y:max_y, min_x:max_x]
cv2.imshow('image', cropped_img)
cv2.waitKey(0)
