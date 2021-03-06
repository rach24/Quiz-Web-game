# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Command for deleting managed instance group."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.instance_groups import flags as instance_groups_flags
from googlecloudsdk.core import properties


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Delete(base.DeleteCommand):
  """Delete per instance configs from managed instance group.

  *{command}* deletes one or more per instance configs from a Google Compute
  Engine managed instance group.
  """

  @staticmethod
  def Args(parser):
    instance_groups_flags.GetInstanceGroupManagerArg(
        region_flag=False).AddArgument(
            parser, operation_type='delete')
    parser.add_argument(
        '--instances',
        metavar='INSTANCE',
        required=True,
        type=arg_parsers.ArgList(min_length=1),
        help='Names of instances to delete instance-configs from.')

  def _GetDeletePerInstanceConfigRequests(
      self, holder, igm_ref, instance_names):
    """Returns a list of delete messages for instance group managers."""

    messages = holder.client.messages
    instance_refs = []
    for instance_name in instance_names:
      ref = holder.resources.Parse(
          instance_name,
          collection='compute.instances',
          params={
              'project': igm_ref.project,
              'zone': igm_ref.zone,
          })
      instance_refs.append(ref)
    req = messages.InstanceGroupManagersDeletePerInstanceConfigsReq(
        instances=[instance_ref.SelfLink() for instance_ref in instance_refs]
    )
    return messages.ComputeInstanceGroupManagersDeletePerInstanceConfigsRequest(
        instanceGroupManager=igm_ref.Name(),
        instanceGroupManagersDeletePerInstanceConfigsReq=req,
        project=igm_ref.project,
        zone=igm_ref.zone,
    )

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    project = properties.VALUES.core.project.Get(required=True)
    igm_ref = (
        instance_groups_flags.GetInstanceGroupManagerArg(
            region_flag=False).
        ResolveAsResource)(
            args, holder.resources, default_scope=compute_scope.ScopeEnum.ZONE,
            scope_lister=flags.GetDefaultScopeLister(holder.client, project))

    request = self._GetDeletePerInstanceConfigRequests(
        holder, igm_ref, args.instances)

    service = holder.client.apitools_client.instanceGroupManagers
    operation = service.DeletePerInstanceConfigs(request)
    operation_ref = holder.resources.Parse(
        operation.selfLink, collection='compute.zoneOperations')
    operation_poller = poller.Poller(service)
    return waiter.WaitFor(
        operation_poller, operation_ref, 'Deleting instance configs.')
