from ..rl_trainers import VAETrainer, SafeSetTrainer, Trainer, \
    ValueTrainer, ConstraintTrainer, GoalIndicatorTrainer, PETSDynamicsTrainer

from ..utils import LossPlotter, EncoderDataLoader

import os


class MPCTrainer(Trainer):

    def __init__(self, env, cfg, modules):

        self.cfg = cfg
        self.env = env

        self.logdir = cfg.log_dir

        loss_plotter = LossPlotter(os.path.join(self.logdir, 'loss_plots'))

        self.trainers = []

        if self.cfg.obs_type == 'pixels':
            self.trainers.append(VAETrainer(cfg, modules['enc'], loss_plotter))
        self.trainers.append(PETSDynamicsTrainer(cfg, modules['dyn'], loss_plotter))
        self.trainers.append(ValueTrainer(env, cfg, modules['val'], loss_plotter))
        self.trainers.append(SafeSetTrainer(env, cfg, modules['ss'], loss_plotter))
        self.trainers.append(ConstraintTrainer(env, cfg, modules['constr'], loss_plotter))
        self.trainers.append(GoalIndicatorTrainer(env, cfg, modules['gi'], loss_plotter))

    def initial_train(self, replay_buffer):
        update_dir = os.path.join(self.logdir, 'initial_train')
        os.makedirs(update_dir, exist_ok=True)
        for trainer in self.trainers:
            if type(trainer) == VAETrainer:

                self.encoder_data_loader = EncoderDataLoader(self.cfg.env, frame_stack=self.cfg.frame_stack)
                trainer.initial_train(self.encoder_data_loader, update_dir)
            else:
                trainer.initial_train(replay_buffer, update_dir)

    def update(self, replay_buffer, update_num):
        update_dir = os.path.join(self.logdir, 'update_%d' % update_num)
        os.makedirs(update_dir, exist_ok=True)
        for trainer in self.trainers:
            trainer.update(replay_buffer, update_dir)
