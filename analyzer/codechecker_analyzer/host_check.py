# -------------------------------------------------------------------------
#                     The CodeChecker Infrastructure
#   This file is distributed under the University of Illinois Open Source
#   License. See LICENSE.TXT for details.
# -------------------------------------------------------------------------
"""
Check static analyzer and features on the host machine.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import errno
import subprocess
import tempfile

from codechecker_common.logger import get_logger

LOG = get_logger('analyze')


def check_clang(compiler_bin, env):
    """
    Simple check if clang is available.
    """
    clang_version_cmd = [compiler_bin, '--version']
    LOG.debug_analyzer(' '.join(clang_version_cmd))
    try:
        res = subprocess.call(clang_version_cmd,
                              env=env,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        if not res:
            return True

        LOG.debug_analyzer('Failed to run: "%s"', ' '.join(clang_version_cmd))
        return False

    except OSError as oerr:
        if oerr.errno == errno.ENOENT:
            LOG.error(oerr)
            LOG.error('Failed to run: "%s"', ' '.join(clang_version_cmd))
            return False


def has_analyzer_feature(clang_bin, feature, env=None):
    with tempfile.NamedTemporaryFile() as inputFile:
        inputFile.write("void foo(){}")
        inputFile.flush()
        cmd = [clang_bin, "-x", "c", "--analyze",
               "-Xclang", feature, inputFile.name, "-o", "-"]
        LOG.debug('run: "%s"', ' '.join(cmd))
        try:
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    env=env)
            out, err = proc.communicate()
            LOG.debug("stdout:\n%s", out)
            LOG.debug("stderr:\n%s", err)

            return proc.returncode == 0
        except OSError:
            LOG.error('Failed to run: "%s"', ' '.join(cmd))
            raise


def get_resource_dir(clang_bin, context, env=None):
    """
    Returns the resource_dir of Clang or None if the switch is not supported by
    Clang.
    """
    if context.compiler_resource_dir:
        return context.compiler_resource_dir
    # If not set then ask the binary for the resource dir.
    cmd = [clang_bin, "-print-resource-dir"]
    LOG.debug('run: "%s"', ' '.join(cmd))
    try:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=env,
                                universal_newlines=True)
        out, err = proc.communicate()

        LOG.debug("stdout:\n%s", out)
        LOG.debug("stderr:\n%s", err)

        if proc.returncode == 0:
            return out.rstrip()
        else:
            return None
    except OSError:
        LOG.error('Failed to run: "%s"', ' '.join(cmd))
        raise
