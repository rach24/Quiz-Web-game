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
"""Shared resource flags for Cloud Pub/Sub commands."""
from googlecloudsdk.calliope.concepts import concept_parsers
from googlecloudsdk.calliope.concepts import concepts
from googlecloudsdk.calliope.concepts import deps
from googlecloudsdk.core import properties


def SubscriptionAttributeConfig():
  return concepts.ResourceParameterAttributeConfig(
      name='subscription',
      help_text='Name of the subscription.')


def TopicAttributeConfig():
  return concepts.ResourceParameterAttributeConfig(
      name='topic',
      help_text='Name of the topic.')


def ProjectAttributeConfig():
  return concepts.ResourceParameterAttributeConfig(
      name='project',
      help_text='The Cloud project for the {resource}. If not set, it will '
                'use the project set in properties.',
      fallthroughs=[deps.PropertyFallthrough(properties.VALUES.core.project)])


def GetSubscriptionResourceSpec():
  return concepts.ResourceSpec(
      'pubsub.projects.subscriptions',
      resource_name='subscription',
      subscriptionsId=SubscriptionAttributeConfig(),
      projectsId=ProjectAttributeConfig())


def GetTopicResourceSpec():
  return concepts.ResourceSpec(
      'pubsub.projects.topics',
      resource_name='topic',
      topicsId=TopicAttributeConfig(),
      projectsId=ProjectAttributeConfig())


def CreateSubscriptionResourceArg(verb, plural=False):
  """Create a resource argument for a Cloud Pub/Sub Subscription.

  Args:
    verb: str, the verb to describe the resource, such as 'to update'.
    plural: bool, if True, use a resource argument that returns a list.

  Returns:
    the PresentationSpec for the resource argument.
  """
  if plural:
    help_stem = 'One or more subscriptions'
  else:
    help_stem = 'Name of the subscription'
  return concept_parsers.ResourcePresentationSpec(
      'subscription',
      GetSubscriptionResourceSpec(),
      '{} {}'.format(help_stem, verb),
      required=True,
      plural=plural)


def AddSubscriptionResourceArg(parser, verb, plural=False):
  """Add a resource argument for a Cloud Pub/Sub Subscription.

  Args:
    parser: the parser for the command.
    verb: str, the verb to describe the resource, such as 'to update'.
    plural: bool, if True, use a resource argument that returns a list.
  """
  concept_parsers.ConceptParser(
      [CreateSubscriptionResourceArg(verb, plural=plural)]
  ).AddToParser(parser)


def CreateTopicResourceArg(verb, positional=True, plural=False):
  """Create a resource argument for a Cloud Pub/Sub Topic.

  Args:
    verb: str, the verb to describe the resource, such as 'to update'.
    positional: bool, if True, means that the topic ID is a positional rather
      than a flag. If not positional, this also creates a '--topic-project' flag
      as subscriptions and topics do not need to be in the same project.
    plural: bool, if True, use a resource argument that returns a list.

  Returns:
    the PresentationSpec for the resource argument.
  """
  if positional:
    name = 'topic'
    flag_name_overrides = {}
  else:
    name = '--topic' if not plural else '--topics'
    flag_name_overrides = {'project': '--topic-project'}
  help_stem = 'Name of the topic'
  if plural:
    help_stem = 'One or more topics'
  return concept_parsers.ResourcePresentationSpec(
      name,
      GetTopicResourceSpec(),
      '{} {}'.format(help_stem, verb),
      required=True,
      flag_name_overrides=flag_name_overrides,
      plural=plural)


def AddTopicResourceArg(parser, verb, positional=True, plural=False):
  """Add a resource argument for a Cloud Pub/Sub Topic.

  Args:
    parser: the parser for the command.
    verb: str, the verb to describe the resource, such as 'to update'.
    positional: bool, if True, means that the topic ID is a positional rather
      than a flag. If not positional, this also creates a '--topic-project' flag
      as subscriptions and topics do not need to be in the same project.
    plural: bool, if True, use a resource argument that returns a list.
  """
  concept_parsers.ConceptParser(
      [CreateTopicResourceArg(verb, positional=positional, plural=plural)]
  ).AddToParser(parser)


def AddResourceArgs(parser, resources):
  """Add resource arguments for commands that have topic and subscriptions.

  Args:
    parser: the parser for the command.
    resources: a list of resource args to add.
  """
  concept_parsers.ConceptParser(resources).AddToParser(parser)
