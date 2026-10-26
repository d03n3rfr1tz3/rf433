# Commands

```
rf433 [--options FILE] [--device DEVICE] [--codes FOLDER] COMMAND …
```

The global options come before the command. Every command ends with exit code 0 on success and 1 on
an error; errors are printed to stderr as `Error: …`. Progress messages start with ` --> `.

Values on the command line (`--code`) are durations in µs, separated by spaces or commas, pulse
first. Quote them: `--code "300 900 300 9300"`.

## Sending

Sending needs root (or the capability `CAP_SYS_NICE` and write access to the LIRC device): rf433
binds itself to one CPU core and switches to SCHED_FIFO for precise pauses between the writes. If
that fails, it warns and sends anyway.

Only one rf433 sends at a time: the LIRC device is locked, a second call waits.

### `send REMOTE CODE [--repeat N]`

Sends a code of the code files with its repeat (see [code files](code-files.md#repeat)).

```
$ sudo rf433 send Garden Light_on
 --> Sending Garden Light_on: 14.4 ms x 10 = 1 window (10)
 --> Done, pauses between windows at most 0.012 ms late
```

`14.4 ms x 10 = 1 window (10)`: one frame takes 14.4 ms, 10 frames are sent in one write.
The last line shows how precisely the pauses between writes were kept.

### `raw --code VALUES [--repeat N]`

Sends a code given on the command line, by default with `repeat` of the options.

## Code files

### `list [REMOTE] [--json]`

Lists all remotes (or one) with their codes, duration and windows, followed by the problems of the
code files. Exit code 1 if there are problems.

`--json` prints the same for other programs:

```json
{
 "remotes": [
  {
   "name": "Garden",
   "file": "garden.conf",
   "repeat": 10,
   "codes": [
    {"name": "Light_on", "repeat": 10, "values": [300, 900, …], "duration_us": 14400}
   ]
  }
 ],
 "problems": ["garden.conf:12: …"]
}
```

`repeat` is always the effective value, after applying remote and options.

### `check`

Reads all code files and prints one line per remote, every problem and `OK` or the number of
problems. Exit code 1 if there are problems. Run it after every change.

### `info REMOTE CODE [--repeat N]` or `info --code VALUES [--repeat N]`

Shows the number of values, the pause, the duration, how many frames fit into one write and how the
repeat is split, without sending.

## Signals

These commands help to turn a recording into a code. They do not touch the code files.

### `clean --code VALUES [--tolerance T]`

Groups pulses and pauses separately: sorted values belong to one group while each is at most
`1 + T` times the previous one (default `T` = 0.25). Every value is replaced by the most frequent value
of its group. Prints the replacements and the cleaned code.

### `frame --code VALUES [--min-gap US]`

Cuts one frame out of a recording with repeats. Pauses of at least `--min-gap` µs (default 5000)
end a frame. Of the frames with the most frequent length, the middle one is taken; its last pause
becomes the median of the pauses of these frames.

### `learn [--seconds N] [--name NAME] [--min-gap US] [--tolerance T]`

Records with `rtl_433` (see [options](options.md#learn)), cuts out one frame as `frame` does and
cleans it as `clean` does. Press the button of the remote several times during the recording.

```
$ sudo rf433 learn --name Light_on
 --> Recording for 10 seconds, press the button now
 --> 3 packages, 42 frames, 38 of them with 26 values
 --> Recorded: 304 892 …
 --> 24.0 ms x 10 = 1 window (10)

    name Light_on
      300 900 …
```

The last lines can be pasted into a `raw_codes` block. The last pause of a recording package is not
trusted, because `rtl_433` cuts the package there.
