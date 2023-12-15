# Auto-GAS

This is the code for the paper: Auto-GAS: Automated Proxy Discovery for Training-free Generation Architecture Search.

## Requirements

* Python 3.6
* PyTorch 1.0.0
* CUDA 9.0
* NVIDIA GPU + CUDA CuDNN

## Usage

### Data

Download the dataset.

### Training

Train the search space.

```
python train.py --dataset mnist --data_path data --save_path save
```

### Evaluation

Evaluate the search space.

```
python evaluate.py --dataset mnist --data_path data --save_path save
```

## Acknowledgements

This code is based on the following projects.

* [EAGAN](https://github.com/marsggbo/EAGAN)
* [NASLib](https://github.com/automl/NASLib)
* [TransBench](https://github.com/yawen-d/TransNASBench)
