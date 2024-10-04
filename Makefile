.PHONY: install
install:
	@[ ! -e /usr/bin/virtualenv ] && python -m pip install --break-system-packages virtualenv || true
	@[ ! -e ~/.virtualenvs ] && mkdir -v ~/.virtualenvs || true
	@if [ ! -e ~/.virtualenvs/sonarcli ]; then
		python -m virtualenv ~/.virtualenvs/sonarcli; \
		~/.virtualenvs/sonarcli/pip install -r requirements.txt; \
		~/.virtualenvs/sonarcli/pip install -r requirements-dev.txt; \
	fi
	@if [ ! -e /usr/local/bin/sonarcli ];then
		sudo cp -v sonarcli.py /usr/local/bin/sonar; \
		echo "Great! Now, you can run: sonar"; \
	fi

.PHONY: uninstall
uninstall:
	@[ -e ~/.virtualenvs/sonarcli ] && rm -fv ~/.virtualenvs/sonarcli || true
	@[ -e /usr/local/bin/sonar ] && rm -fv /usr/local/bin/sonar || true

.PHONY: activate
activate:
	@source .venv/bin/activate
