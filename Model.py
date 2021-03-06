import tensorflow as tf
import numpy as np
import os

from keras.utils import np_utils
from keras.models import Sequential, load_model
from keras.layers import Dense, Conv2D, MaxPool2D
from keras.layers import Flatten, Dropout
from speechpy import mfcc
from speechpy import delta
from speechpy import log_filter_bank
from speechpy import preprocessor
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from random import shuffle

class Model():
        
        def __init__(self):
                self.EMOTIONS = { 'happy': 0, 'neutral': 1, 'sad': 2, 'angry': 3 }
                self.num_sample = 60
                self.epochs = 10
                self.graph = tf.get_default_graph()
                
                with self.graph.as_default():
                        self.model = Sequential()
                        self.model.add(Conv2D(32, (2, 2), input_shape=(self.num_sample, 26, 1), padding='same', activation='relu'))
                        self.model.add(Conv2D(32, (2, 2), padding='same', activation='relu'))
                        self.model.add(MaxPool2D(pool_size=(2, 2)))
                        self.model.add(Conv2D(32, (2, 2), padding = 'same', activation='relu'))
                        self.model.add(Conv2D(32, (2, 2), padding = 'same', activation='relu'))
                        self.model.add(Flatten())
                        self.model.add(Dense(1024, activation='relu'))
                        # TODO(raise ValueError: Tensor("dense_2/Softmax:0", shape=(?, 5), dtype=float32) is not an element of this graph.)
                        self.model.add(Dense(len(self.EMOTIONS), activation='softmax'))
                        # 모델 학습과정
                        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])


        def load_dataset(self, csv='./dataset/dataset.csv'):
        
                handle = open(csv, 'r')
                rawlines = handle.read().split('\n')
                handle.close()
                datalist = [line.split(',') for line in rawlines]
                shuffle(datalist)
                cnt = 0
                processed_x = []
                processed_y = []
                for url, target_emotion in datalist:
                        if url in ['YAF_germ_angry.wav']: continue
                        if cnt == 1560 : break
                        #print(url,cnt)
                        rate, signal = wav.read('./dataset/tess/' +url)
                        filter_bank_feature = log_filter_bank(signal, rate)
                        #filter_bank_feature = preprocessor.process('./dataset/tess/'+url)
                        #processed_x.append(filter_bank_feature)
                        processed_x.append(filter_bank_feature[:self.num_sample, :])
                        processed_y.append(self.EMOTIONS[target_emotion])
                        cnt = cnt+1
                processed_x = np.array(processed_x).reshape(-1, self.num_sample, 26, 1)
                processed_y = np_utils.to_categorical(processed_y)

                train_data_ratio = 0.9
                num_train_data = int(len(datalist) * train_data_ratio)

                self.train_data_x = processed_x[:num_train_data]
                self.train_data_y = processed_y[:num_train_data]
                self.test_data_x = processed_x[num_train_data:]
                self.test_data_y = processed_y[num_train_data:]

                #print(len(self.train_data_x))
                #print(len(self.train_data_y))
        def load_dataset2(self, csv='./dataset/input.csv'):

                handle = open(csv, 'r')
                rawlines = handle.read().split('\n')
                handle.close()
                datalist = [line.split(',') for line in rawlines]
                shuffle(datalist)
                cnt = 0
                processed_x = []
                processed_y = []
                for url, target_emotion in datalist:
                        if url in ['YAF_germ_angry.wav']: continue
                        if cnt == 1560 : break
                        #print(url,cnt)
                        rate, signal = wav.read('./dataset/tess/' +url)
                        filter_bank_feature = log_filter_bank(signal, rate)
                        #filter_bank_feature = preprocessor.process('./dataset/tess/'+url)
                        #processed_x.append(filter_bank_feature)
                        processed_x.append(filter_bank_feature[:self.num_sample, :])
                        processed_y.append(self.EMOTIONS[target_emotion])
                        cnt = cnt+1
                processed_x = np.array(processed_x).reshape(-1, self.num_sample, 26, 1)
                processed_y = np_utils.to_categorical(processed_y)
                train_data_ratio = 0.9
                num_train_data = int(len(datalist) * train_data_ratio)
                self.train_data_x = processed_x[:num_train_data]
                self.train_data_y = processed_y[:num_train_data]
                self.test_data_x = processed_x[num_train_data:]
                self.test_data_y = processed_y[num_train_data:]
                print(len(self.train_data_x))
                print(len(self.train_data_y))
                
                
        def train(self):
                self.load_dataset()
                with self.graph.as_default():
                        hist = self.model.fit(self.train_data_x, self.train_data_y, epochs=self.epochs, batch_size=32 )                                            
                        print('>> training result')
                        print(hist)
                        self.histogram(hist)

        def train2(self):
                self.load_dataset()
                with self.graph.as_default():
 #                       hist2 = self.model.fit(self.train_data_x, self.train_data_y, epochs=self.epochs,batch)
                        print('neural2 result')
                        print(hist2)
                        self.histgram(hist2)
                        
        def test(self):
                loss_and_metrics = self.model.evaluate(self.test_data_x, self.test_data_y, batch_size=26)
                print('>> test result')
                print(loss_and_metrics)

        def process(path, num_sample=32):
                rate, signal = wav.read(path)
                filter_bank_feature = log_filter_bank(signal, rate)
                return filter_bank_feature[:num_sample, :]

        def predict(self, x):
                #x = self.process('./dataset/tess/' + 'OAF_back_happy.wav')
                with self.graph.as_default():
                        x = np.array([x]).reshape(-1, self.num_sample, 26, 1)
                        # x = self.train_data_x[:2]
                        # self.model._make_predict_function()
                        prediction = self.model.predict(x, batch_size=32)
                        print('prediction:', prediction)
                        print('y[:2]:', self.test_data_y[:2])
                        return {
                                'happy': float(prediction[0][0]),
                                'neutral': float(prediction[0][1]),
                                'sad': float(prediction[0][2]),
                                'angry': float(prediction[0][3]),
                   #             'disgust': float(prediction[0][4])
                                

                        }

        def save(self):
                self.model.save('cnn_emotion.h5')

        def load(self):
                self.model = load_model('cnn_emotion.h5')

        def histogram(self, hist):
                fig, loss_ax = plt.subplots()
                acc_ax = loss_ax.twinx()
                loss_ax.plot(hist.history['loss'], 'y', label='train loss')
                acc_ax.plot(hist.history['acc'], 'b', label='train acc')
                loss_ax.set_xlabel('epoch')
                loss_ax.set_ylabel('loss')
                acc_ax.set_ylabel('accuray')
                loss_ax.legend(loc='upper left')
                acc_ax.legend(loc='lower left')
                plt.show()

if __name__ == '__main__':
        model = Model()
#
#
#model.load()
        model.load_dataset()
        model.train()
        #model.load()
        #model.save()
        model.test()
        #print(model.train_data_x[:150])
        print(model.predict(model.train_data_x[:150]))

