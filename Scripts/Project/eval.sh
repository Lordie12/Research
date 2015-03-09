#!/bin/bash

# Run the ensemble model, create the prediction results for different models
python RandomForest.py

# Run the evaluation metrics
python Evaluation.py
