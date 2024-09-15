.PHONY: install-sonar-setup
install-sonar-setup:
	@[ ! -e /usr/bin/virtualenv ] && python -m pip install --break-system-packages virtualenv || true
	@[ ! -e ~/.virtualenvs ] && mkdir -v ~/.virtualenvs || true
	@if [ ! -e ~/.virtualenvs/sonar-setup ]; then
		python -m virtualenv ~/.virtualenvs/sonar-setup; \
		~/.virtualenvs/sonar-setup/pip install -r sonar-setup/requirements.txt; \
	fi
	@if [ ! -e /usr/local/bin/sonar-setup ];then
		sudo cp -v setup-sonarqube.py /usr/local/bin/sonar-setup; \
		echo "Great! Now, you can run: sonar-setup"; \
	fi

.PHONY: install-wait-sonar
install-sonar-setup:
	@if [ ! -e /usr/local/bin/wait-sonar ]; then
		sudo cp -v wait-sonar.sh /usr/local/bin/wait-sonar; \
		echo "Great! Now, you can run: wait-sonar"; \
	fi

.PHONY: uninstall
uninstall:
	@[ -e ~/.virtualenvs/sonar-setup ] && rm -rfv ~/.virtualenvs/sonar-setup || true
	@[ -e /usr/local/bin/sonar-setup ] && rm -fv /usr/local/bin/sonar-setup || true
	@[ -e /usr/local/bin/wait-sonar ] && rm -fv /usr/local/bin/wait-sonar || true

.PHONY: activate
activate:
	@source .venv/bin/activate
