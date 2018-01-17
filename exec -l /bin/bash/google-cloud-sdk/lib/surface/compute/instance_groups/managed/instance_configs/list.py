# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command for listing instance configs of a managed instance group."""
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.instance_groups import flags as instance_groups_flags
from googlecloudsdk.core import properties


class List(base.ListCommand):
  """List per instance configs of a managed instance group."""

  @staticmethod
  def Args(parser):
    instance_groups_flags.GetInstanceGroupManagerArg(
        region_flag=False).AddArgument(
            parser, operation_type='list instance configs for')
    parser.display_info.AddFormat("""table(
        items.instance,
        items.override.disks.deviceName)
    """)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    project = properties.VALUES.core.project.Get(required=True)
    igm_ref = (
        instance_groups_flags.GetInstanceGroupManagerArg(
            region_flag=False).
        ResolveAsResource)(
            args, holder.resources, default_scope=compute_scope.ScopeEnum.ZONE,
            scope_lister=flags.GetDefaultScopeLister(holder.client, project))

    request = (
        client.messages.
        ComputeInstanceGroupManagersListPerInstanceConfigsRequest)(
            filter=args.filter,
            instanceGroupManager=igm_ref.Name(),
            project=igm_ref.project,
            zone=igm_ref.zone,
        )

    return client.MakeRequests([(
        client.apitools_client.instanceGroupManagers, 'ListPerInstanceConfigs',
        request)])
