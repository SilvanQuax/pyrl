"""
Reproduce every figure in the paper from scratch.

"""
from __future__ import division

import argparse
import datetime
import os
import subprocess
import sys
from   os.path import join

import numpy as np

from pyrl import utils

#=========================================================================================
# Command line
#=========================================================================================

p = argparse.ArgumentParser()
p.add_argument('--simulate', action='store_true', default=False)
p.add_argument('args', nargs='*')
a = p.parse_args()

simulate = a.simulate
args     = a.args
if not args:
    args = [
        'mante', # Fig. 1
        ]

#=========================================================================================
# Shared steps
#=========================================================================================

here   = utils.get_here(__file__)
parent = utils.get_parent(here)

dopath       = join(parent, 'examples')
modelspath   = join(parent, 'examples', 'models')
analysispath = join(parent, 'examples', 'analysis')
paperpath    = join(parent, 'paper')
timespath    = join(paperpath, 'times')
#paperfigspath = join(paperpath, 'work', 'figs')

# Make paths
#utils.mkdir_p(paperfigspath)
utils.mkdir_p(timespath)

def call(s):
    if simulate:
        print(3*' ' + s)
    else:
        rval = subprocess.call(s.split())
        if rval != 0:
            sys.stdout.flush()
            print("Something went wrong (return code {}).".format(rval))
            sys.exit(1)

def clean(model):
    call("python {} {} clean"
         .format(join(dopath, 'do.py'), join(modelspath, model)))

def train(model, seed=None):
    if seed is None:
        extra  = ''
        suffix = ''
    else:
        extra = ' --seed {0} --suffix _s{0}'.format(seed)
        suffix = '_s'+str(seed)

    tstart = datetime.datetime.now()
    call("python {} {} train{}".format(join(dopath, 'do.py'),
                                       join(modelspath, model),
                                       extra))
    tend = datetime.datetime.now()

    # Save training time
    totalmins = int((tend - tstart).total_seconds()/60)
    timefile = join(timespath, model + suffix + '.txt')
    np.savetxt(timefile, [totalmins], fmt='%d', header='mins')

def train_seeds(model, start_seed=1000, n_train=1):
    for seed in xrange(start_seed, start_seed+n_train):
        print("[ train_seeds ] {}".format(seed))
        train(model, seed=seed)

def do_action(model, action, analysis=None, seed=None, args=''):
    if analysis is None:
        analysis = model.split('_')[0]

    if seed is not None:
        args = '--suffix _s{0} '.format(seed) + args

    call("python {} {} run {} {} {}".format(join(dopath, 'do.py'),
                                            join(modelspath, model),
                                            join(analysispath, analysis),
                                            action,
                                            args))

def trials(model, trialtype, ntrials, analysis=None, seed=None, args=''):
    do_action(model, 'trials-{} {}'.format(trialtype, ntrials),
              analysis=analysis, seed=seed, args=args)

def figure(fig, args=''):
    call('python {} {}'.format(join(paperpath, fig + '.py'), args))

#=========================================================================================
# Tasks
#=========================================================================================

start_seed = 101
ntrain     = 5

#-----------------------------------------------------------------------------------------
# RDM (FD)
#-----------------------------------------------------------------------------------------

model     = 'rdm_fixed'
ntrials_b = 5000
ntrials_a = 50

if 'rdm_fixed' in args:
    print("=> Perceptual decision-making (FD)")
    train(model)
    trials(model, 'b', ntrials_b)
    do_action(model, 'psychometric')
    do_action(model, 'correct_stimulus_duration')
    trials(model, 'a', ntrials_a)
    do_action(model, 'sort')

if 'rdm_fixed-seeds' in args:
    for seed in xrange(start_seed, start_seed+ntrain):
        print("=> Perceptual decision-making (FD) (seed = {})".format(seed))
        train(model, seed=seed)
        trials(model, 'b', ntrials_b, seed=seed)
        do_action(model, 'psychometric', seed=seed)
        do_action(model, 'correct_stimulus_duration', seed=seed)

#-----------------------------------------------------------------------------------------

model     = 'rdm_rt'
ntrials_b = 1000
ntrials_a = 50

if 'rdm_rt' in args:
    print("=> Perceptual decision-making (RT)")
    train(model)
    trials(model, 'b', ntrials_b)
    do_action(model, 'psychometric')
    do_action(model, 'chronometric')
    trials(model, 'a', ntrials_a)
    do_action(model, 'sort')

if 'rdm_rt-seeds' in args:
    for seed in xrange(start_seed, start_seed+ntrain):
        print("=> Perceptual decision-making (RT) (seed = {})".format(seed))
        train(model, seed=seed)
        trials(model, 'b', ntrials_b, seed=seed)
        do_action(model, 'psychometric', seed=seed)
        do_action(model, 'chronometric', seed=seed)

#-----------------------------------------------------------------------------------------
# Context-dependent integration
#-----------------------------------------------------------------------------------------

model     = 'mante'
ntrials_b = 200
ntrials_a = 20

if 'mante' in args:
    print("=> Context-dependent integration")
    train('mante')
    trials(model, 'b', ntrials_b)
    do_action(model, 'psychometric')
    trials(model, 'a', ntrials_a)
    do_action(model, 'sort')

if 'mante-seeds' in args:
    for seed in xrange(start_seed, start_seed+ntrain):
        print("=> Context-dependent integration (seed = {})".format(seed))
        train(model, seed=seed)
        trials(model, 'b', ntrials_b, seed=seed)
        do_action(model, 'psychometric', seed=seed)

#-----------------------------------------------------------------------------------------
# Multisensory integration
#-----------------------------------------------------------------------------------------

model     = 'multisensory'
ntrials_b = 1500
ntrials_a = 100

if 'multisensory' in args:
    print("=> Multisensory integration")
    train(model)
    trials(model, 'b', ntrials_b)
    do_action(model, 'psychometric')
    trials(model, 'a', ntrials_a)
    do_action(model, 'sort')

if 'multisensory-seeds' in args:
    for seed in xrange(start_seed, start_seed+ntrain):
        print("=> Multisensory integration (seed = {})".format(seed))
        train(model, seed=seed)
        trials(model, 'b', ntrials_b, seed=seed)
        do_action(model, 'psychometric', seed=seed)

#-----------------------------------------------------------------------------------------
# Parametric working memory
#-----------------------------------------------------------------------------------------

model     = 'romo'
ntrials_b = 100
ntrials_a = 20

if 'romo' in args:
    print("=> Parametric working memory")
    train('romo')
    trials(model, 'b', ntrials_b)
    do_action(model, 'performance')
    trials(model, 'a', ntrials_a)
    do_action(model, 'sort')
    do_action(model, 'sort', args='value')

if 'romo-seeds' in args:
    for seed in xrange(start_seed, start_seed+ntrain):
        print("=> Parametric working memory (seed = {})".format(seed))
        train(model, seed=seed)
        trials(model, 'b', ntrials_b, seed=seed)
        do_action(model, 'performance', seed=seed)

#-----------------------------------------------------------------------------------------
# Postdecision wager
#-----------------------------------------------------------------------------------------

model     = 'postdecisionwager'
ntrials_b = 2500
ntrials_a = 100

if 'postdecisionwager' in args:
    print("=> Postdecision wager")
    train(model)
    trials(model, 'b', ntrials_b)
    do_action(model, 'sure_stimulus_duration')
    do_action(model, 'correct_stimulus_duration')
    trials(model, 'a', ntrials_a)
    do_action(model, 'sort')
    do_action(model, 'sort', args='value')

if 'postdecisionwager-seeds' in args:
    for seed in xrange(start_seed, start_seed+ntrain):
        print("=> Postdecision wager (seed = {})".format(seed))
        train(model, seed=seed)

#-----------------------------------------------------------------------------------------
# Economic choice
#-----------------------------------------------------------------------------------------

model     = 'padoaschioppa2006'
ntrials_b = 200
ntrials_a = 200

if 'padoaschioppa2006' in args:
    print("=> Padoa-Schioppa 2006")
    train('padoaschioppa2006')
    trials(model, 'b', ntrials_b)
    do_action(model, 'choice_pattern')
    trials(model, 'a', ntrials_a)
    do_action(model, 'sort_epoch', args='postoffer value')
    do_action(model, 'sort_epoch', args='latedelay value')
    do_action(model, 'sort_epoch', args='prechoice value')
    do_action(model, 'sort_epoch', args='prechoice value separate-by-choice')

if 'padoaschioppa2006-seeds' in args:
    for seed in xrange(start_seed, start_seed+ntrain):
        print("=> Padoa-Schioppa 2006 (seed = {})".format(seed))
        train(model, seed=seed)

if 'padoaschioppa2006-1A3B' in args:
    train(model+'_1A3B')
    trials(model+'_1A3B', 'b', ntrials_b)
    do_action(model+'_1A3B', 'choice_pattern')

#=========================================================================================
# Paper figures
#=========================================================================================

if 'fig1_rdm' in args:
    figure('fig1_rdm')

if 'fig_cognitive' in args:
    figure('fig_cognitive')

if 'fig_postdecisionwager' in args:
    figure('fig_postdecisionwager')

if 'fig_padoaschioppa2006' in args:
    figure('fig_padoaschioppa2006')

if 'fig_rdm_rt' in args:
    figure('fig_rdm_rt')

if 'fig-learning-mante' in args:
    figure('fig_learning', args='mante')

if 'fig-learning-multisensory' in args:
    figure('fig_learning', args='multisensory')

if 'fig-learning-romo' in args:
    figure('fig_learning', args='romo')

if 'fig-learning-postdecisionwager' in args:
    figure('fig_learning', args='postdecisionwager')

if 'fig-learning-padoaschioppa2006' in args:
    figure('fig_learning', args='padoaschioppa2006')