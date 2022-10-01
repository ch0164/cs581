# Filename: min_heap.py
# Author: Christian Hall
# Date: 09/28/2022
# Description: This file contains functions needed to implement a min-heap
#              data structure.

# Python Imports
from typing import Any, List

# These are the functions needed to implement the FEL.
__all__ = [
    'heappush',
    'heappop',
    'heapify',
    'nsmallest',
]


# ------------------------------------------------------------------------------
# Public Module Functions
# ------------------------------------------------------------------------------
def heappush(heap: List[Any], item: Any) -> None:
    """
    Push an item onto the heap.

    :param heap: The heap object.
    :param item: The item to push onto the heap.
    :return: None.
    """
    heap.append(item)
    sift_up(heap, 0, len(heap) - 1)


def heappop(heap: List[Any]) -> Any:
    """
    Pop an item off of the heap.

    :param heap: The heap object. Assumed to be nonempty.
    :return: The minimum element in the heap after removing it from the heap.
    """
    # Pop the last element of the heap and reorder the heap if still nonempty.
    end_element = heap.pop()
    if heap:
        min_element = heap[0]
        heap[0] = end_element
        sift_down(heap, 0)
        return min_element
    return end_element


def heapify(seq: List[Any]) -> None:
    """
    Create a heap from a list iterable.

    :param seq: A regular list iterable.
    :return: None.
    """
    for index in reversed(range(len(seq) // 2)):
        sift_down(seq, index)


def nsmallest(n: int, heap: List[Any]) -> List[Any]:
    """
    Get the n items of the heap in sorted order.

    :param n: The number of elements to obtain in sorted order.
    :param heap: The heap object.
    :return: The sorted "heap" list.
    """
    return sorted(heap)[:n]


# ------------------------------------------------------------------------------
# Private Module Functions
# ------------------------------------------------------------------------------
def get_child_index(index: int) -> int:
    """
    Get the left child index.

    :param index: The index of the current node.
    :return: The index of the current node's leftmost child node.
    """
    return 2 * index + 1


def get_parent_index(index: int) -> int:
    """
    Get the parent index.

    :param index: The index of the current node.
    :return: The index of the current node's parent.
    """
    return (index - 1) // 2


def sift_up(heap: List[Any], start_index: int, current_index: int) -> None:
    """
    Restore the heap by swapping elements up the heap.

    :param heap: The heap object.
    :param start_index: The index of the node to start swapping.
    :param current_index: The current node index to swap.
    :return: None.
    """
    current_element = heap[current_index]
    parent_index = get_parent_index(current_index)
    parent_element = heap[parent_index]

    # Continue to swap elements in the heap until it is restored.
    while current_index > start_index and current_element < parent_element:
        heap[current_index] = parent_element
        current_index = parent_index
        parent_index = get_parent_index(current_index)
        parent_element = heap[parent_index]

    # Now, place the new element of the heap at its proper location.
    heap[current_index] = current_element


def sift_down(heap: List[Any], start_index: int) -> None:
    """
    Restore the heap by swapping elements down the heap.

    :param heap: The heap object.
    :param start_index: The index of the node to start swapping.
    :return: None.
    """
    end_index = len(heap)
    current_index = start_index
    child_index = get_child_index(current_index)
    new_element = heap[start_index]

    # Continue to swap elements in the heap until it is restored.
    while child_index < end_index:
        # Get the current node's left and right elements.
        right_child_index = child_index + 1
        child_element = heap[child_index]
        right_child_element = heap[right_child_index] \
            if right_child_index < end_index else None

        # Swap the child index with the smaller of the two children.
        if right_child_index < end_index and \
                right_child_element < child_element:
            child_index = right_child_index

        # Swap with the smaller child and go further down the heap.
        heap[current_index] = heap[child_index]
        current_index = child_index
        child_index = get_child_index(current_index)

    # The heap now has a free space at current_index, so add the new element
    # and finish restoring the heap by sifting up.
    heap[current_index] = new_element
    sift_up(heap, start_index, current_index)
