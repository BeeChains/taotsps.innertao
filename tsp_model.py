# tsp_model.py

import requests
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
import json
import bittensor

# Configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
API_KEY = config['api_key']

# Data fetching function using Alpha Vantage API
def fetch_tao_data(api_key, symbol="TAO"):
    url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={symbol}&market=USD&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    daily_data = data.get("Time Series (Digital Currency Daily)", {})
    df = pd.DataFrame.from_dict(daily_data, orient='index', dtype=float)
    df = df.rename(columns={'4a. close (USD)': 'close_price'})
    df['close_price'] = df['close_price'].astype(float)
    return df

# Data preprocessing function
def preprocess_data(data):
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_data = scaler.fit_transform(data['close_price'].values.reshape(-1, 1))
    return scaled_data, scaler

# LSTM Model
class TSPSModel(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=100, output_size=1):
        super(TSPSModel, self).__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size)
        self.linear = nn.Linear(hidden_layer_size, output_size)
        self.hidden = (torch.zeros(1,1,self.hidden_layer_size),
                       torch.zeros(1,1,self.hidden_layer_size))

    def forward(self, input_seq):
        lstm_out, self.hidden = self.lstm(input_seq.view(len(input_seq), 1, -1), self.hidden)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]

# Sequence creation for LSTM
def create_sequences(data, tw):
    inout_seq = []
    L = len(data)
    for i in range(L-tw):
        train_seq = data[i:i+tw]
        train_label = data[i+tw:i+tw+1]
        inout_seq.append((train_seq, train_label))
    return inout_seq

# Training the model
def train_model(model, train_data, epochs=150, lr=0.001):
    loss_function = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for i in range(epochs):
        for seq, labels in train_data:
            optimizer.zero_grad()
            model.hidden = (torch.zeros(1, 1, model.hidden_layer_size),
                            torch.zeros(1, 1, model.hidden_layer_size))

            y_pred = model(seq)

            single_loss = loss_function(y_pred, torch.FloatTensor(labels))
            single_loss.backward()
            optimizer.step()

        if i % 25 == 1:
            print(f'epoch {i} loss: {single_loss.item()}')

# Bittensor Subnet Initialization
def initialize_bittensor_subnet():
    # Placeholder for initializing Bittensor components (wallet, neuron, etc.)
    print("Initializing Bittensor Subnet...")
    # Actual initialization logic goes here

# Bittensor Network Interaction
def interact_with_bittensor_network(model):
    # Placeholder for TSPS's interaction logic with the Bittensor network
    print("Interacting with Bittensor Network...")
    # Actual interaction logic goes here

# Main execution
if __name__ == "__main__":
    # Initialize Bittensor Subnet
    initialize_bittensor_subnet()

    # Fetch and preprocess data
    tao_data = fetch_tao_data(API_KEY, symbol="TAO")
    tao_data_normalized, scaler = preprocess_data(tao_data)

    # Prepare training data
    train_window = config['model_params']['train_window']
    train_inout_seq = create_sequences(tao_data_normalized, train_window)

    # Initialize and train the model
    model = TSPSModel(input_size=1, hidden_layer_size=config['model_params']['hidden_layer_size'], output_size=1)
    train_model(model, train_inout_seq, epochs=150, lr=config['model_params']['learning_rate'])

    # Interact with Bittensor Network
    interact_with_bittensor_network(model)
