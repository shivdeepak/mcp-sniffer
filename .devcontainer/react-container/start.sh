#!/bin/bash

pushd /app/frontend
npm install
npm run dev -- --host 0.0.0.0
popd
