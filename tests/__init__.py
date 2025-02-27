# run tests: pytest -sv --cov-report term-missing --cov=workflow-miniscope -p no:warnings

import os
from attr.setters import pipe
import pytest
import pandas as pd
import pathlib
import datajoint as dj
import importlib
import numpy as np


from workflow_miniscope.paths import get_miniscope_root_data_dir
from workflow_miniscope.pipeline import Equipment



@pytest.fixture(autouse=True)
def dj_config():
    if pathlib.Path('./dj_local_conf.json').exists():
        dj.config.load('./dj_local_conf.json')
    dj.config['safemode'] = False
    dj.config['custom'] = {
        'database.prefix': (os.environ.get('DATABASE_PREFIX')
                            or dj.config['custom']['database.prefix']),
        'miniscope_root_data_dir': (os.environ.get('MINISCOPE_ROOT_DATA_DIR')
                                    or dj.config['custom']['miniscope_root_data_dir'])
    }
    return


@pytest.fixture
def pipeline():
    from workflow_miniscope import pipeline

    yield {'subject': pipeline.subject,
           'lab': pipeline.lab,
           'miniscope': pipeline.miniscope,
           'session': pipeline.session,
           'Equipment': pipeline.Equipment,
           'get_miniscope_root_data_dir': pipeline.get_miniscope_root_data_dir}

    pipeline.subject.Subject.delete()


@pytest.fixture
def subjects_csv():
    """ Create a 'subjects.csv' file"""
    input_subjects = pd.DataFrame(columns=['subject', 'sex',
                                           'subject_birth_date',
                                           'subject_description'])

    input_subjects.subject = ['LO012']
    input_subjects.sex = ['F']
    input_subjects.subject_birth_date = ['2020-01-01 00:00:01']
    input_subjects.subject_description = ['']
    input_subjects = input_subjects.set_index('subject')

    subjects_csv_path = pathlib.Path('./tests/user_data/subjects.csv')
    input_subjects.to_csv(subjects_csv_path)  # write csv file

    yield input_subjects, subjects_csv_path

    subjects_csv_path.unlink()  # delete csv file after use


@pytest.fixture
def ingest_subjects(pipeline, subjects_csv):
    from workflow_miniscope.ingest import ingest_subjects
    _, subjects_csv_path = subjects_csv
    ingest_subjects(subjects_csv_path)
    return


@pytest.fixture
def sessions_csv():
    """ Create a 'sessions.csv' file"""
    root_dir = pathlib.Path(get_miniscope_root_data_dir())

    sessions_dirs = ['LO012/20210825_234544/miniscope']

    input_sessions = pd.DataFrame(columns=['subject', 'session_dir'])
    input_sessions.subject = ['LO012']
    input_sessions.session_dir = [(root_dir / sess_dir).as_posix()
                                  for sess_dir in sessions_dirs]
    input_sessions = input_sessions.set_index('subject')

    sessions_csv_path = pathlib.Path('./tests/user_data/sessions.csv')
    input_sessions.to_csv(sessions_csv_path)  # write csv file

    yield input_sessions, sessions_csv_path

    sessions_csv_path.unlink()  # delete csv file after use


@pytest.fixture
def ingest_sessions(ingest_subjects, sessions_csv):
    from workflow_miniscope.ingest import ingest_sessions
    from workflow_miniscope.pipeline import Equipment, session

    _, sessions_csv_path = sessions_csv
    ingest_sessions(sessions_csv_path)
    session_key = dict(subject='LO012', 
                   session_datetime='2021-08-25 23:45:44')

    session.Session.insert1(session_key)

    Equipment.insert1('UCLA Miniscope')


    return



@pytest.fixture
def testdata_paths():
    return {

        'miniscope_daqv4': 'subject1/20200609_171646',
        'caiman': 'subject1/20200609_171646'

    }


@pytest.fixture
def caiman_paramset(pipeline):
    miniscope = pipeline['miniscope']

    params_caiman = {'fnames': None,
                        'dims': None,
                        'fr': 30,
                        'decay_time': 0.4,
                        'dxy': (1, 1),
                        'var_name_hdf5': 'mov',
                        'caiman_version': '1.8.5',
                        'last_commit': 'GITW-a99c03c9cb221e802ec71aacfb988257810c8c4a',
                        'mmap_F': None,
                        'mmap_C': None,
                        'block_size_spat': 5000,
                        'dist': 3,
                        'expandCore': np.array([[0, 0, 1, 0, 0],
                                                [0, 1, 1, 1, 0],
                                                [1, 1, 1, 1, 1],
                                                [0, 1, 1, 1, 0],
                                                [0, 0, 1, 0, 0]], dtype = 'int32'),
                        'extract_cc': True,
                        'maxthr': 0.1,
                        'medw': None,
                        'method_exp': 'dilate',
                        'method_ls': 'lasso_lars',
                        'n_pixels_per_process': None,
                        'nb': 1,
                        'normalize_yyt_one': True,
                        'nrgthr': 0.9999,
                        'num_blocks_per_run_spat': 20,
                        'se': np.array([[1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1]], dtype = 'uint8'),
                        'ss': np.array([[1, 1, 1],
                                        [1, 1, 1],
                                        [1, 1, 1]], dtype = 'uint8'),
                        'thr_method': 'nrg',
                        'update_background_components': True,
                        'ITER': 2,
                        'bas_nonneg': False,
                        'block_size_temp': 5000,
                        'fudge_factor': 0.96,
                        'lags': 5,
                        'optimize_g': False,
                        'memory_efficient': False,
                        'method_deconvolution': 'oasis',
                        'noise_method': 'mean',
                        'noise_range': [0.25, 0.5],
                        'num_blocks_per_run_temp': 20,
                        'p': 2,
                        's_min': None,
                        'solvers': ['ECOS', 'SCS'],
                        'verbosity': False,
                        'K': 30,
                        'SC_kernel': 'heat',
                        'SC_sigma': 1,
                        'SC_thr': 0,
                        'SC_normalize': True,
                        'SC_use_NN': False,
                        'SC_nnn': 20,
                        'alpha_snmf': 100,
                        'center_psf': False,
                        'gSig': [5, 5],
                        'gSiz': (11, 11),
                        'init_iter': 2,
                        'kernel': None,
                        'lambda_gnmf': 1,
                        'maxIter': 5,
                        'max_iter_snmf': 500,
                        'method_init': 'greedy_roi',
                        'min_corr': 0.85,
                        'min_pnr': 20,
                        'nIter': 5,
                        'normalize_init': True,
                        'options_local_NMF': None,
                        'perc_baseline_snmf': 20,
                        'ring_size_factor': 1.5,
                        'rolling_length': 100,
                        'rolling_sum': True,
                        'seed_method': 'auto',
                        'sigma_smooth_snmf': (0.5, 0.5, 0.5),
                        'ssub': 2,
                        'ssub_B': 2,
                        'tsub': 2,
                        'check_nan': True,
                        'compute_g': False,
                        'include_noise': False,
                        'max_num_samples_fft': 3072,
                        'pixels': None,
                        'sn': None,
                        'border_pix': 0,
                        'del_duplicates': False,
                        'in_memory': True,
                        'low_rank_background': True,
                        'memory_fact': 1,
                        'n_processes': 1,
                        'nb_patch': 1,
                        'only_init': True,
                        'p_patch': 0,
                        'remove_very_bad_comps': False,
                        'rf': None,
                        'skip_refinement': False,
                        'p_ssub': 2,
                        'stride': None,
                        'p_tsub': 2,
                        'N_samples_exceptionality': 12,
                        'batch_update_suff_stat': False,
                        'dist_shape_update': False,
                        'ds_factor': 1,
                        'epochs': 1,
                        'expected_comps': 500,
                        'full_XXt': False,
                        'init_batch': 200,
                        'init_method': 'bare',
                        'iters_shape': 5,
                        'max_comp_update_shape': np.inf,
                        'max_num_added': 5,
                        'max_shifts_online': 10,
                        'min_SNR': 2.5,
                        'min_num_trial': 5,
                        'minibatch_shape': 100,
                        'minibatch_suff_stat': 5,
                        'motion_correct': True,
                        'movie_name_online': 'online_movie.mp4',
                        'normalize': False,
                        'n_refit': 0,
                        'num_times_comp_updated': np.inf,
                        'opencv_codec': 'H264',
                        'path_to_model': None,
                        'ring_CNN': False,
                        'rval_thr': 0.8,
                        'save_online_movie': False,
                        'show_movie': False,
                        'simultaneously': False,
                        'sniper_mode': False,
                        'stop_detection': False,
                        'test_both': False,
                        'thresh_CNN_noisy': 0.5,
                        'thresh_fitness_delta': -50,
                        'thresh_fitness_raw': -60.97977932734429,
                        'thresh_overlap': 0.5,
                        'update_freq': 200,
                        'update_num_comps': True,
                        'use_corr_img': False,
                        'use_dense': True,
                        'use_peak_max': True,
                        'W_update_factor': 1,
                        'SNR_lowest': 0.5,
                        'cnn_lowest': 0.1,
                        'gSig_range': None,
                        'min_cnn_thr': 0.9,
                        'rval_lowest': -1,
                        'use_cnn': True,
                        'use_ecc': False,
                        'max_ecc': 3,
                        'do_merge': True,
                        'merge_thr': 0.8,
                        'merge_parallel': False,
                        'max_merge_area': None,
                        'border_nan': 'copy',
                        'gSig_filt': None,
                        'is3D': False,
                        'max_deviation_rigid': 3,
                        'max_shifts': (6, 6),
                        'min_mov': None,
                        'niter_rig': 1,
                        'nonneg_movie': True,
                        'num_frames_split': 80,
                        'num_splits_to_process_els': None,
                        'num_splits_to_process_rig': None,
                        'overlaps': (32, 32),
                        'pw_rigid': False,
                        'shifts_opencv': True,
                        'splits_els': 14,
                        'splits_rig': 14,
                        'strides': (96, 96),
                        'upsample_factor_grid': 4,
                        'use_cuda': False,
                        'n_channels': 2,
                        'use_bias': False,
                        'use_add': False,
                        'pct': 0.01,
                        'patience': 3,
                        'max_epochs': 100,
                        'width': 5,
                        'loss_fn': 'pct',
                        'lr': 0.001,
                        'lr_scheduler': None,
                        'remove_activity': False,
                        'reuse_model': False}

    # miniscope.ProcessingParamSet.insert_new_params(
    #     'caiman', 1, 'Calcium imaging analysis with'
    #                  ' CaImAn using default CaImAn parameters for 2d planar images',
    #     params_caiman)

    # yield params_caiman

    # (miniscope.ProcessingParamSet & 'paramset_idx = 1').delete()


# @pytest.fixture
# # def caiman3D_paramset(pipeline):
#     miniscope = pipeline['miniscope']

#     params_caiman_3d = {'fnames': None,
#                         'dims': None,
#                         'fr': 30,
#                         'decay_time': 0.4,
#                         'dxy': (1, 1),
#                         'var_name_hdf5': 'mov',
#                         'caiman_version': '1.8.5',
#                         'last_commit': 'GITW-a99c03c9cb221e802ec71aacfb988257810c8c4a',
#                         'mmap_F': None,
#                         'mmap_C': None,
#                         'block_size_spat': 5000,
#                         'dist': 3,
#                         'expandCore': np.array([[0, 0, 1, 0, 0],
#                                                 [0, 1, 1, 1, 0],
#                                                 [1, 1, 1, 1, 1],
#                                                 [0, 1, 1, 1, 0],
#                                                 [0, 0, 1, 0, 0]], dtype = 'int32'),
#                         'extract_cc': True,
#                         'maxthr': 0.1,
#                         'medw': None,
#                         'method_exp': 'dilate',
#                         'method_ls': 'lasso_lars',
#                         'n_pixels_per_process': None,
#                         'nb': 1,
#                         'normalize_yyt_one': True,
#                         'nrgthr': 0.9999,
#                         'num_blocks_per_run_spat': 20,
#                         'se': np.array([[1, 1, 1],
#                                         [1, 1, 1],
#                                         [1, 1, 1]], dtype = 'uint8'),
#                         'ss': np.array([[1, 1, 1],
#                                         [1, 1, 1],
#                                         [1, 1, 1]], dtype = 'uint8'),
#                         'thr_method': 'nrg',
#                         'update_background_components': True,
#                         'ITER': 2,
#                         'bas_nonneg': False,
#                         'block_size_temp': 5000,
#                         'fudge_factor': 0.96,
#                         'lags': 5,
#                         'optimize_g': False,
#                         'memory_efficient': False,
#                         'method_deconvolution': 'oasis',
#                         'noise_method': 'mean',
#                         'noise_range': [0.25, 0.5],
#                         'num_blocks_per_run_temp': 20,
#                         'p': 2,
#                         's_min': None,
#                         'solvers': ['ECOS', 'SCS'],
#                         'verbosity': False,
#                         'K': 30,
#                         'SC_kernel': 'heat',
#                         'SC_sigma': 1,
#                         'SC_thr': 0,
#                         'SC_normalize': True,
#                         'SC_use_NN': False,
#                         'SC_nnn': 20,
#                         'alpha_snmf': 100,
#                         'center_psf': False,
#                         'gSig': (5, 5, 1),
#                         'gSiz': (11, 11),
#                         'init_iter': 2,
#                         'kernel': None,
#                         'lambda_gnmf': 1,
#                         'maxIter': 5,
#                         'max_iter_snmf': 500,
#                         'method_init': 'greedy_roi',
#                         'min_corr': 0.85,
#                         'min_pnr': 20,
#                         'nIter': 5,
#                         'normalize_init': True,
#                         'options_local_NMF': None,
#                         'perc_baseline_snmf': 20,
#                         'ring_size_factor': 1.5,
#                         'rolling_length': 100,
#                         'rolling_sum': True,
#                         'seed_method': 'auto',
#                         'sigma_smooth_snmf': (0.5, 0.5, 0.5),
#                         'ssub': 2,
#                         'ssub_B': 2,
#                         'tsub': 2,
#                         'check_nan': True,
#                         'compute_g': False,
#                         'include_noise': False,
#                         'max_num_samples_fft': 3072,
#                         'pixels': None,
#                         'sn': None,
#                         'border_pix': 0,
#                         'del_duplicates': False,
#                         'in_memory': True,
#                         'low_rank_background': True,
#                         'memory_fact': 1,
#                         'n_processes': 1,
#                         'nb_patch': 1,
#                         'only_init': True,
#                         'p_patch': 0,
#                         'remove_very_bad_comps': False,
#                         'rf': None,
#                         'skip_refinement': False,
#                         'p_ssub': 2,
#                         'stride': None,
#                         'p_tsub': 2,
#                         'N_samples_exceptionality': 12,
#                         'batch_update_suff_stat': False,
#                         'dist_shape_update': False,
#                         'ds_factor': 1,
#                         'epochs': 1,
#                         'expected_comps': 500,
#                         'full_XXt': False,
#                         'init_batch': 200,
#                         'init_method': 'bare',
#                         'iters_shape': 5,
#                         'max_comp_update_shape': np.inf,
#                         'max_num_added': 5,
#                         'max_shifts_online': 10,
#                         'min_SNR': 2.5,
#                         'min_num_trial': 5,
#                         'minibatch_shape': 100,
#                         'minibatch_suff_stat': 5,
#                         'motion_correct': True,
#                         'movie_name_online': 'online_movie.mp4',
#                         'normalize': False,
#                         'n_refit': 0,
#                         'num_times_comp_updated': np.inf,
#                         'opencv_codec': 'H264',
#                         'path_to_model': None,
#                         'ring_CNN': False,
#                         'rval_thr': 0.8,
#                         'save_online_movie': False,
#                         'show_movie': False,
#                         'simultaneously': False,
#                         'sniper_mode': False,
#                         'stop_detection': False,
#                         'test_both': False,
#                         'thresh_CNN_noisy': 0.5,
#                         'thresh_fitness_delta': -50,
#                         'thresh_fitness_raw': -60.97977932734429,
#                         'thresh_overlap': 0.5,
#                         'update_freq': 200,
#                         'update_num_comps': True,
#                         'use_corr_img': False,
#                         'use_dense': True,
#                         'use_peak_max': True,
#                         'W_update_factor': 1,
#                         'SNR_lowest': 0.5,
#                         'cnn_lowest': 0.1,
#                         'gSig_range': None,
#                         'min_cnn_thr': 0.9,
#                         'rval_lowest': -1,
#                         'use_cnn': False,
#                         'use_ecc': False,
#                         'max_ecc': 3,
#                         'do_merge': True,
#                         'merge_thr': 0.8,
#                         'merge_parallel': False,
#                         'max_merge_area': None,
#                         'border_nan': 'copy',
#                         'gSig_filt': None,
#                         'is3D': False,
#                         'max_deviation_rigid': 3,
#                         'max_shifts': (6, 6, 1),
#                         'min_mov': None,
#                         'niter_rig': 1,
#                         'nonneg_movie': True,
#                         'num_frames_split': 80,
#                         'num_splits_to_process_els': None,
#                         'num_splits_to_process_rig': None,
#                         'overlaps': (32, 32, 1),
#                         'pw_rigid': False,
#                         'shifts_opencv': True,
#                         'splits_els': 14,
#                         'splits_rig': 14,
#                         'strides': (96, 96, 1),
#                         'upsample_factor_grid': 4,
#                         'use_cuda': False,
#                         'n_channels': 2,
#                         'use_bias': False,
#                         'use_add': False,
#                         'pct': 0.01,
#                         'patience': 3,
#                         'max_epochs': 100,
#                         'width': 5,
#                         'loss_fn': 'pct',
#                         'lr': 0.001,
#                         'lr_scheduler': None,
#                         'remove_activity': False,
#                         'reuse_model': False}

#     miniscope.ProcessingParamSet.insert_new_params(
#         'caiman', 2, 'Calcium imaging analysis with'
#                      ' CaImAn using default CaImAn parameters for 3d volumetric images',
#         params_caiman_3d)

#     yield params_caiman_3d

#     (miniscope.ProcessingParamSet & 'paramset_idx = 2').delete()


# @pytest.fixture
# def scan_info(pipeline, ingest_sessions):
#     scan = pipeline['scan']

#     scan.ScanInfo.populate()

#     yield

#     scan.ScanInfo.delete()


# @pytest.fixture
# def processing_tasks(pipeline, caiman_paramset, caiman3D_paramset, scan_info):
#     miniscope = pipeline['miniscope']
#     scan = pipeline['scan']
#     get_miniscope_root_data_dir = pipeline['get_miniscope_root_data_dir']

#     root_dir = pathlib.Path(get_miniscope_root_data_dir())
#     for scan_key in (scan.Scan & scan.ScanInfo - miniscope.ProcessingTask).fetch('KEY'):
#         scan_file = root_dir / (scan.ScanInfo.ScanFile & scan_key).fetch('file_path')[0]
#         recording_dir = scan_file.parent

#         # caiman
#         caiman_dir = recording_dir / 'caiman'
#         if caiman_dir.exists():
#             is_3D = (scan.ScanInfo & scan_key).fetch1('ndepths') > 1
#             miniscope.ProcessingTask.insert1({**scan_key,
#                                             'paramset_idx': 1 if not is_3D else 2,
#                                             'processing_output_dir': caiman_dir.as_posix()})

#     yield

#     miniscope.ProcessingTask.delete()


@pytest.fixture
def recording(pipeline, ingest_sessions):
    miniscope = pipeline['miniscope']
    session = pipeline['session']
    session_key = dict(subject='LO012', 
                   session_datetime='2021-08-25 23:45:44')

    lab = pipeline['lab']
    
    lab.Equipment.insert1('UCLA Miniscope') 

    recording_key = dict(session_key,
                     recording_id=0)

    miniscope.Recording.insert1(dict(**recording_key,
                                 scanner='UCLA Miniscope', 
                                 acquisition_software='Miniscope-DAQ-V4',
                                 recording_directory='LO012/20210825_234544/miniscope',
                                 recording_notes=''))

    miniscope.RecordingInfo.populate()

    yield

    miniscope.RecordingInfo.delete()


@pytest.fixture
def curations(recording, pipeline):
    miniscope = pipeline['miniscope']

# for key in (miniscope.ProcessingTask - miniscope.Curation).fetch('KEY'):
#         miniscope.Curation().create1_from_processing_task(key)

#     yield

#     miniscope.Curation.delete()
