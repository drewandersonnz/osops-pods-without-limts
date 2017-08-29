#!/usr/bin/env python

""" Check aws instance health """

##pylint: disable=invalid-name
##pylint: disable=line-too-long
##pylint: disable=wrong-import-position

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

import argparse
#import os
import time
import yaml

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.monitoring.ocutil import OCUtil

ocutil = OCUtil()

def runOCcmd(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    oc_time = time.time()
    oc_result = ocutil.run_user_cmd(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - oc_time))
    return oc_result

def runOCcmd_yaml(cmd, base_cmd='oc'):
    """ log commands through ocutil """
    logger.info(base_cmd + " " + cmd)
    ocy_time = time.time()
    ocy_result = ocutil.run_user_cmd_yaml(cmd, base_cmd=base_cmd, )
    logger.info("oc command took %s seconds", str(time.time() - ocy_time))
    return ocy_result

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    namespace_default = ["openshift"]

    parser = argparse.ArgumentParser(description='Pod Status')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, specify multiple')
    parser.add_argument('-a', '--all-namespaces', action='count', default=0, help='Check all namespaces')
    parser.add_argument('--namespace', action='append', default=namespace_default,
                        help='namespace (be careful of using existing namespaces)')

    args = parser.parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    if not args.namespace == namespace_default:
        args.namespace = args.namespace[1:]

    logger.debug("args: %s", args)
    return args

def send_metrics(statistics):
    """ send data to MetricSender"""
    logger.debug("send_metrics(statistics)")

    ms_time = time.time()
    #ms = MetricSender()
    #logger.info("Send data to MetricSender")
    #
    ##ms.add_metric({'aws.ec2.instance.instance_status': problems['InstanceStatus']})
    ##ms.add_metric({'aws.ec2.instance.system_status': problems['SystemStatus']})
    ##ms.add_metric({'aws.ec2.instance.events': problems['Events']})
    #
    #ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def get_pod_statistics_from_namespace(namespace,
        warn_if_pod_missing_limits = False,
        warn_if_pod_missing_requests = False,
    ):
    logger.debug("get_pod_statistics_from_namespace('%s')", get_pod_statistics_from_namespace)

    ocutil.namespace = namespace

    pods = runOCcmd_yaml('get pods')

    for pod in pods['items']:
        logger.debug(yaml.safe_dump(pod, default_flow_style=False, ))


def main():
    """ main() """
    logger.debug("main()")

    args = parse_args()

    if args.all_namespaces:
        raise Exception("all-namespaces not yet implemented")

    for namespace in args.namespace:
        statistics = get_pod_statistics_from_namespace(namespace)

        logger.warn("Statistics: %s", statistics)
        send_metrics(statistics)

if __name__ == "__main__":
    main()
