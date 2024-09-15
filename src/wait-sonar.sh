#!/usr/bin/env bash


## ---------- VARIABLES
SONAR_USER="admin"
SONAR_PASS="admin"
INITIAL_PERIOD=10
MAX_RETRY=10
WAIT_TIME=30


## ---------- FUNCTIONS
function run_sonar() {
    docker run -d \
        --name sonar \
        -p 9000:9000 \
        sonarqube:community
}

function get_sonar_status() {
    curl -s localhost:9000/api/system/health -u "${SONAR_USER}:${SONAR_PASS}"
}

function wait_for_sonar() {
    RETRY_COUNT=0
    until get_sonar_status | jq -e '.|select(.health=="GREEN")'; do
        if [[ "${RETRY_COUNT}" -eq 0 ]]; then
            sleep "${INITIAL_PERIOD}"
        elif [[ "${RETRY_COUNT}" -lt "${MAX_RETRY}" ]]; then
            echo "Waiting for sonar..."; sleep "${WAIT_TIME}"
            RETRY_COUNT=$((RETRY_COUNT + 1))
        else
            echo "The MAX_RETRY was reached" && exit 0
            break
        fi
    done
}

function setup_sonar() {
    python setup-sonarqube.py | jq
}

## ---------- MAIN
run_sonar
wait_for_sonar
setup_sonar
