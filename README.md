![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![SonarQube](https://img.shields.io/badge/SonarQube-red?style=for-the-badge&logo=sonarqube&logoColor=ffffff)

![GitHub commit activity](https://img.shields.io/github/commit-activity/w/aleroxac/sonar)


# sonar
Automation to setup sonarqube to be used on dev environments


## Table of Content
* [Fatures](#fatures)
* [Project Structure](#project-structure)
* [Languages Supported](#languages-supported)
* [Getting started](#getting-started)
* [Installation](#installation)
* [Use mode](#use-mode)
* [Uninstallation](#uninstallation)



## Fatures
- [x] User creation
- [x] Project creation
- [x] QualityGate creation



## Project Structure
```
├── requirements-dev.txt
├── requirements.txt
└── src
    ├── setup-sonarqube.py
    └── wait-sonar.sh
```



## Languages Supported
- [x] python
- [ ] golang
- [ ] node



## Getting started
Before the installation make sure that you already have created the files bellow in your project
- [sonar-project.properties](example/sonar-project.properties)
- [sonar-qualitygate.json](example/sonar-qualitygate.json)
- [coverage.ini](example/coverage.ini)



## Installation
``` shell
git clone git@github.com/aleroxac/sonar.git
cd sonar
make install
```



## Use mode
``` shell
cd sonar/example
wait-sonar
sonar-setup > sonar.json

python -m pytest
docker run --rm \
    --network=host \
    -e SONAR_SCANNER_OPTS=" \
        -Dsonar.host.url=http://localhost:9000 \
        -Dsonar.login=$(shell jq -r '.token' sonar.json) \
        -Dsonar.scm.revision=$(shell git --no-pager log --max-count=1 --oneline --format='%H') \
        -Dsonar.sources=/usr/src/src \
        -Dsonar.python.coverage.reportPaths=/usr/src/coverage.xml \
        -Dsonar.tests=/usr/src/tests \
        -Dsonar.python.xunit.reportPath=/usr/src/testsuite.xml \
        -Dproject.settings=sonar-project.properties" \
    -v ${PWD}:/usr/src \
    sonarsource/sonar-scanner-cli
```



## Uninstallation
``` shell
cd sonar
make uninstall
```
