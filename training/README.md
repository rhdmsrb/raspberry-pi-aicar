# Training

`make_model.ipynb` trains the lane-navigation CNN: it loads labeled frames, splits them into train and validation sets, builds the PilotNet-style model, trains it, and checks the predictions.

The training data (`video.zip`) isn't included in this repo. To re-run the notebook, put the archive in this folder as `video.zip` and adjust the paths and package versions to your environment. The frames are produced by the scripts in `examples/training_data_collection/` (file names end in the steering-angle label, e.g. `train_00020_135.png`).
