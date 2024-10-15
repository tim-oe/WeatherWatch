#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
dashboard application entry point
"""

from dashboard.App import App

app: App = App()

if __name__ == "__main__":

    app.run()
