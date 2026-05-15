# arylic-amp

A Python script for changing settings of the Arylic Up2Stream amplifier boards over TCP (port 8899).

## Usage

```bash
python arylic.py <host> [--command <cmd>] [--port <port>] [--examples]
```

**Get current input mode (default command):**
```bash
python arylic.py 192.168.1.42
```

**Send a custom command:**
```bash
python arylic.py 192.168.1.42 --command "MCU+VOL+GET"
python arylic.py 192.168.1.42 --command "MCU+VOL+SET+50"
```

**List available commands:**
```bash
python arylic.py 192.168.1.42 --examples
```

## Protocol

Packets are sent over TCP using the Arylic binary framing:

```
[4B header][4B length LE][4B checksum LE][8B reserved][ASCII payload]
```

Some responses arrive unframed (plain ASCII); both are handled.
