# sample-app

## Usemode
```
make install
make test

sonar-setup .sonar/sonar-qualitygate.json > sonar.json
wait-sonar
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
