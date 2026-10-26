"""Kernel limits of one write to a LIRC device (drivers/media/rc/lirc_dev.c, include/media/rc-core.h)."""

IR_MAX_DURATION = 500000                # in µs; maximum duration of one write
LIRCBUF_SIZE = 1024                     # maximum number of values of one write
