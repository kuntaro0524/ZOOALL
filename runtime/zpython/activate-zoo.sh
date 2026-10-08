#!/bin/bash
# Source with a runtime profile: source activate-zoo.sh PROFILE

profile_name=${1:-${ZOO_RUNTIME_PROFILE:-}}
if [[ -z "$profile_name" ]]; then
  echo "Usage: source activate-zoo.sh PROFILE" >&2
  return 2
fi
if [[ ! "$profile_name" =~ ^[A-Za-z0-9_.-]+$ ]]; then
  echo "Invalid runtime profile name: $profile_name" >&2
  return 2
fi

launcher_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
profile_path="$launcher_root/profiles/$profile_name.conf"
if [[ ! -f "$profile_path" ]]; then
  echo "Runtime profile does not exist: $profile_path" >&2
  return 2
fi
source "$profile_path"
: "${ZOO_BASE_PYTHON:?profile must define ZOO_BASE_PYTHON}"
: "${KUNPY_ROOT:?profile must define KUNPY_ROOT}"
: "${ZOO_ROOT:?profile must define ZOO_ROOT}"

export ZOO_RUNTIME_PROFILE="$profile_name"
export KUNPY_ROOT ZOO_ROOT
export PATH="$launcher_root/bin:$PATH"
if [[ -n "${QB_PYTHONPATH:-}" ]]; then
  export QB_PYTHONPATH="$ZOO_ROOT:$ZOO_ROOT/Libs:$KUNPY_ROOT:$KUNPY_ROOT/Libs:$QB_PYTHONPATH"
else
  export QB_PYTHONPATH="$ZOO_ROOT:$ZOO_ROOT/Libs:$KUNPY_ROOT:$KUNPY_ROOT/Libs"
fi
