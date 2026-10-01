.PHONY: install uninstall check-sudo

INSTALL_DIR := /opt/practicum7/bin
DATA_DIR := /var/lib/practicum7
KB_DIR := $(DATA_DIR)/knowledge_base
HASH_DIR := $(DATA_DIR)/hashes
LOG_DIR := /var/log/practicum7
RUN_DIR := /var/run/practicum7

CRON_ENTRY := * * * * * /opt/practicum7/bin/upload.sh

check-sudo:
	@test -n "$$SUDO_UID" || (echo "Run as: sudo make <target>"; exit 1)
	@test -n "$$SUDO_GID" || (echo "Run as: sudo make <target>"; exit 1)

install: check-sudo
	mkdir -p $(INSTALL_DIR)
	mkdir -p $(HASH_DIR)
	mkdir -p $(KB_DIR)
	mkdir -p $(LOG_DIR)
	mkdir -p $(RUN_DIR)

	cp upload.sh $(INSTALL_DIR)/
	cp ../Task3/index_or_query.py $(INSTALL_DIR)/

	find ../Task2/knowledge_base/ \
		-type f \
		! -name 'Сёку.txt' \
                ! -name poisoned_document.txt \
		-exec cp {} $(KB_DIR)/ \;

	echo 3.11.16 > $(INSTALL_DIR)/.python-version

	chown -R $$SUDO_UID:$$SUDO_GID \
		/opt/practicum7 \
		/var/lib/practicum7 \
		/var/log/practicum7 \
		/var/run/practicum7

	( crontab -u $$(id -nu $$SUDO_UID) -l 2>/dev/null | \
		grep -F -v '/opt/practicum7/bin/upload.sh' ; \
		echo "$(CRON_ENTRY)" ) | \
		crontab -u $$(id -nu $$SUDO_UID) -

uninstall: check-sudo
	( crontab -u $$(id -nu $$SUDO_UID) -l 2>/dev/null | \
		grep -F -v '/opt/practicum7/bin/upload.sh' ) | \
		crontab -u $$(id -nu $$SUDO_UID) -

	rm -rf /opt/practicum7
	rm -rf /var/lib/practicum7
	rm -rf /var/log/practicum7
	rm -rf /var/run/practicum7
