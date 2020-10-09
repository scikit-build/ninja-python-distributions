#!/bin/bash

set -e
set -x

MANYLINUX_PYTHON=cp38-cp38
export PATH="/opt/python/${MANYLINUX_PYTHON}/bin:$PATH"

cd /io

ci_before_install() {
    /opt/python/${MANYLINUX_PYTHON}/bin/pip install scikit-ci scikit-ci-addons scikit-build
}

ci_install() {
    /opt/python/${MANYLINUX_PYTHON}/bin/ci install
}
ci_script() {
    /opt/python/${MANYLINUX_PYTHON}/bin/ci test
}
ci_after_success() {
    /opt/python/${MANYLINUX_PYTHON}/bin/ci after_test
}


if [[ $1 == 'all' ]]; then
    ci_before_install
    ci_install
    ci_script
    ci_after_success
else
    $1
fi
