# Hardware

## Transmitter

Any 433 MHz OOK (ASK) transmitter module with a DATA input works, e.g. the common FS1000A. Connect

- VCC to 5 V (more range) or 3.3 V
- GND to GND
- DATA to a free GPIO, e.g. GPIO17 (pin 11)
- a 17.3 cm wire as antenna (quarter wavelength at 433.92 MHz)

The 3.3 V level of the GPIO is enough for DATA even when the module runs on 5 V.

## Driver

`gpio-ir-tx` is meant for infrared LEDs. With carrier 0 it does not modulate the pulses, it just
switches the GPIO for the given durations, which is what an OOK transmitter needs. The kernel times
every pulse, so the timing does not depend on the load of the system.

`/boot/firmware/config.txt` (`/boot/config.txt` on older systems):

```
dtoverlay=gpio-ir-tx,gpio_pin=17
```

After a reboot the transmitter is a LIRC device, `/dev/lirc0` or the next free number. Several
`gpio-ir-tx` overlays (e.g. an IR LED as well) are fine, each gets its own device.

If LIRC (`lircd`) is installed, keep it away from the 433 MHz device: rf433 opens the device itself.

## Fixed device name

The number of a LIRC device may change between boots. A udev rule gives it a fixed name, e.g.
`/etc/udev/rules.d/71-rf433.rules` from [examples/udev](../examples/udev/71-rf433.rules):

```
SUBSYSTEM=="lirc", DRIVERS=="gpio-ir-tx", SYMLINK+="lirc-433"
```

With more than one `gpio-ir-tx` device, match the device tree node instead. It is named after the
GPIO in hex (GPIO17 = 11); `udevadm info -a -n /dev/lirc0` shows the name:

```
SUBSYSTEM=="lirc", KERNELS=="gpio-ir-transmitter@11|11.gpio-ir-transmitter", SYMLINK+="lirc-433"
```

Reload with `sudo udevadm control --reload && sudo udevadm trigger --subsystem-match=lirc`, then set
`device = /dev/lirc-433` in the [options](options.md).

## Kernel limits

One write to a LIRC device may hold at most 1024 values and last at most 500 ms
(`LIRCBUF_SIZE` and `IR_MAX_DURATION` in the kernel). rf433 packs as many frames as fit into one
write and waits for the pause of the code between two writes.

While `gpio-ir-tx` sends a write, it blocks the interrupts of its CPU core. rf433 therefore binds
itself to one core (see `cpu_core` in the [options](options.md)), so USB and network keep running on
the others. `grep -E 'xhci|pcie|eth' /proc/interrupts` shows which cores handle them.

## Receiver for `learn`

`rf433 learn` records with an RTL-SDR stick and [rtl_433](https://github.com/merbanan/rtl_433):

```
sudo apt install rtl-433
```

A 433 MHz receiver module on a GPIO is not supported yet. Recordings of a Flipper Zero can be
converted with [f0-converter](https://github.com/d03n3rfr1tz3/f0-converter) instead.
