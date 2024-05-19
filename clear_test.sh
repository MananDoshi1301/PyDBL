#!/bin/bash
find tests/autograde/p0a/easy -type f ! -name '*.py' -delete
find tests/autograde/p0a/medium -type f ! -name '*.py' -delete
find tests/autograde/p0a/hard -type f ! -name '*.py' -delete
find tests/mytests/ -type f ! -name '*.py' -delete