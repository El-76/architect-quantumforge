.PHONY: install uninstall

INSTALL_DIR := /opt/practicum7/bin
HASH_DIR := /var/lib/practicum7/hashes
LOG_DIR := /var/log/practicum7
RUN_DIR := /var/run/practicum7

install:
	sudo mkdir -p $(INSTALL_DIR)
	sudo chown $$(id -u):$$(id -g) -R /opt/practicum7

	cp upload.sh $(INSTALL_DIR)/
	cp ../Task3/index_or_query.py $(INSTALL_DIR)/

	cd $(INSTALL_DIR) && pyenv local 3.11.16

	sudo mkdir -p $(HASH_DIR)
	sudo chown $$(id -u):$$(id -g) -R /var/lib/practicum7

	sudo mkdir -p $(LOG_DIR)
	sudo chown $$(id -u):$$(id -g) -R /var/log/practicum7

	sudo mkdir -p $(RUN_DIR)
	sudo chown $$(id -u):$$(id -g) -R /var/run/practicum7

uninstall:
	sudo rm -rf /opt/practicum7
	sudo rm -rf /var/lib/practicum7
	sudo rm -rf /var/log/practicum7
	sudo rm -rf /var/run/practicum7
