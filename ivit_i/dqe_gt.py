# -*- coding: UTF-8 -*-

import logging as log
import os
import re

from .wmic import get_test_product


def remove_invalid_characters(filename):
    # 定義 Windows 不支援的字元
    invalid_chars = r"[\/:*?\"'<>|]"
    # 使用 re.sub 來替換這些字元為空字串
    cleaned_filename = re.sub(invalid_chars, "", filename)
    return cleaned_filename


# GT Helper
class DqeGT:
    def __init__(self) -> None:
        target_disks = get_test_product()
        if len(target_disks) > 1:
            raise RuntimeError("The program only support one testing disk.")
        if len(target_disks) == 0:
            raise RuntimeError("Can not find any disks for testing.")
        self.ans = remove_invalid_characters(target_disks[0])
        log.info(f"Get Ground Truth: {self.ans}")

    def update_by_labels(self, labels: list) -> None:
        for label in labels:
            if label in self.ans:
                self.ans = label
                break
        else:
            self.ans = os.path.join("OTHERS", f"{self.ans}")
        log.warning(f"Updated ground truth: {self.ans}")

    def compare(self, label: str) -> bool:
        return label == self.ans


# GT Helper
class MockDqeGT(DqeGT):
    def __init__(self, disk_name: str = "3TE6") -> None:
        self.ans = remove_invalid_characters(disk_name)
        log.info(f"Get Ground Truth: {self.ans} ( Capture from config.ini )")
