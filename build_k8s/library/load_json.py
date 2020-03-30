#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# how to developing a ansible module:
# https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html

# https://docs.ansible.com/ansible/latest/reference_appendices/module_utils.html
from ansible.module_utils.basic import *

ANSIBLE_METADATA = {
    'metadata_version': '0.9.0',
    'status': ['preview'],
    'supported_by': 'kklongmono@gmail.com'
}

DOCUMENTATION = '''
---
module: my_test

short_description: This is my test module

version_added: "0.9.0"

description:
    - "This is my longer description explaining my test module"

options:
    name:
        description:
            - This is the message to send to the test module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:
    - azure

author:
    - kklongmono@gmail.com
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_test:
    name: fail me
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: The output message that the test module generates
    type: str
    returned: always
'''


def main():
    # define available arguments/parameters a user can pass to the module
    # Argument spec: https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html#argument-spec
    module_args = dict(
        path = dict(type = 'str', required = True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    # Return Values ref: https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values
    result = dict(
        changed = False,
        ansible_facts = {}
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec = module_args
    )

    path = module.params['path']
    with open(path, 'r') as f:
        result['ansible_facts'] = json.load(f)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
