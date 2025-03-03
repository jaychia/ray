#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys
from pprint import pformat


# NOTE(simon): do not add type hint here because it's ran using python2 in CI.
def list_changed_files(commit_range):
    """Returns a list of names of files changed in the given commit range.

    The function works by opening a subprocess and running git. If an error
    occurs while running git, the script will abort.

    Args:
        commit_range: The commit range to diff, consisting of the two
            commit IDs separated by \"..\"

    Returns:
        list: List of changed files within the commit range
    """
    base_branch = os.environ.get("BUILDKITE_PULL_REQUEST_BASE_BRANCH")
    if base_branch:
        pull_command = ["git", "fetch", "origin", base_branch]
        subprocess.check_call(pull_command)

    command = ["git", "diff", "--name-only", commit_range, "--"]
    out = subprocess.check_output(command)
    return [s.strip() for s in out.decode().splitlines() if s is not None]


def is_pull_request():
    return os.environ.get("BUILDKITE_PULL_REQUEST", "false") != "false"


def get_commit_range():
    return "origin/{}...{}".format(
        os.environ["BUILDKITE_PULL_REQUEST_BASE_BRANCH"],
        os.environ["BUILDKITE_COMMIT"],
    )


if __name__ == "__main__":
    assert os.environ.get("BUILDKITE")

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    RAY_CI_ML_AFFECTED = 0
    RAY_CI_TUNE_AFFECTED = 0
    RAY_CI_TRAIN_AFFECTED = 0
    RAY_CI_LLM_AFFECTED = 0
    # Whether only the most important (high-level) RLlib tests should be run.
    # Set to 1 for any changes to Ray Tune or python source files that are
    # NOT related to Serve, Dashboard or Train.
    RAY_CI_RLLIB_AFFECTED = 0
    RAY_CI_RLLIB_GPU_AFFECTED = 0
    # Whether all RLlib tests should be run.
    # Set to 1 only when a source file in `ray/rllib` has been changed.
    RAY_CI_RLLIB_DIRECTLY_AFFECTED = 0
    RAY_CI_SERVE_AFFECTED = 0
    RAY_CI_CORE_CPP_AFFECTED = 0
    RAY_CI_CPP_AFFECTED = 0
    RAY_CI_JAVA_AFFECTED = 0
    RAY_CI_PYTHON_AFFECTED = 0
    RAY_CI_LINUX_WHEELS_AFFECTED = 0
    RAY_CI_MACOS_WHEELS_AFFECTED = 0
    RAY_CI_DASHBOARD_AFFECTED = 0
    RAY_CI_DOCKER_AFFECTED = 0
    RAY_CI_DOC_AFFECTED = 0
    RAY_CI_PYTHON_DEPENDENCIES_AFFECTED = 0
    RAY_CI_TOOLS_AFFECTED = 0
    RAY_CI_DATA_AFFECTED = 0
    RAY_CI_WORKFLOW_AFFECTED = 0
    RAY_CI_RELEASE_TESTS_AFFECTED = 0
    RAY_CI_COMPILED_PYTHON_AFFECTED = 0
    RAY_CI_ACCELERATED_DAG_AFFECTED = 0
    # Whether to run jobs that are affected by any changes
    RAY_CI_LINT_AFFECTED = 1

    if is_pull_request():
        commit_range = get_commit_range()
        files = list_changed_files(commit_range)
        print(pformat(commit_range), file=sys.stderr)
        print(pformat(files), file=sys.stderr)

        skip_prefix_list = [
            "doc/",
            "examples/",
            "dev/",
            "kubernetes/",
            "site/",
        ]

        for changed_file in files:
            if changed_file.startswith("python/ray/air"):
                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_TUNE_AFFECTED = 1
                RAY_CI_DATA_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif (
                changed_file.startswith("python/ray/llm")
                or changed_file == ".buildkite/llm.rayci.yml"
                or changed_file == "ci/docker/llm.build.Dockerfile"
            ):
                RAY_CI_LLM_AFFECTED = 1
            elif (
                changed_file.startswith("python/ray/data")
                or changed_file == ".buildkite/data.rayci.yml"
                or changed_file == "ci/docker/data.build.Dockerfile"
                or changed_file == "ci/docker/data.build.wanda.yaml"
                or changed_file == "ci/docker/datan.build.wanda.yaml"
                or changed_file == "ci/docker/data9.build.wanda.yaml"
                or changed_file == "ci/docker/datal.build.wanda.yaml"
            ):
                RAY_CI_DATA_AFFECTED = 1
                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif changed_file.startswith("python/ray/workflow"):
                RAY_CI_WORKFLOW_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif changed_file.startswith("python/ray/tune"):
                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TUNE_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif changed_file.startswith("python/ray/train"):
                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif (
                changed_file == ".buildkite/ml.rayci.yml"
                or changed_file == ".buildkite/pipeline.test.yml"
                or changed_file == "ci/docker/ml.build.Dockerfile"
                or changed_file == ".buildkite/pipeline.gpu.yml"
                or changed_file == ".buildkite/pipeline.gpu_large.yml"
                or changed_file == "ci/docker/ml.build.wanda.yaml"
                or changed_file == "ci/ray_ci/ml.tests.yml"
                or changed_file == "ci/docker/min.build.Dockerfile"
                or changed_file == "ci/docker/min.build.wanda.yaml"
            ):
                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_TUNE_AFFECTED = 1
            elif (
                re.match("^(python/ray/)?rllib/", changed_file)
                or changed_file == "ray_ci/rllib.tests.yml"
                or changed_file == ".buildkite/rllib.rayci.yml"
            ):
                RAY_CI_RLLIB_AFFECTED = 1
                RAY_CI_RLLIB_GPU_AFFECTED = 1
                RAY_CI_RLLIB_DIRECTLY_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif (
                changed_file.startswith("python/ray/serve")
                or changed_file == ".buildkite/serve.rayci.yml"
                or changed_file == "ci/docker/serve.build.Dockerfile"
            ):
                RAY_CI_SERVE_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
                RAY_CI_JAVA_AFFECTED = 1
            elif changed_file.startswith("python/ray/dashboard"):
                RAY_CI_DASHBOARD_AFFECTED = 1
                # https://github.com/ray-project/ray/pull/15981
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif changed_file.startswith("dashboard"):
                RAY_CI_DASHBOARD_AFFECTED = 1
                # https://github.com/ray-project/ray/pull/15981
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif changed_file.startswith("python/"):
                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TUNE_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_SERVE_AFFECTED = 1
                RAY_CI_WORKFLOW_AFFECTED = 1
                RAY_CI_DATA_AFFECTED = 1
                RAY_CI_PYTHON_AFFECTED = 1
                RAY_CI_DASHBOARD_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
                # Python changes might impact cross language stack in Java.
                # Java also depends on Python CLI to manage processes.
                RAY_CI_JAVA_AFFECTED = 1
                if (
                    changed_file.startswith("python/setup.py")
                    or re.match(r".*requirements.*\.txt", changed_file)
                    or changed_file == "python/requirements_compiled.txt"
                ):
                    RAY_CI_PYTHON_DEPENDENCIES_AFFECTED = 1
                for compiled_extension in (".pxd", ".pyi", ".pyx", ".so"):
                    if changed_file.endswith(compiled_extension):
                        RAY_CI_COMPILED_PYTHON_AFFECTED = 1
                        break

                # Some accelerated DAG tests require GPUs so we only run them
                # if Ray DAGs or experimental.channels were affected.
                if changed_file.startswith("python/ray/dag") or changed_file.startswith(
                    "python/ray/experimental/channel"
                ):
                    RAY_CI_ACCELERATED_DAG_AFFECTED = 1

            elif changed_file == ".buildkite/core.rayci.yml":
                RAY_CI_PYTHON_AFFECTED = 1
                RAY_CI_CORE_CPP_AFFECTED = 1
            elif (
                changed_file == "ci/docker/min.build.Dockerfile"
                or changed_file == "ci/docker/min.build.wanda.yaml"
                or changed_file == ".buildkite/serverless.rayci.yml"
            ):
                RAY_CI_PYTHON_AFFECTED = 1
            elif (
                changed_file.startswith("java/")
                or changed_file == ".buildkite/others.rayci.yml"
            ):
                RAY_CI_JAVA_AFFECTED = 1
            elif (
                changed_file.startswith("cpp/")
                or changed_file == ".buildkite/pipeline.build_cpp.yml"
            ):
                RAY_CI_CPP_AFFECTED = 1
            elif (
                changed_file.startswith("docker/")
                or changed_file == ".buildkite/pipeline.build_release.yml"
            ):
                RAY_CI_DOCKER_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
            elif changed_file == ".readthedocs.yaml":
                RAY_CI_DOC_AFFECTED = 1
            elif changed_file.startswith("doc/"):
                if (
                    changed_file.endswith(".py")
                    or changed_file.endswith(".ipynb")
                    or changed_file.endswith("BUILD")
                    or changed_file.endswith(".rst")
                ):
                    RAY_CI_DOC_AFFECTED = 1
                # Else, this affects only a rst file or so. In that case,
                # we pass, as the flag RAY_CI_DOC_AFFECTED is only
                # used to indicate that tests/examples should be run
                # (documentation will be built always)
            elif (
                changed_file == "ci/docker/doctest.build.Dockerfile"
                or changed_file == "ci/docker/doctest.build.wanda.yaml"
            ):
                # common doctest always run without coverage
                pass
            elif changed_file.startswith("release/") or changed_file.startswith(
                ".buildkite/release"
            ):
                if changed_file.startswith("release/ray_release"):
                    # Release test unit tests are ALWAYS RUN, so pass
                    pass
                elif not changed_file.endswith(".yaml") and not changed_file.endswith(
                    ".md"
                ):
                    # Do not run on config changes
                    RAY_CI_RELEASE_TESTS_AFFECTED = 1
            elif any(changed_file.startswith(prefix) for prefix in skip_prefix_list):
                # nothing is run but linting in these cases
                pass
            elif (
                changed_file.startswith("ci/lint")
                or changed_file == ".buildkite/lint.rayci.yml"
            ):
                # Linter will always be run
                RAY_CI_TOOLS_AFFECTED = 1
            elif (
                changed_file == ".buildkite/macos.rayci.yml"
                or changed_file == ".buildkite/pipeline.macos.yml"
                or changed_file == "ci/ray_ci/macos/macos_ci.sh"
                or changed_file == "ci/ray_ci/macos/macos_ci_build.sh"
            ):
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
            elif (
                changed_file.startswith("ci/pipeline")
                or changed_file.startswith("ci/build")
                or changed_file.startswith("ci/ray_ci")
                or changed_file == ".buildkite/_forge.rayci.yml"
                or changed_file == ".buildkite/_forge.aarch64.rayci.yml"
                or changed_file == "ci/docker/forge.wanda.yaml"
                or changed_file == "ci/docker/forge.aarch64.wanda.yaml"
                or changed_file == ".buildkite/pipeline.build.yml"
                or changed_file == ".buildkite/hooks/post-command"
            ):
                # These scripts are always run as part of the build process
                RAY_CI_TOOLS_AFFECTED = 1
            elif (
                changed_file == ".buildkite/base.rayci.yml"
                or changed_file == ".buildkite/build.rayci.yml"
                or changed_file == ".buildkite/pipeline.arm64.yml"
                or changed_file == "ci/docker/manylinux.Dockerfile"
                or changed_file == "ci/docker/manylinux.wanda.yaml"
                or changed_file == "ci/docker/manylinux.aarch64.wanda.yaml"
                or changed_file == "ci/docker/ray.cpu.base.wanda.yaml"
                or changed_file == "ci/docker/ray.cpu.base.aarch64.wanda.yaml"
                or changed_file == "ci/docker/ray.cuda.base.wanda.yaml"
                or changed_file == "ci/docker/ray.cuda.base.aarch64.wanda.yaml"
                or changed_file == "ci/docker/windows.build.Dockerfile"
                or changed_file == "ci/docker/windows.build.wanda.yaml"
            ):
                RAY_CI_DOCKER_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_TOOLS_AFFECTED = 1
            elif changed_file.startswith("ci/run") or changed_file == "ci/ci.sh":
                RAY_CI_TOOLS_AFFECTED = 1
            elif changed_file.startswith("src/"):
                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TUNE_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_SERVE_AFFECTED = 1
                RAY_CI_CORE_CPP_AFFECTED = 1
                RAY_CI_CPP_AFFECTED = 1
                RAY_CI_JAVA_AFFECTED = 1
                RAY_CI_PYTHON_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
                RAY_CI_DASHBOARD_AFFECTED = 1
                RAY_CI_RELEASE_TESTS_AFFECTED = 1
                RAY_CI_ACCELERATED_DAG_AFFECTED = 1
            elif changed_file.startswith(".github/"):
                pass
            else:
                print(
                    "Unhandled source code change: {changed_file}".format(
                        changed_file=changed_file
                    ),
                    file=sys.stderr,
                )

                RAY_CI_ML_AFFECTED = 1
                RAY_CI_TUNE_AFFECTED = 1
                RAY_CI_TRAIN_AFFECTED = 1
                RAY_CI_DATA_AFFECTED = 1
                RAY_CI_SERVE_AFFECTED = 1
                RAY_CI_CORE_CPP_AFFECTED = 1
                RAY_CI_CPP_AFFECTED = 1
                RAY_CI_JAVA_AFFECTED = 1
                RAY_CI_PYTHON_AFFECTED = 1
                RAY_CI_DOC_AFFECTED = 1
                RAY_CI_LINUX_WHEELS_AFFECTED = 1
                RAY_CI_MACOS_WHEELS_AFFECTED = 1
                RAY_CI_DASHBOARD_AFFECTED = 1
                RAY_CI_TOOLS_AFFECTED = 1
                RAY_CI_RELEASE_TESTS_AFFECTED = 1
                RAY_CI_COMPILED_PYTHON_AFFECTED = 1

    else:
        RAY_CI_ML_AFFECTED = 1
        RAY_CI_TUNE_AFFECTED = 1
        RAY_CI_TRAIN_AFFECTED = 1
        RAY_CI_RLLIB_AFFECTED = 1
        RAY_CI_RLLIB_DIRECTLY_AFFECTED = 1
        RAY_CI_SERVE_AFFECTED = 1
        RAY_CI_CPP_AFFECTED = 1
        RAY_CI_CORE_CPP_AFFECTED = 1
        RAY_CI_JAVA_AFFECTED = 1
        RAY_CI_PYTHON_AFFECTED = 1
        RAY_CI_DOC_AFFECTED = 1
        RAY_CI_LINUX_WHEELS_AFFECTED = 1
        RAY_CI_MACOS_WHEELS_AFFECTED = 1
        RAY_CI_DOCKER_AFFECTED = 1
        RAY_CI_DASHBOARD_AFFECTED = 1
        RAY_CI_TOOLS_AFFECTED = 1
        RAY_CI_WORKFLOW_AFFECTED = 1
        RAY_CI_DATA_AFFECTED = 1
        RAY_CI_RELEASE_TESTS_AFFECTED = 1
        RAY_CI_COMPILED_PYTHON_AFFECTED = 1

    # Log the modified environment variables visible in console.
    output_string = " ".join(
        [
            "RAY_CI_ML_AFFECTED={}".format(RAY_CI_ML_AFFECTED),
            "RAY_CI_TUNE_AFFECTED={}".format(RAY_CI_TUNE_AFFECTED),
            "RAY_CI_TRAIN_AFFECTED={}".format(RAY_CI_TRAIN_AFFECTED),
            "RAY_CI_LLM_AFFECTED={}".format(RAY_CI_LLM_AFFECTED),
            "RAY_CI_RLLIB_AFFECTED={}".format(RAY_CI_RLLIB_AFFECTED),
            "RAY_CI_RLLIB_GPU_AFFECTED={}".format(RAY_CI_RLLIB_GPU_AFFECTED),
            "RAY_CI_RLLIB_DIRECTLY_AFFECTED={}".format(RAY_CI_RLLIB_DIRECTLY_AFFECTED),
            "RAY_CI_SERVE_AFFECTED={}".format(RAY_CI_SERVE_AFFECTED),
            "RAY_CI_DASHBOARD_AFFECTED={}".format(RAY_CI_DASHBOARD_AFFECTED),
            "RAY_CI_DOC_AFFECTED={}".format(RAY_CI_DOC_AFFECTED),
            "RAY_CI_CORE_CPP_AFFECTED={}".format(RAY_CI_CORE_CPP_AFFECTED),
            "RAY_CI_CPP_AFFECTED={}".format(RAY_CI_CPP_AFFECTED),
            "RAY_CI_JAVA_AFFECTED={}".format(RAY_CI_JAVA_AFFECTED),
            "RAY_CI_PYTHON_AFFECTED={}".format(RAY_CI_PYTHON_AFFECTED),
            "RAY_CI_LINUX_WHEELS_AFFECTED={}".format(RAY_CI_LINUX_WHEELS_AFFECTED),
            "RAY_CI_MACOS_WHEELS_AFFECTED={}".format(RAY_CI_MACOS_WHEELS_AFFECTED),
            "RAY_CI_DOCKER_AFFECTED={}".format(RAY_CI_DOCKER_AFFECTED),
            "RAY_CI_PYTHON_DEPENDENCIES_AFFECTED={}".format(
                RAY_CI_PYTHON_DEPENDENCIES_AFFECTED
            ),
            "RAY_CI_TOOLS_AFFECTED={}".format(RAY_CI_TOOLS_AFFECTED),
            "RAY_CI_WORKFLOW_AFFECTED={}".format(RAY_CI_WORKFLOW_AFFECTED),
            "RAY_CI_DATA_AFFECTED={}".format(RAY_CI_DATA_AFFECTED),
            "RAY_CI_RELEASE_TESTS_AFFECTED={}".format(RAY_CI_RELEASE_TESTS_AFFECTED),
            "RAY_CI_COMPILED_PYTHON_AFFECTED={}".format(
                RAY_CI_COMPILED_PYTHON_AFFECTED
            ),
            "RAY_CI_ACCELERATED_DAG_AFFECTED={}".format(
                RAY_CI_ACCELERATED_DAG_AFFECTED
            ),
            "RAY_CI_LINT_AFFECTED={}".format(RAY_CI_LINT_AFFECTED),
        ]
    )

    # Debug purpose
    print(output_string, file=sys.stderr)

    # Used by buildkite log format
    pairs = [item.split("=") for item in output_string.split(" ")]
    affected_vars = [key for key, affected in pairs if affected == "1"]

    def to_tag(s):
        if s.startswith("RAY_CI_"):
            s = s[7:]
        if s.endswith("_AFFECTED"):
            s = s[:-9]
        return s.lower()

    print(" ".join(list(map(to_tag, affected_vars))))
