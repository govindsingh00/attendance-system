# TODO: Train face recognition model using captured dataset
# Will use DeepFace to generate face embeddings

import os

dataset_dir = "datasets"

for student_id in os.listdir(dataset_dir):
    print(f"Found student: {student_id}")

print("Training logic will be added here.")