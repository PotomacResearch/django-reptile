import numpy as np
import rescompy
from reptile import Library, Autoencoder, RepTiLe

'''
???
data[5][2][7] = timepoint 5, dimension 2, library member 7
'''


filename = r'C:\Downloads\VIX_OpenHighLowCloseAdjclose_Day.csv'

# In data in columns, with last column as time
data = np.genfromtxt(filename, delimiter=',')

# Reshape to rows, keep one for testing, take out time
num_test_data = 2
train_data = data[:,:-(num_test_data+1)].T
num_train_data = train_data.shape[0]
test_data = data[:,-(num_test_data+1):-1].T
time_data = data[:, -1].T

lib = Library(train_data, t=time_data, name='traincsv')
lib.plot_series([i for i in range(num_train_data)])

lib.save('train_csv_library', False)

esn = rescompy.ESN(input_dimension=1, size=250, connections=25,
                    spectral_radius=1.1, input_strength=0.25,
                    bias_strength=1.5, leaking_rate=0.014)
autoencoder = Autoencoder(input_dim=500, hidden_dim=[500, 200],
                          encoder_dim=3, learning_rate=0.0001,
                          bounded_latent=True)

reptile = RepTiLe(lib, esn, autoencoder, None)
reptile.save('train_csv_reptile', False)

reptile.train_library(transient_length=100, reg=1e-1)
performance_unoptimized = reptile.diagnose_library(
                                            num_diagnose_series=num_train_data,
                                            plot_summary=False)

#reptile.train_autoencoder(epochs=250000, patience=25000)
reptile.train_autoencoder(epochs=2500, patience=250)
reptile.autoencoder.plot_fit()
reptile.plot_latent_space()
_ = reptile.diagnose_autoencoder(plot_summary=True)


lib_test = Library(test_data, t=time_data, name='testcsv')
lib_test.plot_series([i for i in range(num_test_data)])

# Try 'interpolation' mode first, where observations are randomly sampled.
# Use the sample method to generate observations.
# The predict method returns a rescompy.predict_result object, which we can use
# to analyze further, but we are just going to plot the results.
results = list()
for i in range(num_test_data):
    index = i
    observations = lib_test.sample(num_samples=100,
                                   #prediction=True,
                                   index=index,
                                   transient_length=100)
    results.append(reptile.predict(observations=observations,
                                   ground_truth=lib_test.data[index],
                                   plot=True))

# Next, try setting prediction=True.
for i in range(num_test_data):
    index = i
    observations = lib_test.sample(num_samples=50,
                                   prediction=True,
                                   index=index,
                                   transient_length=100)
    _ = reptile.predict(observations=observations,
                                     ground_truth=lib_test.data[index],
                                     plot=True)

reptile.save('tested_reptile', False)
