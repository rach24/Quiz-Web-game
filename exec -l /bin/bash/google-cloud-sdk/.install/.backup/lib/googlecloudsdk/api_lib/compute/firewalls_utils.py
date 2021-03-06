# Copyright 2014 Google Inc. All Rights Reserved.
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
"""Common classes and functions for firewall rules."""
import re

import enum
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.core import exceptions

ALLOWED_METAVAR = 'PROTOCOL[:PORT[-PORT]]'
LEGAL_SPECS = re.compile(
    r"""

    (?P<protocol>[a-zA-Z0-9+.-]+) # The protocol group.

    (:(?P<ports>\d+(-\d+)?))?     # The optional ports group.
                                  # May specify a range.

    $                             # End of input marker.
    """,
    re.VERBOSE)


class ArgumentValidationError(exceptions.Error):
  """Raised when a user specifies --rules and --allow parameters together."""

  def __init__(self, error_message):
    super(ArgumentValidationError, self).__init__(error_message)


class ActionType(enum.Enum):
  """Firewall Action type."""
  ALLOW = 1
  DENY = 2


def AddCommonArgs(parser,
                  for_update=False,
                  with_egress_support=False,
                  with_service_account=False,
                  with_disabled=False):
  """Adds common arguments for firewall create or update subcommands."""

  min_length = 0 if for_update else 1
  if not for_update:
    parser.add_argument(
        '--network',
        default='default',
        help="""\
        The network to which this rule is attached. If omitted, the
        rule is attached to the ``default'' network.
        """)

  ruleset_parser = parser
  if with_egress_support:
    ruleset_parser = parser.add_mutually_exclusive_group(
        required=not for_update)
  ruleset_parser.add_argument(
      '--allow',
      metavar=ALLOWED_METAVAR,
      type=arg_parsers.ArgList(min_length=min_length),
      required=(not for_update) and (not with_egress_support),
      help="""\
      A list of protocols and ports whose traffic will be allowed.

      The protocols allowed over this connection. This can be the
      (case-sensitive) string values `tcp`, `udp`, `icmp`, `esp`, `ah`, `sctp`,
      or any IP protocol number. An IP-based protocol must be specified for each
      rule. The rule applies only to specified protocol.

      For port-based protocols - `tcp`, `udp`, and `sctp` - a list of
      destination ports or port ranges to which the rule applies may optionally
      be specified. If no port or port range is specified, the rule applies to
      all destination ports.

      The ICMP protocol is supported, but there is no support for configuring
      ICMP packet filtering by ICMP code.

      For example, to create a rule that allows TCP traffic through port 80 and
      ICMP traffic:

        $ {command} MY-RULE --allow tcp:80,icmp

      To create a rule that allows TCP traffic from port 20000 to 25000:

        $ {command} MY-RULE --allow tcp:20000-25000

      To create a rule that allows all TCP traffic:

        $ {command} MY-RULE --allow tcp

      """ + ("""
      Setting this will override the current values.
      """ if for_update else ''))

  parser.add_argument(
      '--description',
      help='A textual description for the firewall rule.{0}'.format(
          ' Set to an empty string to clear existing.' if for_update else ''))

  source_ranges_help = """\
      A list of IP address blocks that are allowed to make inbound
      connections that match the firewall rule to the instances on
      the network. The IP address blocks must be specified in CIDR
      format:
      link:http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing[].

      If neither --source-ranges nor --source-tags are specified,
      --source-ranges defaults to `0.0.0.0/0`, which means that the rule applies
      to all incoming connections from inside or outside the network.  If both
      --source-ranges and --source-tags are specified, the rule matches if
      either the range of the source matches  --source-ranges or the tag of the
      source matches --source-tags.
      """
  if for_update:
    source_ranges_help += """
      Setting this will override the existing source ranges for the firewall.
      The following will clear the existing source ranges:

        $ {command} MY-RULE --source-ranges
      """
  else:
    source_ranges_help += """
      If neither --source-ranges nor --source-tags is provided, then this
      flag will default to 0.0.0.0/0, allowing all sources. Multiple IP
      address blocks can be specified if they are separated by commas.
      """
  parser.add_argument(
      '--source-ranges',
      default=None if for_update else [],
      metavar='CIDR_RANGE',
      type=arg_parsers.ArgList(min_length=min_length),
      help=source_ranges_help)

  source_tags_help = """\
      A list of instance tags indicating the set of instances on the network to
      which the rule applies if all other fields match.  If neither
      --source-ranges nor --source-tags are specified, --source-ranges
      defaults to `0.0.0.0/0`, which means that the rule applies to all
      incoming connections from inside or outside the network.

      If both --source-ranges and --source-tags are specified, an inbound
      connection is allowed if either the range of the source matches
      --source-ranges or the tag of the source matches --source-tags.

      Tags can be assigned to instances during instance creation.
      """
  if with_service_account:
    source_tags_help += """
      If source tags are specified then neither a source nor target service
      account can also be specified.
      """
  if for_update:
    source_tags_help += """
      Setting this will override the existing source tags for the firewall.
      The following will clear the existing source tags:

        $ {command} MY-RULE --source-tags
      """
  parser.add_argument(
      '--source-tags',
      default=None if for_update else [],
      metavar='TAG',
      type=arg_parsers.ArgList(min_length=min_length),
      help=source_tags_help)

  target_tags_help = """\
      A list of instance tags indicating which instances the rule is applied to.
      If the field is set, the rule applies to only instances with a matching
      tag. If omitted, the rule applies to all instances in the network.

      Tags can be assigned to instances during instance creation.
      """
  if with_service_account:
    target_tags_help = """\
      A list of instance tags indicating the set of instances on the
      network which may accept inbound connections that match the
      firewall rule. If both target tags and target service account
      are omitted, all instances on the network can receive inbound
      connections that match the rule.

      Tags can be assigned to instances during instance creation.

      If target tags are specified then neither a source nor target
      service account can also be specified.
      """
  if for_update:
    target_tags_help += """
      Setting this will override the existing target tags for the firewall.
      The following will clear the existing target tags:

        $ {command} MY-RULE --target-tags
      """
  parser.add_argument(
      '--target-tags',
      default=None if for_update else [],
      metavar='TAG',
      type=arg_parsers.ArgList(min_length=min_length),
      help=target_tags_help)

  disabled_help = """\
      Use this flag to disable a firewall rule and stop it from being enforced
      in the network. Disabled firewall rules are not enforced, and the
      associated network behaves as if the firewall rule did not exist. Use

       $ gcloud alpha compute firewall-rules update MY-RULE --no-disabled

      to enable a disabled rule.
      """
  if not for_update:
    disabled_help += """\
        If omitted firewall rule is considered enabled.
    """
  if with_disabled:
    parser.add_argument(
        '--disabled', action='store_true', default=None, help=disabled_help)

  # Add egress deny firewall cli support.
  if with_egress_support:
    AddArgsForEgress(parser, ruleset_parser, for_update)


def AddArgsForEgress(parser, ruleset_parser, for_update=False):
  """Adds arguments for egress firewall create or update subcommands."""
  min_length = 0 if for_update else 1

  if not for_update:
    ruleset_parser.add_argument(
        '--action',
        choices=['ALLOW', 'DENY'],
        type=lambda x: x.upper(),
        help="""\
        The action for the firewall rule: whether to allow or deny matching
        traffic. If specified, the flag `--rules` must also be specified.
        """)

  rules_help = """\
      A list of protocols and ports to which the firewall rule will apply.

      PROTOCOL is the IP protocol whose traffic will be checked.
      PROTOCOL can be either the name of a well-known protocol
      (e.g., tcp or icmp) or the IP protocol number.
      A list of IP protocols can be found at
      http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml

      A port or port range can be specified after PROTOCOL to which the
      firewall rule apply on traffic through specific ports. If no port
      or port range is specified, connections through all ranges are applied.
      For example, the following will create a rule that blocks TCP
      traffic through port 80 and ICMP traffic:

        $ {command} MY-RULE --action deny --rules tcp:80,icmp

      TCP and UDP rules must include a port or port range.
      """
  if for_update:
    rules_help += """
      Setting this will override the current values.
      """
  else:
    rules_help += """
      If specified, the flag --action must also be specified.
      """
  parser.add_argument(
      '--rules',
      metavar=ALLOWED_METAVAR,
      type=arg_parsers.ArgList(min_length=min_length),
      help=rules_help,
      required=False)

  # Do NOT allow change direction in update case.
  if not for_update:
    parser.add_argument(
        '--direction',
        choices=['INGRESS', 'EGRESS', 'IN', 'OUT'],
        type=lambda x: x.upper(),
        help="""\
        If direction is NOT specified, then default is to apply on incoming
        traffic. For incoming traffic, it is NOT supported to specify
        destination-ranges; For outbound traffic, it is NOT supported to specify
        source-ranges or source-tags.

        For convenience, 'IN' can be used to represent ingress direction and
        'OUT' can be used to represent egress direction.
        """)

  parser.add_argument(
      '--priority', type=int,
      help="""\
      This is an integer between 0 and 65535, both inclusive. When NOT
      specified, the value assumed is 1000. Relative priority determines
      precedence of conflicting rules: lower priority values imply higher
      precedence. DENY rules take precedence over ALLOW rules having equal
      priority.
      """)

  destination_ranges_help = """\
      The firewall rule will apply to traffic that has destination IP address
      in these IP address block list. The IP address blocks must be specified
      in CIDR format:
      link:http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing[].
      """
  if for_update:
    destination_ranges_help += """
      Setting this will override the existing destination ranges for the
      firewall. The following will clear the existing destination ranges:

        $ {command} MY-RULE --destination-ranges
      """
  else:
    destination_ranges_help += """
      If --destination-ranges is NOT provided, then this
      flag will default to 0.0.0.0/0, allowing all destinations. Multiple IP
      address blocks can be specified if they are separated by commas.
      """
  parser.add_argument(
      '--destination-ranges',
      default=None if for_update else [],
      metavar='CIDR_RANGE',
      type=arg_parsers.ArgList(min_length=min_length),
      help=destination_ranges_help)


def AddArgsForServiceAccount(parser, for_update=False):
  """Adds arguments for secure firewall create or update subcommands."""
  min_length = 0 if for_update else 1
  source_service_accounts_help = """\
      The email of a service account indicating the set of instances on the
      network which match a traffic source in the firewall rule.

      If a source service account is specified then neither source tags nor
      target tags can also be specified.
      """
  if for_update:
    source_service_accounts_help += """
      Setting this will override the existing source service accounts for the
      firewall.
      The following will clear the existing source service accounts:

        $ {command} MY-RULE --source-service-accounts
      """
  parser.add_argument(
      '--source-service-accounts',
      default=None if for_update else [],
      metavar='EMAIL',
      type=arg_parsers.ArgList(min_length=min_length),
      help=source_service_accounts_help)

  target_service_accounts_help = """\
      The email of a service account indicating the set of instances to which
      firewall rules apply. If both target tags and target service account are
      omitted,  the firewall rule is applied to all instances on the network.

      If a target service account is specified then neither source tag nor
      target tags can also be specified.
      """
  if for_update:
    target_service_accounts_help += """
      Setting this will override the existing target service accounts for the
      firewall.
      The following will clear the existing target service accounts:

        $ {command} MY-RULE --target-service-accounts
      """
  parser.add_argument(
      '--target-service-accounts',
      default=None if for_update else [],
      metavar='EMAIL',
      type=arg_parsers.ArgList(min_length=min_length),
      help=target_service_accounts_help)


def ParseRules(rules, message_classes, action=ActionType.ALLOW):
  """Parses protocol:port mappings from --allow or --rules command line."""
  rule_value_list = []
  for spec in rules or []:
    match = LEGAL_SPECS.match(spec)
    if not match:
      raise calliope_exceptions.ToolException(
          'Firewall rules must be of the form {0}; received [{1}].'
          .format(ALLOWED_METAVAR, spec))
    if match.group('ports'):
      ports = [match.group('ports')]
    else:
      ports = []

    if action == ActionType.ALLOW:
      rule = message_classes.Firewall.AllowedValueListEntry(
          IPProtocol=match.group('protocol'), ports=ports)
    else:
      rule = message_classes.Firewall.DeniedValueListEntry(
          IPProtocol=match.group('protocol'), ports=ports)
    rule_value_list.append(rule)
  return rule_value_list
