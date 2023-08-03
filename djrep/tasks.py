import os

from huey.contrib.djhuey import task

from djrep.task_helpers import start_training, save_training, update_status
from djrep.models import Reptile
from djrep.reptile import ReptileParams


@task()
def run_training_task(reptile_training_id: int) -> None:
    """
    1. Training ESN on library with/without automatic hyperparameter
        optimization

        - Show fast feedback on frontend for parameters, showing reconstruction
        - Training does real training and does diagnose library (just ESN)
        - Once that looks good, set autoencoder training and hit go
        - Once complete, get diagnose error
        - Then run prediction task -- prediction values (maybe latent variables)
        - Finally, do all this for 10 seeds and then report the median

    I think the pattern should be
        - Save number / figure summaries to display on the website
        - Save actual results as files that can be downloaded
        - Save any intermediate data in a unique dir
    """
    try:
        (task_name, library_params, esn_params, autoencoder_params,
         data_file_path, dataset_params) = start_training(reptile_training_id)

        base_path = Reptile.get_base_save_path(reptile_training_id)
        os.makedirs(base_path, exist_ok=True)

        # Imports inside the function so that Django doesn't require running
        #    reptile/numpy/whatever to serve the website
        import numpy as np
        import rescompy
        from reptile.reptile import Autoencoder, RepTiLe, Library


        #if task_type == ReptileTypes.SINE_EXAMPLE:
        '''
        if False:
        from reptile import toysystems

        sine_params = {
            'num_series': 100,
            'length_series': 1100,
            'amplitude_low': 0.1,
            'amplitude_high': 5.0,
            'frequency_low': 1.0,
            'frequency_high': 1.0,
            'phase_low': 0,
            'phase_high': pi,
        }
        library = toysystems.sine_example(**sine_params)
        '''

        # In data in columns, with last column as time
        data = np.genfromtxt(data_file_path, delimiter=',')

        # Reshape to rows, keep one for testing, take out time
        # data[5][2][7] = timepoint 5, dimension 2, library member 7
        num_test_data = 0
        train_data = data[:,:-(num_test_data+1)].T
        num_train_data = train_data.shape[0]
        test_data = data[:,-(num_test_data+1):-1].T
        time_data = data[:, -1].T

        lib = Library(train_data, t=time_data, name='reptilelibrary')
        #lib.plot_series([i for i in range(num_train_data)])

        lib.save(str(base_path / ReptileParams.library_path), False)

        default_esn_params = {
            'input_dimension': 2,
            'size': 250,
            'connections': 25,
            'spectral_radius': 1.1,
            'input_strength': 0.25,
            'bias_strength': 1.5,
            'leaking_rate': 0.014,

            'transient_length': 100,
            'reg': 1e-1,
        }
        default_esn_params.update(esn_params)
        esn = rescompy.ESN(**default_esn_params)

        default_autoencoder_params = {
            'input_dim': 500,
            'hidden_dim': [500, 200],
            'encoder_dim': 3,
            'learning_rate': 0.0001,
            'bounded_latent': True,

            'epochs': 25000,
            'patience': 2500,
        }
        default_autoencoder_params.update(autoencoder_params)
        autoencoder = Autoencoder(**default_autoencoder_params)

        reptile = RepTiLe(lib, esn, autoencoder, 't')
        reptile.save(str(base_path / ReptileParams.reptile_path), False)

        # Trains the ESN on each library member and accumulates weight matrices
        update_status(reptile_training_id, "Created RepTile, training ESN")
        reptile.train_library(**default_esn_params)

        update_status(reptile_training_id, "Trained ESN, checking performance")
        _ = reptile.diagnose_library(num_diagnose_series=num_train_data,
                             plot_members=True,
                             plot_summary=True,
                             save_dir=str(base_path / ReptileParams.esn_path))

        update_status(reptile_training_id, "Training autoencoder")

        reptile.train_autoencoder(**default_autoencoder_params)
            #epochs=250000, patience=25000)

        _ = reptile.diagnose_autoencoder(plot_members=True,
                 plot_summary=True,
                 save_dir=str(base_path / ReptileParams.autoencoder_path))


        '''
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

        '''

        print(f'{task_name} completed training {type}: {lib}')

        save_training(reptile_training_id)

    except Exception as e:
        update_status(reptile_training_id, f'Error: {e}')
        raise
