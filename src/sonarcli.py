#!/usr/bin/env python
import json
import sys
from os import getcwd
from time import sleep
from pathlib import Path
from requests import get, post, ConnectionError
from subprocess import run, CalledProcessError, PIPE, Popen



## ---------- VARIABLES
sonar_url = 'http://localhost:9000'

initial_auth = ('admin', 'admin')
dev_auth = ('dev', 'dev')
user_name = dev_auth[0]
user_pass = dev_auth[1]

INITIAL_DELAY=10
MAX_RETRY=12
WAIT_TIME=10



## ---------- FUNCTIONS
## ----- SONAR
def run_sonar():
    try:
        check_container = run(
            ["docker", "ps", "-q", "--filter", "name=sonar"],
            stdout=PIPE,
            stderr=PIPE
        )

        if check_container.stdout:
            run(["docker", "rm", "-f", "sonar"], check=True, stdout=PIPE, stderr=PIPE)

        run(
            ["docker", "run", "-d", "--name", "sonar", "-p", "9000:9000", "sonarqube:community"],
            check=True,
            stdout=PIPE,
            stderr=PIPE
        )
    except CalledProcessError as e:
        print(f"Fail to start or remove sonarqube container: \n{e.stderr.decode().strip()}\n")


def run_sonar_scanner():
    try:
        sonar_token = run(
            ["jq", "-r", ".token", "sonar.json"], 
            check=True, stdout=PIPE
        ).stdout.decode().strip()
        
        git_revision = run(
            ["git", "--no-pager", "log", "--max-count=1", "--oneline", "--format=%H"], 
            check=True, stdout=PIPE
        ).stdout.decode().strip()

        sonar_scanner_opts = f"-Dsonar.host.url=http://localhost:9000 " \
                             f"-Dsonar.token={sonar_token} " \
                             f"-Dsonar.scm.revision={git_revision} " \
                             f"-Dproject.settings=sonar-project.properties"

        process = Popen([
            "docker", "run", "--rm",
            "--network=host",
            "-e", f"SONAR_SCANNER_OPTS={sonar_scanner_opts}",
            "-v", f"{getcwd()}:/usr/src",
            "sonarsource/sonar-scanner-cli"
        ], stdout=PIPE, stderr=PIPE, text=True)

        for line in process.stdout:
            print(line, end='')

        process.wait()

    except CalledProcessError as e:
        print(f"Failed to run sonar scanner: \n{e.stderr.decode().strip()}\n")


def get_sonar_status():
    try:
        status = get(f'{sonar_url}/api/system/health', auth=initial_auth)
        status.raise_for_status()
        return status.json()
    except Exception as error:
        return {"health": "RED"}


def wait_for_sonar():
    retry_count=0
    while retry_count <= MAX_RETRY:
        if "health" in get_sonar_status().keys():
            if get_sonar_status()["health"] != "GREEN":
                if retry_count == 0:
                    print("Waiting: initial delay...")
                    sleep(INITIAL_DELAY)
                elif retry_count < MAX_RETRY:
                    print(f"[RETRY: {retry_count}/{MAX_RETRY}] - Waiting for sonar...")
                    sleep(WAIT_TIME)
                else:
                    print(f"[RETRY: {retry_count}/{MAX_RETRY}] - MAX_RETRY was reached")
                    sys.exit(1)
            else:
                print("Great, sonar is ready!")
                break
        else:
            print("Sonar API is not ready, wait some seconds and try again...")
            sleep(INITIAL_DELAY)
        retry_count += 1



## ----- SETUP:USER
def setup_user():
    user_creation_data = {
        'login': user_name,
        'name': user_name,
        'password': user_pass,
        'password_confirmation': user_pass,
        'email': f'{user_name}@local.dev',
        'scm_account': user_name,
        'groups': 'sonar-administrators'
    }
    post(
        f'{sonar_url}/api/users/create', 
        auth=initial_auth, 
        data=user_creation_data
    )



## ----- SETUP:PROJECT
def create_project(project_name):
    project_creation_data = {
        'name': project_name,
        'project': project_name,
        'visibility': 'public'
    }

    projects = get(
        f'{sonar_url}/api/projects/search', 
        auth=initial_auth
    ).json()["components"]

    if project_name in [ project["key"] for project in projects ]:
        project_key = project_name
    else:
        project_key = post(
            f'{sonar_url}/api/projects/create', 
            auth=dev_auth, 
            data=project_creation_data
        ).json()['project']['key']


def get_tokens():
    return get(
        f'{sonar_url}/api/user_tokens/search',
        auth=dev_auth
    ).json()["userTokens"]


def revoke_token(token_name):
    post(
        f'{sonar_url}/api/user_tokens/revoke',
        auth=dev_auth,
        data={"name": token_name}
    )


def create_token(project_name):
    token_creation_data = {
        'name': f'{user_name}-token',
        'login': user_name,
        'scopes': 'project:' + project_name
    }

    tokens = get_tokens()
    if len(tokens) >= 1:
        if token_creation_data["name"] in [ token["name"] for token in tokens ]:
            revoke_token(token_creation_data["name"])

    return post(
        f'{sonar_url}/api/user_tokens/generate',
        auth=dev_auth,
        data=token_creation_data
    ).json()['token']


def create_qualitygate_bare_condition():
    post(
        f'{sonar_url}/api/qualitygates/create?name=dev',
        auth=initial_auth,
        timeout=1
    )


def get_qualitygates():
    qualitygates = get(
        f'{sonar_url}/api/qualitygates/show?name=dev',
        auth=initial_auth,
        timeout=1
    ).json()

    if "errors" in qualitygates.keys():
        conditions = []
    else:
        conditions = qualitygates["conditions"]

    return conditions


def remove_initial_qualitygate_conditions():
    conditions = get_qualitygates()
    if conditions == None:
        return

    for condition in conditions:
        post(
            f'{sonar_url}/api/qualitygates/delete_condition',
            auth=initial_auth,
            data={
                "id": condition['id'],
            },
            timeout=1
        )


def create_custom_qualitygate_conditions():
    qualitygate_file_path = "sonar-qualitygate.json"
    if not Path("sonar-qualitygate.json").exists():
        print(f"File not found: sonar-qualitygate.json")
        sys.exit(1)

    qualitygate_config = open(qualitygate_file_path).read()
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


def set_qualitygate_on_project(project_name):
    post(
        f'{sonar_url}/api/qualitygates/select',
        auth=initial_auth,
        data={"projectKey": project_name, "gateName": "dev"},
        timeout=1
    )



## ---------- HELPERS
def help():
    print(
    """
    USEMODE:
        sonar [COMMAND]

    COMMANDS
        run                         Run sonarqube via docker
        scan                        Run sonar-scanner via docker
        wait                        Wait for sonarqube to be ready
        setup   [PROJECT_NAME]      Setup sonarqube; create a user, project and quality gate
    """
    )
    sys.exit(0)

def handle_input():
    if len(sys.argv) == 1:
        print("[ERROR] [MISSING_COMMAND] Please inform some command")
        help()
    else:
        if sys.argv[1] == "run":
            run_sonar()
        elif sys.argv[1] == "scan":
            run_sonar_scanner()
        elif sys.argv[1] == "wait":
            wait_for_sonar()
        elif sys.argv[1] == "setup":
            if len(sys.argv) != 3:
                print("[ERROR] [MISSING_OPTION] - Please, provide the project name")
                help()

            project_name=sys.argv[2]
            setup_user()
            setup_project(project_name)
            show_sonar_details(project_name)
        elif sys.argv[1] == "help":
            help()
        else:
            print("[ERROR] [INVALID_COMMAND] - Please, provide a valid command")
            help()
        



def setup_project(project_name):
    create_project(project_name)
    create_qualitygate_bare_condition()
    remove_initial_qualitygate_conditions()
    create_custom_qualitygate_conditions()
    set_qualitygate_on_project(project_name)


def show_sonar_details(project_name):
    print(
        json.dumps(
            {
                'project_url': f'{sonar_url}/dashboard?id={project_name}',
                'token': create_token(project_name),
                'user': user_name,
                'pass': user_pass,
                'qualitygates': get_qualitygates()
            }
        )
    )



## ---------- MAIN
if __name__ == "__main__":
    handle_input()
