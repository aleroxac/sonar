# sample-app

## Usemode
```
make install
make test
sed -i "s|<source>${PWD}/src<\/source>|<source>/usr/src/src</source>|g" coverage.xml

sonar run
sonar wait
sonar setup sample-app | jq > sonar.json
sonar scan
```
