#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
My Custom Utility Script for MakeHuman
"""

def load_utility():
    """
    This function will be called when the shell plugin loads
    """
    print("My utility script is loaded!")
    
    # Add your utility functions here
    def my_utility_function():
        print("Running my utility function")
        # Add your code here
        
    # Make your functions available in the shell
    return {
        'my_utility_function': my_utility_function
    }

# This will be called when the script is imported
utility_functions = load_utility() 