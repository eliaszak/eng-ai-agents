# -*- coding: utf-8 -*-
"""ASSIGNMENT3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WKS9BzLer4-ca5JXH_kcqVvq8FkXrP1Z
"""

# Task 1
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image
import cv2
import matplotlib.pyplot as plt

model = fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

COCO_CLASSES = {1: 'person', 37: 'sports ball'}

def get_video_frames(input_video, frame_skip_interval=30):
    cap = cv2.VideoCapture(input_video)
    video_frames = []
    count = 0

    while cap.isOpened():
        ret, current_frame = cap.read()
        if not ret:
            break
        if count % frame_skip_interval == 0:
            video_frames.append(current_frame)
        count += 1

    cap.release()
    return video_frames

def perform_detection(model, current_frame, threshold=0.5):
    img = Image.fromarray(cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB))
    img_tensor = F.to_tensor(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_tensor)[0]

    bounding_boxes, detected_labels, confidence_scores = outputs['boxes'], outputs['labels'], outputs['scores']
    filtered_indices = [i for i, label in enumerate(detected_labels) if label in [1, 37] and confidence_scores[i] > threshold]

    return bounding_boxes[filtered_indices], detected_labels[filtered_indices], confidence_scores[filtered_indices]

def display_results(current_frame, bounding_boxes, detected_labels, confidence_scores):
    current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
    for box, label, score in zip(bounding_boxes, detected_labels, confidence_scores):
        x1, y1, x2, y2 = box
        label_name = COCO_CLASSES[label.item()]
        cv2.rectangle(current_frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
        cv2.putText(current_frame, f"{label_name}: {score:.2f}", (int(x1), int(y1)-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    plt.figure(figsize=(10, 10))
    plt.imshow(current_frame)
    plt.axis('off')
    plt.show()

def run_object_detection(input_video, frame_skip_interval=30, threshold=0.5):
    video_frames = get_video_frames(input_video, frame_skip_interval)

    for i, current_frame in enumerate(video_frames[:5]):
        print(f"Processing frame {i + 1}")
        bounding_boxes, detected_labels, confidence_scores = perform_detection(model, current_frame, threshold)
        display_results(current_frame, bounding_boxes, detected_labels, confidence_scores)

input_video = 'soccer_game.mp4'
run_object_detection(input_video, frame_skip_interval=30, threshold=0.5)

# TASK 2
# Here is the revised explanation for Task 2: Deep-SORT, with all words in parentheses removed:

#Task 2: Deep-SORT

#1. Architecture Diagram

#The architecture of Deep-SORT includes several important components. The first component is object detection, which is handled by Faster R-CNN. This model detects objects in each frame, including players and the soccer ball, and outputs bounding boxes, confidence scores, and class labels. The Kalman Filter tracks the state of objects over time by estimating their position and velocity. It predicts the next location of each object based on a motion model and updates the state using matches from new detections. The next component is feature extraction, where an appearance descriptor is used to generate embeddings for each detected object. These embeddings help distinguish between objects that may have similar locations or movement patterns. Data association is performed using the Hungarian Algorithm, which matches detections with existing tracks. It does this by minimizing a cost matrix, which combines the motion cost and the appearance cost. Finally, track management ensures that all active tracks are maintained, new tracks are initialized for unmatched detections, and tracks are terminated if they remain unmatched for a certain number of frames.

#2. Summary of Key Components

#The Kalman Filter works in two steps: prediction and update. In the prediction step, the Kalman Filter estimates the next state of an object, using a state transition matrix and a process noise covariance. This prediction accounts for uncertainty in the object’s motion. In the update step, the Kalman Filter refines this prediction using new measurements, such as the detected bounding box. The Kalman gain determines how much weight is given to the new measurement compared to the predicted state, and the updated state is used to adjust the object’s estimated position and velocity.

#The Hungarian Algorithm solves the assignment problem by matching detections with existing tracks. It minimizes a cost matrix that combines motion and appearance costs. The motion cost measures the difference between the predicted position and the actual detection, while the appearance cost measures the similarity between the appearance features of a detection and the current tracked object. This method ensures that the correct detection is matched to the correct track, even in challenging scenarios with multiple objects.

#Track management ensures that tracks are continuously updated and maintained. If a detection does not match any existing track, a new track is created. Tracks are updated based on new detections, and those that haven’t been matched for a set number of frames are terminated. This ensures that the track IDs remain consistent and relevant throughout the video.

#3. Deep-SORT Integration with Object Detector

#Deep-SORT works in conjunction with an object detector like Faster R-CNN. First, Faster R-CNN processes each video frame and detects the players and the soccer ball, returning bounding boxes and class labels. These detections are passed to Deep-SORT, which uses the Kalman Filter to predict the position of each object based on its previous state. The Hungarian Algorithm then matches the detections to existing tracks by considering both motion and appearance. After matching, the tracker updates the position and velocity of each object. Deep-SORT outputs track IDs, bounding box coordinates, and trajectories for each detected object, allowing the tracking of players and the ball across multiple frames. The same track ID is maintained for each object, even when objects interact or move out of the frame.