#!/usr/bin/env bash

make install && psql -a -d $DATABASE_URL -f page_analyzer.sql