# Save a pretrained keras Resnet50 model
from tensorflow.keras.applications import ResNet50

model = ResNet50(weights="imagenet")
model.save('resnet.h5', overwrite=True, include_optimizer=True)

