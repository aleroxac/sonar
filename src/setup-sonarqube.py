#!/usr/bin/env python
import json
import requests
import sys
from pathlib import Path



## ---------- VARIABLES
sonar_protocol="http"
sonar_host="localhost"
sonar_port=9000

initial_auth = ('admin', 'admin')
dev_auth = ('dev', 'dev')
user_name = dev_auth[0]
user_pass = dev_auth[1]



## ---------- CHECKS
if sys.argv[1] != "" and sys.argv[1] != None:
    project_name = sys.argv[1]
else:
    print("Please inform the project_name.")
    sys.exit(1)



## ---------- FUNCTIONS
## ----- SETUP:USER
def create_user():
    user_creation_data = {
        'login': user_name,
        'name': user_name,
        'password': user_pass,
        'password_confirmation': user_pass,
        'email': f'{user_name}@local.dev',
        'scm_account': user_name,
        'groups': 'sonar-administrators'
    }
    requests.post(
        'http://localhost:9000/api/users/create', 
        auth=initial_auth, 
        data=user_creation_data
    )



## ----- SETUP:PROJECT
def create_project():
    project_creation_data = {
        'name': project_name,
        'project': project_name,
        'visibility': 'public'
    }
    response = requests.post(
        f'{sonar_protocol}://{sonar_host}:{sonar_port}/api/projects/create', 
        auth=dev_auth, 
        data=project_creation_data
    )
    return response.json()['project']['key']


def create_token(project_key):
    token_creation_data = {
        'name': f'{user_name}-token',
        'login': user_name,
        'scopes': 'project:' + project_key
    }
    response = requests.post(
        f'{sonar_protocol}://{sonar_host}:{sonar_port}/api/user_tokens/generate',
        auth=dev_auth,
        data=token_creation_data
    )
    return response.json()['token']


def create_qualitygate_bare_condition():
    post(
        f'{sonar_protocol}://{sonar_host}:{sonar_port}/api/qualitygates/create?name=dev',
        auth=initial_auth,
        timeout=1
    )


def get_qualitygates():
    conditions = get(
        f'{sonar_protocol}://{sonar_host}:{sonar_port}/api/qualitygates/show?name=dev',
        auth=initial_auth,
        timeout=1
    ).json()['conditions']


def remove_initial_qualitygate_conditions():
    for condition in get_qualitygates():
        post(
            f'{sonar_protocol}://{sonar_host}:{sonar_port}/api/qualitygates/delete_condition',
            auth=initial_auth,
            data={
                "id": condition['id'],
            },
            timeout=1
        )


def create_custom_qualitygate_conditions():
    if len(sys.argv) == 1:
        qualitygate_file_path = "sonar-qualitygate.json"
    else:
        if Path(sys.argv[1]).exists():
            qualitygate_file_path = sys.argv[1]
        else:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(1)

    qualitygate_config = open("sonar-qualitygate.json").read()

    newcode_conditions = json.loads(qualitygate_config)["newcode"]
    overall_conditions = json.loads(qualitygate_config)["overall"]

    conditions = newcode_conditions + overall_conditions
    for condition in conditions:
        post(
            'http://localhost:9000/api/qualitygates/create_condition',
            auth=initial_auth,
            data=condition,
            timeout=1
        )



## ---------- HELPERS
def setup_user():
    create_user()


def setup_project():
    project_key = create_project()
    token = create_token(project_key)

    create_qualitygate_bare_condition()
    remove_initial_qualitygate_conditions()
    create_custom_qualitygate_conditions()

    return project_key, token



## ---------- MAIN
if __name__ == "__main__":
    setup_user()
    project_key, token = setup_project()

    print(
        json.dumps(
            {
                'project_url': f'{sonar_protocol}://{sonar_host}:{sonar_port}/dashboard?id={project_key}',
                'token': token,
                'user': user_name,
                'pass': user_pass,
                'qualitygates': get_qualitygates()
            }
        )
    )
