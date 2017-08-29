#!/usr/bin/env python

""" Check pod limts and requests """

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
import time

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
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    ms.add_metric({'pod.without_limits': statistics['pods_without_limits']})
    ms.add_metric({'pod.without_requests': statistics['pods_without_requests']})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def pod_all_containers_have_limits(pod):
    """ pod_all_containers_have_limits """
    for container in pod['spec']['containers']:
        if 'limits' not in container['resources']:
            return False

    return True

def pod_all_containers_have_requests(pod):
    """ pod_all_containers_have_requests """
    for container in pod['spec']['containers']:
        if 'requests' not in container['resources']:
            return False

    return True

def get_pod_displayname(pod):
    """ get_pod_displayname """
    return pod['metadata']['namespace'] + '/' + pod['metadata']['name']

def get_pod_statistics_from_namespace(namespace,
                                      warn_if_pod_missing_limits=False,
                                      warn_if_pod_missing_requests=False, ):
    """ get_pod_statistics_from_namespace """
    logger.info("get_pod_statistics_from_namespace('%s')", get_pod_statistics_from_namespace)

    ocutil.namespace = namespace

    pods = runOCcmd_yaml('get pods')

    results = {
        'pods_without_limits': 0,
        'pods_without_requests': 0,
    }

    for pod in pods['items']:
        podname = get_pod_displayname(pod)
        logger.debug(podname)

        if not pod_all_containers_have_limits(pod):
            results['pods_without_limits'] += 1
            if warn_if_pod_missing_limits:
                logger.critical("pod has no limits: %s", podname)

        if not pod_all_containers_have_requests(pod):
            results['pods_without_requests'] += 1
            if warn_if_pod_missing_requests:
                logger.critical("pod has no requests: %s", podname)

    return results

def main():
    """ main() """
    logger.debug("main()")

    args = parse_args()

    if args.all_namespaces:
        raise Exception("all-namespaces not yet implemented")

    overall_statistics = {
        'pods_without_limits': 0,
        'pods_without_requests': 0,
    }

    for namespace in args.namespace:
        namespace_statistics = get_pod_statistics_from_namespace(namespace,
                                                       warn_if_pod_missing_limits=True,
                                                       warn_if_pod_missing_requests=True,)

        overall_statistics['pods_without_limits'] += namespace_statistics['pods_without_limits']
        overall_statistics['pods_without_requests'] += namespace_statistics['pods_without_requests']

    logger.warning("overall_statistics: %s", overall_statistics)
    send_metrics(overall_statistics)

if __name__ == "__main__":
    main()
