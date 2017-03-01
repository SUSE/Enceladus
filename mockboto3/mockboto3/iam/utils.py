# -*- coding: utf-8 -*-


def get_arn(obj, value):
    return "arn:aws:iam::123456789012:{obj}/{value}".format(
        obj=obj,
        value=value
    )


def get_value_from_arn(arn):
    return arn.split('/')[1]
