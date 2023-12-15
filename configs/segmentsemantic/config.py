from pathlib import Path

import numpy as np
import torch

import gaswot.dataset.load_ops as load_ops
import gaswot.losses.loss as loss_lib
from gaswot.optimizers.warmup import WarmupCosine
from gaswot.tnb101.models.task_models.decoder import SegmentationDecoder
from gaswot.tnb101.models.task_models.encoder import FFEncoder
from gaswot.tnb101.models.task_models.segmentation import Segmentation


def get_cfg(encoder_str):
    cfg = {}

    # basics
    cfg['encoder_str'] = encoder_str
    cfg['config_dir'] = str(Path(__file__).parent.resolve())
    cfg['task_name'] = Path(cfg['config_dir']).name

    # paths
    cfg['root_dir'] = str(
        (Path(__file__).parent / '..' / '..' / '..' / '..' / '..').resolve())
    cfg['dataset_dir'] = str(
        Path(cfg['root_dir']) / 'data/taskonomy_data/taskonomydata_mini')
    cfg['data_split_dir'] = str(
        Path(cfg['root_dir']) / 'tb101/code/experiments/final5k')
    cfg['log_dir'] = str(
        Path(cfg['root_dir']) /
        'tb101/benchmark_results/benchmark_results_local' / cfg['task_name'] /
        'model_results' / cfg['encoder_str'])

    cfg['s3_dir'] = ''  # to setup in main.py
    cfg['train_filenames'] = 'train_filenames_final5k.json'
    cfg['val_filenames'] = 'val_filenames_final5k.json'
    cfg['test_filenames'] = 'test_filenames_final5k.json'

    # data loading
    cfg['batch_size'] = 128
    cfg['num_workers'] = 8

    # inputs
    cfg['input_dim'] = (256, 256)  # (1024, 1024)
    cfg['input_num_channels'] = 3

    # targets
    cfg['target_dim'] = (256, 256)  # (256, 256)
    cfg['target_num_channel'] = 17
    cfg['target_load_fn'] = load_ops.semantic_segment_label
    cfg['target_load_kwargs'] = {}

    # demo
    cfg['demo_kwargs'] = {}

    # transform
    cfg['normal_params'] = {'mean': [0.5, 0.5, 0.5], 'std': [0.5, 0.5, 0.5]}
    cfg['train_transform_fn'] = load_ops.Compose(cfg['task_name'], [
        load_ops.ToPILImage(),
        load_ops.Resize(list(cfg['input_dim'])),
        load_ops.RandomHorizontalFlip(0.5),
        load_ops.ColorJitter(
            brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        load_ops.ToTensor(),
        load_ops.Normalize(**cfg['normal_params'])
    ])
    cfg['val_transform_fn'] = load_ops.Compose(cfg['task_name'], [
        load_ops.ToPILImage(),
        load_ops.Resize(list(cfg['input_dim'])),
        load_ops.ToTensor(),
        load_ops.Normalize(**cfg['normal_params'])
    ])

    # model
    cfg['encoder'] = FFEncoder(encoder_str, task_name=cfg['task_name']).network
    cfg['decoder_input_dim'] = (
        2048, 16,
        16) if cfg['encoder_str'] == 'resnet50' else cfg['encoder'].output_dim
    cfg['decoder'] = SegmentationDecoder(
        cfg['decoder_input_dim'],
        cfg['target_dim'],
        target_num_channel=cfg['target_num_channel'])

    cfg['model_type'] = Segmentation(cfg['encoder'], cfg['decoder'])

    # train
    cfg['fp16'] = False
    cfg['amp_opt_level'] = 'O1'
    cfg['num_epochs'] = 30
    cfg['class_weights'] = np.load(
        str(Path(cfg['root_dir']) / 'tb101/code/lib/data/seg_sem_inv.npy'))
    # cfg['criterion'] = torch.nn.CrossEntropyLoss(weight=torch.tensor(cfg['class_weights']).float().cuda())
    cfg['criterion'] = loss_lib.CrossEntropyLoss()

    # cfg['optimizer'] = torch.optim.Adam
    # cfg['initial_lr'] = 0.001
    # cfg['optimizer_kwargs'] = {
    #     "lr": cfg['initial_lr'],
    #     'weight_decay': 0.0005
    # }

    cfg['optimizer'] = torch.optim.SGD
    cfg['lr_scheduler'] = WarmupCosine
    cfg['initial_lr'] = 0.1
    cfg['optimizer_kwargs'] = {
        'lr': cfg['initial_lr'],
        'momentum': 0.9,
        'nesterov': True,
        'weight_decay': 0.0005
    }

    # cfg['identity_elems'] = {'seed': cfg['seed'], 'batch-size': cfg['batch_size'], 'lr': cfg['initial_lr']}
    cfg['metric_content'] = [
        'train_loss', 'train_acc', 'train_mIoU', 'valid_loss', 'valid_acc',
        'valid_mIoU', 'test_loss', 'test_acc', 'test_mIoU', 'time_elapsed'
    ]
    cfg['plot_msg'] = ''

    return cfg
