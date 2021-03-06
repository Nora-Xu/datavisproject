import numpy as np
import pandas as pd
from sklearn.preprocessing import minmax_scale
from numpy import linalg as la
import os
import json
from collections import defaultdict

from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


input_idx = [34,21,41,88,81,12,121,141]

def open_courses():
    course_data = cache.get('course_data')
    if course_data is None:
        fn = os.path.join(os.path.dirname(__file__), 'course_mat.csv')
        cache.set('course_data', np.array(pd.read_csv(fn)))
        course_data = cache.get('course_data')
    return course_data


def open_jobs():
    jobs_data = cache.get('jobs_data')
    if jobs_data is None:
        fn = os.path.join(os.path.dirname(__file__), 'job_mat.csv')
        cache.set('jobs_data', np.array(pd.read_csv(fn)))
        jobs_data = cache.get('jobs_data')
    return jobs_data

def open_concentrations():
    concentration_data = cache.get('concentration_data')
    if concentration_data is None:
        fn = os.path.join(os.path.dirname(__file__), 'courses.csv')
        cache.set('concentration_data', pd.read_csv(fn))
        concentration_data = cache.get('concentration_data')
    return concentration_data


def get_course_idx_by_concentration(idx):

    c_df = open_concentrations()

    res = {level:[] for level in set(c_df.level.tolist())}
    for i in idx:
        res[c_df.iloc[i].level].append(i)
    return res


def cosSim(inA,inB):
    num = np.dot(inA, inB)
    denom = la.norm(inA)*la.norm(inB)
    return num / denom

def get_job_sim(idx):

    c_mat = open_courses()
    j_mat = open_jobs()


    ## normalize the Job matrix
    j_mat = minmax_scale(j_mat, feature_range=(0,1), axis=0)

    ## create a Selection vector
    selected = np.sum(c_mat[idx,], axis= 0).reshape(1, c_mat.shape[1])

    ## concate the Selection vector and the Course matrix
    conbined = np.concatenate((selected, c_mat), axis=0)
    ## normalize the conbined matrix
    conbined = minmax_scale(conbined, feature_range=(0,1), axis=0)
    selected = conbined[0]

    ## Run selected course on every job to find similarities
    sims = [cosSim(selected,j_mat[i]) for i in range(j_mat.shape[0])]
    adjusted_sims = np.argsort(sims)

    return adjusted_sims.tolist()


def get_group_sim(idx):
    dic = get_course_idx_by_concentration(idx)
    for k in dic:
        if dic[k]:
            dic[k] = get_job_sim(dic[k])
        else:
            dic[k] = 0
    return dic

## get sorted job index for all selected courses
sorted_job_idx = get_job_sim(input_idx)

## get sorted job index for all selected concentration
group_sim_idxs = get_group_sim(input_idx)

