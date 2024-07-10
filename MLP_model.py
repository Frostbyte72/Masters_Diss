from tensorflow import keras
import pandas as pd
import numpy as np

# create and complile model.
def create_model(shape,loss_function,optimiser,layer_size,activation,dropout):
    
    model = keras.models.Sequential()
    
    model.add(keras.layers.Dense(layer_size, input_shape=(shape,), name = 'Layer1')) #setsup first hidden layer aswell as defing the input layers shape
    model.add(keras.layers.Dropout(rate=dropout)) 
    model.add(keras.layers.Dense(layer_size, activation=activation, name = 'Layer2'))

    #Compile defines the loss function, the optimizer and the metrics. That's all.
    model.compile(loss=loss_function, optimizer=optimiser, metrics=['MSE','mae', 'mape'] )

    model.summary()

    return model

#Retrive dataset
data = pd.read_csv('Input.csv')
y = data['Correlation']
x = data.drop(columns=['Period','Correlation','Ticker1','Ticker2'])

model = create_model(len(x.columns),'MSE','adam',32,'relu',0.1)
model.fit(x , y, epochs = 32, batch_size = 1)
