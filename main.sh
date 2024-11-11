#!/bin/bash


python rnn.py \
  -hd 8 \
  -e 10 \
  --train_data ./training.json \
  --val_data validation.json \
  --test_data test.json \
  --do_train

python rnn.py \
  -hd 16 \
  -e 10 \
  --train_data ./training.json \
  --val_data validation.json \
  --test_data test.json \
  --do_train

python rnn.py \
  -hd 32 \
  -e 10 \
  --train_data ./training.json \
  --val_data validation.json \
  --test_data test.json \
  --do_train