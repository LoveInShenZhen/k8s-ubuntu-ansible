#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# how to developing a ansible module:
# https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html

# https://docs.ansible.com/ansible/latest/reference_appendices/module_utils.html
from ansible.module_utils.basic import *


def main():
    # define available arguments/parameters a user can pass to the module
    # Argument spec: https://docs.ansible.com/ansible/latest/dev_guide/developing_program_flow_modules.html#argument-spec
    module_args = dict(
        save_to = dict(type = 'str', default = '')
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

    save_to = module.params['save_to']

    cmd = 'kubectl get nodes -o json'
    cmd_result = module.run_command(cmd)

    if cmd_result[0] != 0:
        module.fail_json(msg = cmd_result[2])
        return
    else:
        info = json.loads(cmd_result[1])
        node_names = [node['metadata']['name'] for node in info['items']]
        result['ansible_facts'] = dict(k8s_node_names = node_names)

        if save_to != '':
            with open(save_to, 'w') as f:
                f.write(json.dumps(result['ansible_facts'], indent = '  '))

        module.exit_json(**result)


if __name__ == '__main__':
    main()
