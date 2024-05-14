from tensorflow import keras
import cv2
import os
from keras import layers
import numpy as np

dataset_path = 'Dataset'

dataset_data = []
class_data = []
bounding_box_data = []
with open('dataset.txt', 'r') as file:
    # name.jpg, x, y, width, height, klasa
    for line in file: dataset_data.append(line.strip().split(', '))
    for data in dataset_data:
        class_data.append(data[5])
        bounding_box_data.append(data[1:5])

bounding_box_data = np.array(bounding_box_data, dtype = 'float32')
bounding_box_data = bounding_box_data/600


dataset = []
for file in os.listdir(dataset_path): 
    image = cv2.imread(f'{dataset_path}/{file}')
    normalized_image = image/255.0
    dataset.append(normalized_image)

dataset = np.array(dataset)

test_dataset = dataset[:20]
test_bounding_box_data = bounding_box_data[:20]
test_class_data = class_data[:20]

train_dataset = dataset[349:]
train_bounding_box_data = bounding_box_data[349:]
train_class_data = class_data[349:]

valid_dataset  =dataset[350:400]
valid_bounding_box_data = bounding_box_data[350:400]
valid_class_data = class_data[350:400]

num_coordinates = 4

model = keras.models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape = (600,600, 3)),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(128, (3,3), activation='relu'),
    layers.Flatten(),
    layers.Dense(128, activation ='relu'),
    layers.Dense(num_coordinates, activation='sigmoid') # wyjscie dla bboxów

])

bounding_box_loss = 'mean_squared_error'
model.compile(optimizer='adam', loss=bounding_box_loss, metrics=['accuracy'])

history = model.fit(train_dataset, train_bounding_box_data, epochs = 10, validation_data = (valid_dataset, valid_bounding_box_data))

test_loss, test_bounding_box_loss = model.evaluate(test_dataset, test_bounding_box_data)
print("Test bounding box loss:", test_bounding_box_loss)

val_loss, val_bounding_box_loss =model.evaluate(valid_dataset, valid_bounding_box_data)

print("Validation bounding box loss:", val_bounding_box_loss)