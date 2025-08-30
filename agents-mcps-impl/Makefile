# Makefile for consul-adk-example

.PHONY: build clean setup build-arm64-linux build-universal

build:
	python -m build

build-arm64-linux:
	python -m build --wheel --config-setting="--plat-name=linux_aarch64"

build-universal:
	python -m build --wheel --config-setting="--global-option=--universal"

clean:
	rm -rf build/ dist/ *.egg-info

setup:
	pip install --upgrade build
