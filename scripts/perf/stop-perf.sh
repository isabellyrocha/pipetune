#!/bin/bash

ps -aux | grep -i perf | awk {'print $2'} | xargs sudo kill
