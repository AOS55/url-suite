from .trainer import Trainer
from ..utils import plot_utils as pu

import logging
from tqdm import trange
import os

log = logging.getLogger("ss train")


class SafeSetTrainer(Trainer):
    def __init__(self, env, cfg, safe_set, loss_plotter):
        self.cfg = cfg
        self.safe_set = safe_set
        self.loss_plotter = loss_plotter
        self.env = env

        self.env_name = cfg.env
        self.ss_type = cfg.safe_set_type
        self.ensemble = cfg.safe_set_n_models if cfg.safe_set_ensemble else 0
        self.ensemble = 0
        self.batch_size = cfg.safe_set_batch_size

    def initial_train(self, replay_buffer, update_dir):
        if self.safe_set.trained:
            # self.plot(os.path.join(update_dir, "safe_set_start.pdf"), replay_buffer)
            return

        log.info('Beginning safe set initial optimization')

        for i in range(self.cfg.safe_set_init_iters):
            self._sample_and_update(replay_buffer)

            if i % self.cfg.log_freq == 0:
                self.loss_plotter.print(i)
            if i % self.cfg.plot_freq == 0:
                log.info('Creating safe set heatmap')
                self.loss_plotter.plot()
                self.plot(os.path.join(update_dir, "ss%d.pdf" % i), replay_buffer)
            if i % self.cfg.checkpoint_freq == 0 and i > 0:
                self.safe_set.save(os.path.join(update_dir, 'safe_set_%d.pth' % i))

        self.safe_set.save(os.path.join(update_dir, 'ss.pth'))

    def update(self, replay_buffer, update_dir):
        log.info('Beginning safe set optimization')

        for _ in trange(self.cfg.safe_set_update_iters):
            self._sample_and_update(replay_buffer)

        log.info('Creating safe set heatmap')
        self.loss_plotter.plot()
        self.safe_set.save(os.path.join(update_dir, 'ss.pth'))
        self.plot(os.path.join(update_dir, "ss.pdf"), replay_buffer)

        # return heatmap

    def _sample_and_update(self, replay_buffer):
        if self.ss_type == 'ex2':
            out_dict = replay_buffer.sample(self.batch_size, self.ensemble)
            out_dict_pos = replay_buffer.sample_positive(self.batch_size, 'safe_set', self.ensemble)
            obs = out_dict['obs']
            obs_pos = out_dict_pos['obs']

            loss, info = self.safe_set.update(obs, obs_pos, already_embedded=True)
        elif self.ss_type == 'rnd':
            out_dict = replay_buffer.sample_positive(self.batch_size, 'safe_set', self.ensemble)
            obs = out_dict['obs']

            loss, info = self.safe_set.update(obs, already_embedded=True)
        else:
            out_dict = replay_buffer.sample(self.batch_size, self.ensemble)\

            loss, info = self.safe_set.update(out_dict, already_embedded=True)
        self.loss_plotter.add_data(info)

    def plot(self, file, replay_buffer):
        out_dict = replay_buffer.sample(self.cfg.safe_set_batch_size)
        obs = out_dict['obs']
        pu.visualize_safe_set(obs, self.safe_set, file, env=self.env, obs_type=self.cfg.obs_type)
