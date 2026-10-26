# Code files

rf433 reads all files ending in `.conf` in the code folder, by default `/etc/rf433/rf433.conf.d`
(see [options](options.md)). The format follows the `raw_codes` part of LIRC's `lircd.conf`.

```
# Comments are whole lines starting with #.
begin remote
  name    Livingroom
  repeat  20

  begin raw_codes
    name Light_on
      270 2700 270 1300 270 270 270 1300
      270 270 270 10400

    name Light_off
      repeat 40
      270 2700 270 1300 270 1300 270 270
      270 270 270 10400
  end raw_codes
end remote
```

## Structure

- A file holds one or more remotes, each between `begin remote` and `end remote`.
- A remote has a `name`, an optional `repeat` and one `begin raw_codes … end raw_codes` block.
- A code starts with `name`, may have a `repeat` directly below it and then its values.
  The values may be spread over several lines. The next `name` or `end raw_codes` ends the code.
- Indentation, empty lines and comment lines have no meaning.
- Names consist of letters, digits, `_` and `-`. Remote names are unique over all files, code names
  within their remote.

## Values

A code is exactly one frame including the pause after it:

- durations in µs, pulse first, then pause, pulse, pause, …
- an even number of values, the last one is the pause after the frame
- no zero values
- one frame without its last pause must fit into one write of the driver: at most 1025 values
  and 500 ms

Values can be separated by spaces or commas; `+` and `-` signs (as in `mode2` output) are ignored.

## Repeat

`repeat` is the total number of frames sent. The repeat of a code wins over the repeat of its remote,
which wins over `repeat` of the [options](options.md) (default 10). `send --repeat` and
`raw --repeat` override all of them. Every repeat must be between 1 and `max_repeat` (default 100).

As many frames as possible are packed into one write. Between two writes rf433 waits for the pause at
the end of the code, so the receiver sees the same stream as from the original remote.
`rf433 info REMOTE CODE` shows how a code is split.

## Problems

`rf433 check` reads all files and lists every problem with file and line, e.g.

```
garden.conf:12: Garden Light_on: code must end with a pause (even number of values, got 25)
```

A code with a problem is left out; the other codes of the file still work. `send` lists the problems
when the requested code is missing.

## Comments as annotations

rf433 ignores comments, so other tools may use them for their own purposes. A web remote can, for
example, read the comment line above a code as colour and label of its button:

```
  begin raw_codes
    #0A0 Light on
    name Light_on
      270 2700 …

    #A00 Light off
    name Light_off
      270 2700 …
  end raw_codes
```

Such a convention is up to the tool; [f0-converter](https://github.com/d03n3rfr1tz3/f0-converter)
writes these lines with `--extension webremote`.
