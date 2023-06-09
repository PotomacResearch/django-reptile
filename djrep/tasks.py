import os
from math import pi

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
        (task_name, task_type, task_params, esn_params,
             autoencoder_params) = start_training(reptile_training_id)

        base_path = Reptile.get_base_save_path(reptile_training_id)
        os.makedirs(base_path, exist_ok=True)

        data_file = base_path / ReptileParams.data_path \
                                                / ReptileParams.datafile_name

        # Import here so that Django doesn't require running reptile to serve
        #    the website
        #if task_type == ReptileTypes.SINE_EXAMPLE:
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

        elif True:
        #elif task_type == ReptileTypes.DATA_FILE:
            if os.path.exists(data_file):
                with data_file.open('rb') as f:
                    print(f.read())

            raise NotImplementedError("Library loading not implemented")

        else:
            raise NotImplementedError(f"Not implemented: {task_type}")

        from reptile.reptile import Autoencoder, RepTiLe
        import rescompy

        library.save(str(base_path / ReptileParams.library_path), False)

        default_esn_params = {
            'input_dimension': 2,
            'size': 250,
            'connections': 25,
            'spectral_radius': 1.1,
            'input_strength': 0.25,
            'bias_strength': 1.5,
            'leaking_rate': 0.014,
        }
        default_esn_params.update(esn_params)
        esn = rescompy.ESN(**default_esn_params)

        default_autoencoder_params = {
            'input_dim': 500,
            'hidden_dim': [500, 200],
            'encoder_dim': 3,
            'learning_rate': 0.0001,
            'bounded_latent': True,
        }
        default_autoencoder_params.update(autoencoder_params)
        autoencoder = Autoencoder(**default_autoencoder_params)
        reptile = RepTiLe(library, esn, autoencoder, 't')

        reptile.save(str(base_path / ReptileParams.reptile_path), False)


        # Trains the ESN on each library member and accumulates weight matrices
        update_status(reptile_training_id, "Created RepTile, training ESN")
        reptile.train_library(transient_length=100, reg=1e-1)

        # Runs a prediction on each library member, compare to original
        update_status(reptile_training_id,
                      "Trained ESN, checking performance")
        _ = reptile.diagnose_library(num_diagnose_series=10,
                     plot_members=True,
                     plot_summary=True,
                     save_dir=str(base_path / ReptileParams.esn_path))

        update_status(reptile_training_id, "Training autoencoder")
        reptile.train_autoencoder(epochs=25000, patience=2500)
            #epochs=250000, patience=25000)

        _ = reptile.diagnose_autoencoder(plot_members=True,
                 plot_summary=True,
                 save_dir=str(base_path / ReptileParams.autoencoder_path))

        """
        # Create a test library with a grid of parameters.
        library_test = toysystems.sine_example(grid=True, **task_params)

        results = list()
        for i in range(100):
            observations = library_test.sample(num_samples=100,
                                               prediction=True,
                                               index=i,
                                               transient_length=100)
            results.append(
                reptile.predict(observations=observations,
                                ground_truth=library_test.data[i],
                                )
                           )

        for i in range(100):
            observations = library_test.sample(num_samples=50,
                                               prediction=True,
                                               index=i,
                                               transient_length=100)
            _ = reptile.predict(observations=observations,
                                ground_truth=library_test.data[i],
                                )

        reptile.add_note('Fully trained')
        reptile.save(f'sine_reptile_{reptile_training_id}', False)
        """

        print(f'{task_name} completed training {type}: {library}')

        save_training(reptile_training_id)

    except Exception as e:
        update_status(reptile_training_id, f'Error: {e}')
        raise
