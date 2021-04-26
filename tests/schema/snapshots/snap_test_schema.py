# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema 1'] = {
    'data': {
        '__schema': {
            'types': [
                {
                    'description': 'A GraphQL Schema defines the capabilities of a GraphQL server. It exposes all available types and directives on the server, as well as the entry points for query, mutation, and subscription operations.',
                    'fields': [
                        {
                            'description': None,
                            'name': 'description',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': 'A list of all types supported by this server.',
                            'name': 'types',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': 'The type that query operations will be rooted at.',
                            'name': 'queryType',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': 'If this server supports mutation, the type that mutation operations will be rooted at.',
                            'name': 'mutationType',
                            'type': {
                                'name': '__Type'
                            }
                        },
                        {
                            'description': 'If this server support subscription, the type that subscription operations will be rooted at.',
                            'name': 'subscriptionType',
                            'type': {
                                'name': '__Type'
                            }
                        },
                        {
                            'description': 'A list of all directives supported by this server.',
                            'name': 'directives',
                            'type': {
                                'name': None
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': '__Schema'
                },
                {
                    'description': 'The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.',
                    'fields': None,
                    'inputFields': None,
                    'name': 'String'
                },
                {
                    'description': '''The fundamental unit of any GraphQL Schema is the type. There are many kinds of types in GraphQL as represented by the `__TypeKind` enum.

Depending on the kind of a type, certain fields describe information about that type. Scalar types provide no information beyond a name, description and optional `specifiedByUrl`, while Enum types provide their values. Object and Interface types provide the fields they describe. Abstract types, Union and Interface, provide the Object types possible at runtime. List and NonNull types compose other types.''',
                    'fields': [
                        {
                            'description': None,
                            'name': 'kind',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'name',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'description',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'specifiedByUrl',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'fields',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'interfaces',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'possibleTypes',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'enumValues',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'inputFields',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'ofType',
                            'type': {
                                'name': '__Type'
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': '__Type'
                },
                {
                    'description': 'An enum describing what kind of type a given `__Type` is.',
                    'fields': None,
                    'inputFields': None,
                    'name': '__TypeKind'
                },
                {
                    'description': 'Object and Interface types are described by a list of Fields, each of which has a name, potentially a list of arguments, and a return type.',
                    'fields': [
                        {
                            'description': None,
                            'name': 'name',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'description',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'args',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'type',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'isDeprecated',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'deprecationReason',
                            'type': {
                                'name': 'String'
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': '__Field'
                },
                {
                    'description': 'Arguments provided to Fields or Directives and the input fields of an InputObject are represented as Input Values which describe their type and optionally a default value.',
                    'fields': [
                        {
                            'description': None,
                            'name': 'name',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'description',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'type',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': 'A GraphQL-formatted string representing the default value for this input value.',
                            'name': 'defaultValue',
                            'type': {
                                'name': 'String'
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': '__InputValue'
                },
                {
                    'description': 'The `Boolean` scalar type represents `true` or `false`.',
                    'fields': None,
                    'inputFields': None,
                    'name': 'Boolean'
                },
                {
                    'description': 'One possible value for a given Enum. Enum values are unique values, not a placeholder for a string or numeric value. However an Enum value is returned in a JSON response as a string.',
                    'fields': [
                        {
                            'description': None,
                            'name': 'name',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'description',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'isDeprecated',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'deprecationReason',
                            'type': {
                                'name': 'String'
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': '__EnumValue'
                },
                {
                    'description': '''A Directive provides a way to describe alternate runtime execution and type validation behavior in a GraphQL document.

In some cases, you need to provide options to alter GraphQL's execution behavior in ways field arguments will not suffice, such as conditionally including or skipping a field. Directives provide this by describing additional information to the executor.''',
                    'fields': [
                        {
                            'description': None,
                            'name': 'name',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'description',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'isRepeatable',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'locations',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'args',
                            'type': {
                                'name': None
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': '__Directive'
                },
                {
                    'description': 'A Directive can be adjacent to many parts of the GraphQL language, a __DirectiveLocation describes one such possible adjacencies.',
                    'fields': None,
                    'inputFields': None,
                    'name': '__DirectiveLocation'
                },
                {
                    'description': None,
                    'fields': [
                        {
                            'description': None,
                            'name': 'hello',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'globalState',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'state',
                            'type': {
                                'name': None
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': 'Query'
                },
                {
                    'description': None,
                    'fields': [
                        {
                            'description': None,
                            'name': 'counter',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'globalState',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'state',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'stdout',
                            'type': {
                                'name': 'String'
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': 'Subscription'
                },
                {
                    'description': 'The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.',
                    'fields': None,
                    'inputFields': None,
                    'name': 'Int'
                },
                {
                    'description': None,
                    'fields': [
                        {
                            'description': None,
                            'name': 'exec',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'reset',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'sendPdbCommand',
                            'type': {
                                'name': None
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': 'Mutation'
                },
                {
                    'description': None,
                    'fields': [
                        {
                            'description': None,
                            'name': 'taskId',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'prompting',
                            'type': {
                                'name': 'Int'
                            }
                        },
                        {
                            'description': None,
                            'name': 'fileName',
                            'type': {
                                'name': 'String'
                            }
                        },
                        {
                            'description': None,
                            'name': 'lineNo',
                            'type': {
                                'name': 'Int'
                            }
                        },
                        {
                            'description': None,
                            'name': 'fileLines',
                            'type': {
                                'name': None
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': 'Task'
                },
                {
                    'description': None,
                    'fields': [
                        {
                            'description': None,
                            'name': 'threadId',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'tasks',
                            'type': {
                                'name': None
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': 'Thread'
                },
                {
                    'description': None,
                    'fields': [
                        {
                            'description': None,
                            'name': 'globalState',
                            'type': {
                                'name': None
                            }
                        },
                        {
                            'description': None,
                            'name': 'nthreads',
                            'type': {
                                'name': 'Int'
                            }
                        },
                        {
                            'description': None,
                            'name': 'threads',
                            'type': {
                                'name': None
                            }
                        }
                    ],
                    'inputFields': None,
                    'name': 'State'
                }
            ]
        }
    }
}
