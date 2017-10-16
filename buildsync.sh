#!/usr/bin/env bash
npm run build
rsync -avrz --progress annotator/static/ annotate:annotate.wkroberts.com/annotator/annotator/annotator/static/
