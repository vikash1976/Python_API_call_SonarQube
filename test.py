#!/usr/bin/env python3

'''
This module creates a Quality Gate, adds conditions to and Set the Quality Gate as Default.
It needs admin user privilages
You can either use Token or use your username and password
To use Token add token in the user prompt and leave password field empty
'''

import requests
from requests.exceptions import HTTPError
from getpass import getpass


SONARQUBE_QUALITYGATE_API = input("SonarQube URL like http://localhost:9000: ")+"/api/qualitygates"
USER = input('User: ')
PASS = getpass()
QUALITY_GATE_NAME = input("Quality Gate Name: ")

CONDITIONS = {
    0: ["coverage", "LT", "100"],
    1: ["dc5_mutationAnalysis_mutations_coverage", "LT", "100"],
    2: ["sqale_rating", "GT", "1"],
    3: ["reliability_rating", "GT", "1"],
    4: ["code_smells", "GT", "1"],
    5: ["security_rating", "GT", "1"],
    6: ["blocker_violations", "GT", "0"],
    7: ["critical_violations", "GT", "0"],
    8: ["major_violations", "GT", "0"],
    9: ["minor_violations", "GT", "0"],
}

def create_quality_gate(quality_gate_name):
    '''
    This function creates a Quality Gate
    '''
    try:
        res = requests.post(
            '{}/create'.format(SONARQUBE_QUALITYGATE_API),
            params={'name':quality_gate_name},
            auth=(USER, PASS)
            )
        res.raise_for_status()
        print(
            'Quality Gate Creation Successfull\n status: {}\n response:{}'
            .format(res.status_code, res.text)
            )
        return res.json()['id']
    except HTTPError as http_error:
        print(
            'Quality Gate creation failed. It can be due to duplicate quality \
gate name or invalid credentials. It throws the following HTTP Error : {}'
            .format(http_error)
            )
    except Exception as err:
        print("Error in the Code", err)

    return None

def add_conditions(gate_id, metric, operator, error):
    '''
    This function adds condition to our quality gate
    '''
    res = requests.post(
        '{}/create_condition'.format(SONARQUBE_QUALITYGATE_API),
        params=[('gateId', gate_id), ('metric', metric), ('op', operator), ('error', error)],
        auth=(USER, PASS)
        )
    print(res.text)
    return res.status_code

def set_qg_default(gate_id):
    '''
    This function makes our quality gate as default
    '''
    res = requests.post(
        '{}/set_as_default'.format(SONARQUBE_QUALITYGATE_API),
        params={'id':gate_id},
        auth=(USER, PASS)
        )
    print(res.text)  
    return res.status_code

if __name__ == "__main__":
    try:
        gate_id = create_quality_gate(QUALITY_GATE_NAME)
        if gate_id:
            for _, val in CONDITIONS.items():
                result = add_conditions(gate_id, val[0], val[1], val[2])
                if result & 200 != 200:
                    raise ValueError('Quality Gate Condition creation failed {}'.format(val))
            print(
                'Conditions added successfully to Quality Gate'
                )
            result = set_qg_default(gate_id)
            if result & 200 != 200:
                raise ValueError('Error while making the quality gate as default')
            print(
                'Quality Gate with ID {} is set as default'
                .format(gate_id)
                )
    except ValueError as error:
        print(error)
