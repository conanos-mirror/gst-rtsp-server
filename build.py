#!/usr/bin/env python
from conanos.build import Main

if __name__ == "__main__":
    Main('gst-rtsp-server',pure_c=True)