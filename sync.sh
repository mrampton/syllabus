#!/bin/sh

set -x
set -e

rsync -vp index.html ejones.html coms4111@clic.cs.columbia.edu:html
