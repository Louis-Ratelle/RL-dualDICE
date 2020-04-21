import concurrent.futures
import multiprocessing
from functools import partial
import numpy as np
import matplotlib.pyplot as plt

from run_exp import *

def run_seeds_in_parallel(nb_processes, partial_fct, estimator_names, nb_seeds=12):
    seeds = range(nb_seeds)

    res = np.zeros((len(estimator_names), nb_seeds), dtype = np.float32)
    with concurrent.futures.ProcessPoolExecutor(nb_processes) as executor:
        for ret, k in executor.map(partial_fct, seeds):
            res[:, k] = ret

    for k in seeds:
        print('------seed = {}------'.format(k))
        for i in range(len(estimator_names)):
            print('  ESTIMATOR: '+estimator_names[i]+ ', rewards = {}'.format(res[i,k]))
        print('----------------------')
        sys.stdout.flush()
    
    #executor.terminate()
    return res

def varying_number_trajectories(estimator_names, nt_list = [200, 500, 1000, 2000]):
    """
    Run multiple experiments that vary the number of trajectories
    """
    # environment
    length = 5
    env = taxi(length)
    n_state = env.n_state
    n_action = env.n_action

    # Policies
    alpha = 0.0 # mixture ratio
    pi_target = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi19.npy')
    pi_behavior = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi18.npy')
    pi_behavior = alpha * pi_target + (1-alpha) * pi_behavior

    # Sampling vars
    ts = 400 # truncate_size
    gm = 0.99 # gamma
    nb_seeds = 12

    results = np.zeros( (len(nt_list), len(estimator_names), nb_seeds) )
    for idx, nt in enumerate(nt_list):
        lam_fct = partial(run_wrapper, n_state, n_action, env, roll_out, on_policy, estimator_names, pi_behavior, 
                          pi_target, nt, ts, gm)
        ret = run_seeds_in_parallel(int(multiprocessing.cpu_count() / 4), lam_fct, estimator_names)
        results[idx, :, :] = ret

    return results


def varying_gamma(estimator_names, gm_list = [200, 500, 1000, 2000]):
    """
    Run multiple experiments that vary the number of trajectories
    """
    # environment
    length = 5
    env = taxi(length)
    n_state = env.n_state
    n_action = env.n_action

    # Policies
    alpha = 0.0 # mixture ratio
    pi_target = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi19.npy')
    pi_behavior = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi18.npy')
    pi_behavior = alpha * pi_target + (1-alpha) * pi_behavior

    # Sampling vars
    ts = 400 # truncate_size
    nt = 1000
    nb_seeds = 12

    results = np.zeros( (len(gm_list), len(estimator_names), nb_seeds) )
    for idx, gm in enumerate(gm_list):
        lam_fct = partial(run_wrapper, n_state, n_action, env, roll_out, on_policy, estimator_names, pi_behavior, 
                          pi_target, nt, ts, gm)
        ret = run_seeds_in_parallel(int(multiprocessing.cpu_count() / 4), lam_fct, estimator_names)
        results[idx, :, :] = ret

    return results

def varying_target_mixture(estimator_names, alpha_list = [0.0, 0.2, 0.5, 0.7]):
    """
    Run multiple experiments that vary the number of trajectories
    """
    # environment
    length = 5
    env = taxi(length)
    n_state = env.n_state
    n_action = env.n_action

    # Policies
    pi_target = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi19.npy')
    pi_behavior = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi18.npy')

    # Sampling vars
    ts = 400 # truncate_size
    nt = 1000
    gm = 0.99
    nb_seeds = 12

    results = np.zeros( (len(alpha_list), len(estimator_names), nb_seeds) )
    for idx, alpha in enumerate(alpha_list):
        pi_behavior = alpha * pi_target + (1-alpha) * pi_behavior
        lam_fct = partial(run_wrapper, n_state, n_action, env, roll_out, on_policy, estimator_names, pi_behavior, 
                          pi_target, nt, ts, gm)
        ret = run_seeds_in_parallel(int(multiprocessing.cpu_count() / 4), lam_fct, estimator_names)
        results[idx, :, :] = ret

    return results

def varying_trajectories_and_alpha(estimator_names, nt_list, alpha_list):
    # environment
    length = 5
    env = taxi(length)
    n_state = env.n_state
    n_action = env.n_action

    # Policies
    pi_target = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi19.npy')
    pi_behavior = np.load(os.getcwd() + '/infinite-horizon-off-policy-estimation/taxi/taxi-policy/pi18.npy')

    # Sampling vars
    ts = 400 # truncate_size
    gm = 0.995
    nb_seeds = 12

    results = np.zeros( (len(alpha_list), len(nt_list), len(estimator_names), nb_seeds) )
    for i, alpha in enumerate(alpha_list):
        for j, nt in enumerate(nt_list):
            pi_behavior = alpha * pi_target + (1-alpha) * pi_behavior
            lam_fct = partial(run_wrapper, n_state, n_action, env, roll_out, on_policy, estimator_names, pi_behavior, 
                            pi_target, nt, ts, gm)
            ret = run_seeds_in_parallel(int(multiprocessing.cpu_count() / 4), lam_fct, estimator_names)
            results[i, j, :, :] = ret

    return results

if __name__ == "__main__":
    estimator_names = ['On Policy', 'Density Ratio', 'Naive Average', 'IST', 'ISS', 'WIST', 'WISS', 'Model Based', 'DualDICE']
    
    if not os.path.exists(os.getcwd() + "/result"):
            os.mkdir(os.getcwd() + "/result")

    run_data_gen = False
    nt_list = [200, 500, 1000, 2000]
    gm_list = [0.999, 0.9, 0.8, 0.7, 0.5]
    alpha_list = [0.0, 0.2, 0.5, 0.7]
    if run_data_gen:
        # Number of trajectories
        results = varying_number_trajectories(estimator_names, nt_list)
        np.save(os.getcwd() + '/result/varying_nb_trajectories_{}.npy'.format("_".join([str(i) for i in nt_list])), results)
        
        # Changing Gamma
        results = varying_gamma(estimator_names, gm_list)
        np.save(os.getcwd() + '/result/varying_gamma_{}.npy'.format("_".join([str(i) for i in gm_list])), results)

        # Changing Gamma
        results = varying_target_mixture(estimator_names, alpha_list)
        np.save(os.getcwd() + '/result/varying_target_alpha_{}.npy'.format("_".join([str(i) for i in alpha_list])), results)

    # Reproducing graph in dual dice for taxi
    alpha_list = [0.0, 0.33, 0.66]
    nt_list = [500, 1000, 2000, 3000]
    results = varying_trajectories_and_alpha(estimator_names, nt_list, alpha_list)
    np.save(os.getcwd() + '/result/varying_alpha_and_nt_({})_({}).npy'.format(
        "_".join([str(i) for i in alpha_list]),
        "_".join([str(i) for i in nt_list])),
        results)
    
    # plot
    trajectory_results = np.load( os.getcwd() + '/result/varying_nb_trajectories_{}.npy'.format("_".join([str(i) for i in nt_list])) )
    gamma_results = np.load( os.getcwd() + '/result/varying_gamma_{}.npy'.format("_".join([str(i) for i in gm_list])) )
    misture_policy_results = np.load( os.getcwd() + '/result/varying_target_alpha_{}.npy'.format("_".join([str(i) for i in alpha_list])) )
    alpha_trajectories_results = np.load(os.getcwd() + '/result/varying_alpha_and_nt_({})_().npy'.format(
        "_".join([str(i) for i in alpha_list]),
        "_".join([str(i) for i in nt_list])))

    trajectory_results_min = trajectory_results.min(axis=-1)
    trajectory_results_mean = trajectory_results.mean(axis=-1)
    trajectory_results_max = trajectory_results.max(axis=-1)

    gamma_results_min = gamma_results.min(axis=-1)
    gamma_results_mean = gamma_results.mean(axis=-1)
    gamma_results_max = gamma_results.max(axis=-1)

    misture_policy_results_min = misture_policy_results.min(axis=-1)
    misture_policy_results_mean = misture_policy_results.mean(axis=-1)
    misture_policy_results_max = misture_policy_results.max(axis=-1)

    alpha_trajectories_min = alpha_trajectories_results.min(axis=-1)
    alpha_trajectories_mean = alpha_trajectories_results.mean(axis=-1)
    alpha_trajectories_max = alpha_trajectories_results.max(axis=-1)

    # Plot number of trajectories
    plt.plot(nt_list, trajectory_results_mean[:, 0],
            nt_list, trajectory_results_mean[:, -1])
    plt.fill_between(nt_list, trajectory_results_min[:, 0], trajectory_results_max[:, 0], color='pink', alpha=0.5)
    plt.fill_between(nt_list, trajectory_results_min[:, -1], trajectory_results_max[:, -1], color='grey', alpha=0.5)
    plt.show()

    # Plot gamma changes
    plt.plot(gm_list, gamma_results_mean[:, 0],
            gm_list, gamma_results_mean[:, -1])
    plt.fill_between(gm_list, gamma_results_min[:, 0], gamma_results_max[:, 0], color='grey', alpha=0.5)
    plt.fill_between(gm_list, gamma_results_min[:, -1], gamma_results_max[:, -1], color='pink', alpha=0.5)
    plt.show()

    # Policy change
    plt.plot(alpha_list, misture_policy_results_mean[:, 0],
            alpha_list, misture_policy_results_mean[:, -1])
    plt.fill_between(alpha_list, misture_policy_results_min[:, 0], misture_policy_results_max[:, 0], color='grey', alpha=0.5)
    plt.fill_between(alpha_list, misture_policy_results_min[:, -1], misture_policy_results_max[:, -1], color='pink', alpha=0.5)
    plt.show()

    # Reproducing graph
    plt.subplot(131)# alpha = 0.0
    plt.plot(gm_list, alpha_trajectories_mean[0, :, 0],
            gm_list, alpha_trajectories_mean[0, :, -1])
    plt.fill_between(alpha_list, alpha_trajectories_min[0, :, 0], alpha_trajectories_max[0, :, 0], color='grey', alpha=0.5)
    plt.fill_between(alpha_list, alpha_trajectories_min[0, :, -1], alpha_trajectories_max[0, :, -1], color='pink', alpha=0.5)

    plt.subplot(132) # alpha = 0.33
    plt.plot(gm_list, alpha_trajectories_mean[1, :, 0],
            gm_list, alpha_trajectories_mean[1, :, -1])
    plt.fill_between(alpha_list, alpha_trajectories_min[1, :, 0], alpha_trajectories_max[1, :, 0], color='grey', alpha=0.5)
    plt.fill_between(alpha_list, alpha_trajectories_min[1, :, -1], alpha_trajectories_max[1, :, -1], color='pink', alpha=0.5)

    plt.subplot(133) # alpha = 0.66
    plt.plot(gm_list, alpha_trajectories_mean[2, :, 0],
            gm_list, alpha_trajectories_mean[2, :, -1])
    plt.fill_between(alpha_list, alpha_trajectories_min[2, :, 0], alpha_trajectories_max[2, :, 0], color='grey', alpha=0.5)
    plt.fill_between(alpha_list, alpha_trajectories_min[2, :, -1], alpha_trajectories_max[2, :, -1], color='pink', alpha=0.5)
    plt.show()
    

    pass


