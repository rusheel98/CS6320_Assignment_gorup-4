#!/bin/bash
# Run the Python script with specified arguments
python3 ffnn.py \
  -hd 8 \
  -e 10 \
  --train_data ./training.json \
  --val_data validation.json \
  --test_data test.json \
  --do_train

python3 ffnn.py \
  -hd 16 \
  -e 10 \
  --train_data ./training.json \
  --val_data validation.json \
  --test_data test.json \
  --do_train

python3 ffnn.py \
  -hd 32 \
  -e 10 \
  --train_data ./training.json \
  --val_data validation.json \
  --test_data test.json \
  --do_train