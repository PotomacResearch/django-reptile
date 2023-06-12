from huey.contrib.djhuey import task

from djrep.task_helpers import start_training,save_training
from djrep.types import ReptileTypes


@task()
def run_training_task(reptile_training_id: int) -> None:
    (task_name, task_type, task_params, esn_params, autoencoder_params,
        csv_file) = start_training(reptile_training_id)

    if csv_file:
        with csv_file.open('rb') as f:
            print(f.read())

    # Import here so that Django doesn't require running reptile to serve
    #    the website
    if task_type == ReptileTypes.SINE_EXAMPLE:
        from reptile import toysystems
        from reptile.reptile import Autoencoder,RepTiLe
        import rescompy
        library = toysystems.sine_example(**task_params)

        # Save library files to permanent storage
        # Will need a way to save other than this, maybe as a single
        #    numpy file
        #library.save('sine_library', False)

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

        # Again, figure out a way to save the progress
        #reptile.save('sine_reptile', False)

        reptile.train_library(transient_length=100, reg=1e-1)
        _ = reptile.diagnose_library(num_diagnose_series=10,
                                     plot_summary=False)
        reptile.add_note('Optimized the ESN')

        reptile.train_autoencoder(epochs=25000, patience=2500)
            #epochs=250000, patience=25000)

        _ = reptile.diagnose_autoencoder()

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

    else:
        raise NotImplementedError(f'Type not implemented: {type}')

    print(f'{task_name} completed training {type}: {library}')

    save_training(reptile_training_id)
