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

    module = AnsibleModule(
        argument_spec = module_args
    )

    save_to = module.params['save_to']

    cmd = 'kubeadm token create --print-join-command --description=created_by_ansible'
    cmd_result = module.run_command(cmd)
    # stdout like this: kubeadm join k8s.cluster.local:6443 --token phsz1s.4a6hb09le2ymdwjj     --discovery-token-ca-cert-hash sha256:00545ed6985a015f84cd9b878e6dc21f24683501b0379cefd2909647cfe7cfe4

    if cmd_result[0] != 0:
        module.fail_json(msg = cmd_result[2])
        return

    worker_join_cmd = cmd_result[1].strip()

    cmd = 'kubeadm init phase upload-certs --upload-certs'
    cmd_result = module.run_command(cmd)

    if cmd_result[0] != 0:
        module.fail_json(msg = cmd_result[2])
        return

    certificate_key = cmd_result[1].strip().split('\n')[-1]
    master_join_cmd = f'{worker_join_cmd} --control-plane --certificate-key {certificate_key}'

    result['ansible_facts'] = dict(k8s_worker_join_cmd = worker_join_cmd, k8s_master_join_cmd = master_join_cmd)

    if save_to != '':
        with open(save_to, 'w') as f:
            f.write(json.dumps(result['ansible_facts'], indent = '  '))

    module.exit_json(**result)


if __name__ == '__main__':
    main()
