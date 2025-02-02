from .trainer import Trainer
from ..utils import plot_utils as pu

import logging
from tqdm import trange
import os

log = logging.getLogger("dyn train")


class PETSDynamicsTrainer(Trainer):
    def __init__(self, cfg, dynamics, loss_plotter):
        self.cfg = cfg
        self.dynamics = dynamics
        self.loss_plotter = loss_plotter

        self.ensemble = cfg.dyn_n_models

        self.env_name = cfg.env

    def initial_train(self, replay_buffer, update_dir):
        if self.dynamics.trained:
            self.visualize(os.path.join(update_dir, "dyn_start.gif"), replay_buffer)
            return

        log.info('Beginning dynamics initial optimization')

        for i in range(self.cfg.dyn_init_iters):
            out_dict = replay_buffer.sample(self.cfg.dyn_batch_size,
                                            ensemble=self.ensemble)
            obs, next_obs, act = out_dict['obs'], out_dict['next_obs'], out_dict['action']

            loss, info = self.dynamics.update(obs, next_obs, act, already_embedded=True)

            self.loss_plotter.add_data(info)

            if i % self.cfg.log_freq == 0:
                self.loss_plotter.print(i)
            if i % self.cfg.plot_freq == 0:
                log.info('Creating dynamics visualization')
                self.loss_plotter.plot()

                print(f'started visualize')
                self.visualize(os.path.join(update_dir, "dyn%d.gif" % i), replay_buffer)
                print(f'end visualize')

            if i % self.cfg.checkpoint_freq == 0 and i > 0:
                self.dynamics.save(os.path.join(update_dir, 'dynamics_%d.pth' % i))

        self.dynamics.save(os.path.join(update_dir, 'dyn.pth'))

    def update(self, replay_buffer, update_dir):
        log.info('Beginning dynamics optimization')

        for _ in trange(self.cfg.dyn_update_iters):
            out_dict = replay_buffer.sample(self.cfg.dyn_batch_size,
                                            ensemble=self.ensemble)
            obs, next_obs, act = out_dict['obs'], out_dict['next_obs'], out_dict['action']

            loss, info = self.dynamics.update(obs, next_obs, act, already_embedded=True)
            self.loss_plotter.add_data(info)

        log.info('Creating dynamics heatmap')
        self.loss_plotter.plot()
        self.visualize(os.path.join(update_dir, "dyn.gif"), replay_buffer)
        self.dynamics.save(os.path.join(update_dir, 'dyn.pth'))

    def visualize(self, file, replay_buffer):
        print('started visualize function')
        out_dict = replay_buffer.sample_chunk(8, 10)
        obs = out_dict['obs']
        act = out_dict['action']
        # pu.visualize_dynamics(obs, act, self.dynamics, self.dynamics.encoder, file, self.cfg.obs_type)
