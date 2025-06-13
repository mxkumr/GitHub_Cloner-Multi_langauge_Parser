#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 这是一个测试文件，包含中文内容
# This is a test file with Chinese content

class 测试类:
    """这是一个测试类的文档字符串"""
    
    def __init__(self):
        self.变量 = "你好，世界"
        self.数字 = 42
    
    def 方法(self):
        """这个方法打印一些中文内容"""
        print(self.变量)
        print("这是一些中文字符串")

def 独立函数():
    """独立函数的文档字符串"""
    全局变量 = "全局变量的值"
    return 全局变量

# 创建实例并测试
测试实例 = 测试类()
测试实例.方法()
结果 = 独立函数()
print(结果)

# 一些常量定义
常量_PI = 3.14159
常量_重力 = 9.81

"""
多行文档字符串
包含一些中文内容
用于测试文档字符串检测
""" 