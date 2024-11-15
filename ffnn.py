import numpy as np
import torch
import torch.nn as nn
from torch.nn import init
import torch.optim as optim
import math
import random
import os
import time
from tqdm import tqdm
import json
from argparse import ArgumentParser
import matplotlib.pyplot as plt


unk = '<UNK>'
# Consult the PyTorch documentation for information on the functions used below:
# https://pytorch.org/docs/stable/torch.html
class FFNN(nn.Module):
    def __init__(self, input_dim, h):
        super(FFNN, self).__init__()
        self.h = h
        self.W1 = nn.Linear(input_dim, h)
        self.activation = nn.ReLU() # The rectified linear unit; one valid choice of activation function
        self.output_dim = 5
        self.W2 = nn.Linear(h, self.output_dim)

        self.softmax = nn.LogSoftmax() # The softmax function that converts vectors into probability distributions; computes log probabilities for computational benefits
        self.loss = nn.NLLLoss() # The cross-entropy/negative log likelihood loss taught in class

    def compute_Loss(self, predicted_vector, gold_label):
        return self.loss(predicted_vector, gold_label)

    def forward(self, input_vector):
        # Linear function 1
        out = self.W1(input_vector)
        # Non-linearity 1
        out = self.activation(out)

        # Linear function 2
        out = self.W2(out)

        return self.softmax(out)


# Returns: 
# vocab = A set of strings corresponding to the vocabulary
def make_vocab(data):
    vocab = set()
    for document, _ in data:
        for word in document:
            vocab.add(word)
    return vocab 


# Returns:
# vocab = A set of strings corresponding to the vocabulary including <UNK>
# word2index = A dictionary mapping word/token to its index (a number in 0, ..., V - 1)
# index2word = A dictionary inverting the mapping of word2index
def make_indices(vocab):
    vocab_list = sorted(vocab)
    vocab_list.append(unk)
    word2index = {}
    index2word = {}
    for index, word in enumerate(vocab_list):
        word2index[word] = index 
        index2word[index] = word 
    vocab.add(unk)
    return vocab, word2index, index2word 


# Returns:
# vectorized_data = A list of pairs (vector representation of input, y)
def convert_to_vector_representation(data, word2index):
    vectorized_data = []
    for document, y in data:
        vector = torch.zeros(len(word2index)) 
        for word in document:
            index = word2index.get(word, word2index[unk])
            vector[index] += 1
        vectorized_data.append((vector, y))
    return vectorized_data



def load_data(train_data, val_data):
    with open(train_data) as training_f:
        training = json.load(training_f)
    with open(val_data) as valid_f:
        validation = json.load(valid_f)

    tra = []
    val = []
    for elt in training:
        tra.append((elt["text"].split(),int(elt["stars"]-1)))
    for elt in validation:
        val.append((elt["text"].split(),int(elt["stars"]-1)))

    return tra, val


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-hd", "--hidden_dim", type=int, required = True, help = "hidden_dim")
    parser.add_argument("-e", "--epochs", type=int, required = True, help = "num of epochs to train")
    parser.add_argument("--train_data", required = True, help = "path to training data")
    parser.add_argument("--val_data", required = True, help = "path to validation data")
    parser.add_argument("--test_data", default = "to fill", help = "path to test data")
    parser.add_argument('--do_train', action='store_true')
    args = parser.parse_args()

    # fix random seeds
    random.seed(42)
    torch.manual_seed(42)

    # load data
    print("========== Loading data ==========")
    train_data, valid_data = load_data(args.train_data, args.val_data) 
    # print("len",len(train_data))# X_data is a list of pairs (document, y); y in {0,1,2,3,4}
    vocab = make_vocab(train_data)
    vocab, word2index, index2word = make_indices(vocab)

    print("========== Vectorizing data ==========")
    train_data = convert_to_vector_representation(train_data, word2index)

    valid_data = convert_to_vector_representation(valid_data, word2index)
    

    model = FFNN(input_dim = len(vocab), h = args.hidden_dim)
    lrs = [0.001,0.0015,0.002,0.0025,0.01]
    optimizers = ["adam", "sgd"]

    for lr in lrs:
        for i in optimizers:
            if i == "adam":
                optimizer = optim.Adam(model.parameters(),lr=lr)
            else:
                optimizer = optim.SGD(model.parameters(),lr=lr, momentum=0.75)
            print("========== Training for {} epochs ==========".format(args.epochs))
            # train_loss = []
            # valid_loss = []
            # train_acc = []
            # valid_acc = []
            epochs = []
            for epoch in range(args.epochs):
                model.train()
                optimizer.zero_grad()
                loss = None
                correct = 0
                total = 0
                start_time = time.time()
                print("Training started for epoch {}".format(epoch + 1))
                random.shuffle(train_data) # Good practice to shuffle order of training data
                minibatch_size = 16 
                N = len(train_data)
                # print("N train ",N)
                for minibatch_index in tqdm(range(N // minibatch_size)):
                    optimizer.zero_grad()
                    loss = None
                    for example_index in range(minibatch_size):
                        input_vector, gold_label = train_data[minibatch_index * minibatch_size + example_index]
                        predicted_vector = model(input_vector)
                        predicted_label = torch.argmax(predicted_vector)
                        correct += int(predicted_label == gold_label)
                        total += 1
                        example_loss = model.compute_Loss(predicted_vector.view(1,-1), torch.tensor([gold_label]))
                        if loss is None:
                            loss = example_loss
                        else:
                            loss += example_loss
                    loss = loss / minibatch_size
                    loss.backward()
                    optimizer.step()
                print("Training completed for epoch {}".format(epoch + 1))
                print("Training accuracy for epoch {}: {}".format(epoch + 1, correct / total))
                print("Training time for this epoch: {}".format(time.time() - start_time))
                # print("train",loss.item())
                # train_loss.append(loss.item())
                # train_acc.append(correct / total)

                loss = None
                correct = 0
                total = 0
                start_time = time.time()
                print("Validation started for epoch {}".format(epoch + 1))
                minibatch_size = 16 
                N = len(valid_data)
                # print("N valid ",N)
                for minibatch_index in tqdm(range(N // minibatch_size)):
                    optimizer.zero_grad()
                    loss = None
                    for example_index in range(minibatch_size):
                        input_vector, gold_label = valid_data[minibatch_index * minibatch_size + example_index]
                        predicted_vector = model(input_vector)
                        predicted_label = torch.argmax(predicted_vector)
                        correct += int(predicted_label == gold_label)
                        total += 1
                        example_loss = model.compute_Loss(predicted_vector.view(1,-1), torch.tensor([gold_label]))
                        if loss is None:
                            loss = example_loss
                        else:
                            loss += example_loss
                    loss = loss / minibatch_size
                print("Validation completed for epoch {}".format(epoch + 1))
                print("Validation accuracy for epoch {}: {}".format(epoch + 1, correct / total))
                print("Validation time for this epoch: {}".format(time.time() - start_time))
                # valid_loss.append(loss.item())
                # print("valid",loss.item())
                # epochs.append(epoch+1)
                # valid_acc.append(correct / total)
                # print(len(train_loss), len(valid_loss))


            # write out to results/test.out
            # Load and process test data
            # if not os.path.exists("results/{}".format(i)):
            #     os.makedirs("results/{}".format(i))

            # plt.clf()
            # plt.plot(epochs, train_acc, label='train plot', color='blue')
            # plt.plot(epochs, valid_acc, label='valid plot', color='red')
            # plt.legend()
            # plt.title('Training and Validation accuracy')
            # plt.xlabel('Epochs')
            # plt.ylabel('Accuracy')
            # plt.savefig("results/{}/acc_{}_{}.png".format(i,args.hidden_dim,lr))
            # plt.close()

            # test_data, _ = load_data(args.test_data, args.val_data)
            # # print("N test ",len(test_data))
            # test_data = convert_to_vector_representation(test_data, word2index)
            # # Testing phase
            # print("========== Testing Phase ==========")
            # model.eval()
            # correct = 0
            # total = 0
            # for input_vector, gold_label in test_data:
            #     predicted_vector = model(input_vector)
            #     predicted_label = torch.argmax(predicted_vector)
            #     correct += int(predicted_label == gold_label)
            #     total += 1

            # test_accuracy = correct / total
            # print("Test accuracy: {}".format(test_accuracy))

            # # Write test results to file
            # with open("results/{}/test_{}.out".format(i,lr), "w") as f:
            #     f.write("Test accuracy: {}\n".format(test_accuracy))
            # with open("results_adam.out", "a") as h:
            #     h.write("{} {} {} {} {} {}\n".format(args.hidden_dim, i, train_loss, valid_loss, lr, test_accuracy))