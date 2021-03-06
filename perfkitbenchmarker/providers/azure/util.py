# Copyright 2019 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for working with Azure resources."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

from perfkitbenchmarker import context
from perfkitbenchmarker import flags
from perfkitbenchmarker import vm_util
from perfkitbenchmarker.providers import azure
import six

AZURE_PATH = azure.AZURE_PATH
AZURE_SUFFIX = ['--output', 'json']
FLAGS = flags.FLAGS


def GetAzureStorageConnectionString(storage_account_name, resource_group_args):
  """Get connection string."""
  stdout, _ = vm_util.IssueRetryableCommand(
      [AZURE_PATH, 'storage', 'account', 'show-connection-string',
       '--name', storage_account_name] + resource_group_args + AZURE_SUFFIX)
  response = json.loads(stdout)
  return response['connectionString']


def GetAzureStorageConnectionArgs(storage_account_name, resource_group_args):
  """Get connection CLI arguments."""
  return ['--connection-string',
          GetAzureStorageConnectionString(storage_account_name,
                                          resource_group_args)]


def GetAzureStorageAccountKey(storage_account_name, resource_group_args):
  """Get storage account key."""
  stdout, _ = vm_util.IssueRetryableCommand(
      [AZURE_PATH, 'storage', 'account', 'keys', 'list',
       '--account-name', storage_account_name] +
      resource_group_args + AZURE_SUFFIX)

  response = json.loads(stdout)
  # A new storage account comes with two keys, but we only need one.
  assert response[0]['permissions'] == 'Full'
  return response[0]['value']


def FormatTag(key, value):
  """Format an individual tag for use with the --tags param of Azure CLI."""
  return '{0}={1}'.format(key, value)


def FormatTags(tags_dict):
  """Format a dict of tags into arguments for 'tag' parameter.

  Args:
    tags_dict: Tags to be formatted.

  Returns:
    A list of tags formatted as arguments for 'tag' parameter.
  """
  return [FormatTag(k, v) for k, v in six.iteritems(tags_dict)]


def GetResourceTags(timeout_minutes):
  """Gets a dict of tags.

  Args:
    timeout_minutes: int, Timeout used for setting the timeout_utc tag.

  Returns:
    A dict contains formatted tags.
  """
  benchmark_spec = context.GetThreadBenchmarkSpec()
  return benchmark_spec.GetResourceTags(timeout_minutes)


def GetTags(timeout_minutes):
  """Gets a list of tags to be used with the --tags param of Azure CLI.

  Args:
    timeout_minutes: int, Timeout used for setting the timeout_utc tag.

  Returns:
    A string contains formatted tags.
  """
  return FormatTags(GetResourceTags(timeout_minutes))


def GetTagsJson(timeout_minutes):
  """Gets a JSON string of tags to be used with the --set param of Azure CLI.

  Args:
    timeout_minutes: int, Timeout used for setting the timeout_utc tag.

  Returns:
    A string contains json formatted tags.
  """
  return 'tags={}'.format(json.dumps(GetResourceTags(timeout_minutes)))
