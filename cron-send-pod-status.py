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

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.cloud.aws.base import Base

def parse_args():
    """ parse the args from the cli """
    logger.debug("parse_args()")

    parser = argparse.ArgumentParser(description='Pod Status')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='verbosity level, specify multiple')
    return parser.parse_args()

def send_metrics(statistics):
    """ send data to MetricSender"""
    logger.debug("send_metrics(statistics)")

    ms_time = time.time()
    ms = MetricSender()
    logger.info("Send data to MetricSender")

    #ms.add_metric({'aws.ec2.instance.instance_status': problems['InstanceStatus']})
    #ms.add_metric({'aws.ec2.instance.system_status': problems['SystemStatus']})
    #ms.add_metric({'aws.ec2.instance.events': problems['Events']})

    ms.send_metrics()
    logger.info("Data sent to Zagg in %s seconds", str(time.time() - ms_time))

def main():
    """ main() """
    logger.debug("main()")

    args = parse_args()

    if args.verbose > 0:
        logger.setLevel(logging.INFO)
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    statistics = {}

    logger.warn("Statistics: %s", statistics)
    send_metrics(statistics)

if __name__ == "__main__":
    main()
