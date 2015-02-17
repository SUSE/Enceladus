# azuremetadata

## Introduction

azuremetadata is a command line utility to collect meta data available in a
Microsoft Azure instance. The metadata is provided by the cloud framework
utility WALinuxAgent as documented here (https://github.com/Azure/WALinuxAgent).
The command line utility gets the requested information and by default
writes the data to standard output in a json format. The data can optionally
be represented as XML snippets or raw text

## Installation

Use the standard make install process:

```bash
  sudo make install
```
