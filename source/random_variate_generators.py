# Filename: grocery_checkout.py
# Author: Christian Hall
# Date: 10/13/2022
# Description: This file contains functions for various
#              random variate generators.

# Python Imports
import numpy as np

# Global Variables
saved_x = None
rng = np.random.default_rng()


def set_seed(seed: int):
    """
    Sets the seed of the random number generator.
    :param seed: Any integer value.
    """
    global rng
    rng = np.random.default_rng(seed)


def normal(mu: float, sigma: float, use_np: bool = False) -> float:
    """
    Generate a random variate from the normal distribution.
    :param mu: The mean of the distribution.
    :param sigma: The standard deviation of the distribution.
    :param use_np: Specifies whether to use the numpy normal RVG.
    :return: A random variate from the normal distribution.
    """
    if use_np:
        x = rng.normal(mu, sigma)
    else:
        global saved_x
        if saved_x is None:
            r1 = rng.uniform(0, 1)
            r2 = rng.uniform(0, 1)
            temp = np.sqrt(-2 * np.log(r1))
            x = temp * np.cos(2 * np.pi * r2)
            saved_x = temp * np.sin(2 * np.pi * r2)
        else:
            x = saved_x
            saved_x = None
        x = x * sigma + mu

    return x


def truncated_normal(mu: float,
                     sigma: float,
                     a=-np.inf,
                     b=np.inf,
                     use_np: bool = False) -> float:
    """
    Generate a random variate from the normal distribution, such that
    it is bounded by a and b.
    :param mu: The mean of the distribution.
    :param sigma: The standard deviation of the distribution.
    :param a: The upper bound.
    :param b: The lower bound.
    :param use_np: Specifies whether to use the numpy normal RVG.
    :return: A random variate from the normal distribution
    (bounded by a <= x <= b).
    """
    x = normal(mu, sigma, use_np)
    while not a <= x <= b:
        x = normal(mu, sigma, use_np)
    return x


def exponential(beta: float, use_np: bool = False) -> float:
    """
    :param beta: The scale of the distribution (i.e., the inverse of the rate,
    1 / lambda).
    :param use_np: Specifies whether to use the numpy normal RVG.
    :return: A random variate from the exponential distribution.
    """
    if use_np:
        x = rng.exponential(beta)
    else:
        r = rng.uniform(0, 1)
        x = -beta * np.log(r)
    return x
