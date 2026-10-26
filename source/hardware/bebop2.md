# Bebop 2 reference and troubleshooting

Selected material from the archived Bebop wiki page, restricted to Bebop 2.
For initial setup, uploading, autostart, networking, calibration, and joystick
setup, see **Experimental Flight** in the main Paparazzi Sphinx documentation
(`getting_started/first_flight.rst`).

```{note}
The source wiki revision dates from 2022-09-28 and mixes Bebop generations.
The code references below were checked against the local Paparazzi checkout
when preparing this page. The procedures have not been tested on a drone.
```

## Video streaming

Enable `video_rtp_stream` in the airframe's modules section. For example,
to send the front camera to a specific ground station:

```xml
<module name="video_rtp_stream">
  <configure name="VIEWVIDEO_HOST" value="192.168.42.2"/>
  <configure name="VIEWVIDEO_BROADCAST" value="FALSE"/>
  <configure name="VIEWVIDEO_PORT_OUT" value="5000"/>
  <define name="VIEWVIDEO_CAMERA" value="front_camera"/>
</module>
```

Replace `192.168.42.2` with the laptop's address on the drone network. The module
depends on `video_thread`; check the selected airframe's camera configuration.
`bottom_camera` is another camera choice. The default output ports are 5000
and 6000 for the first and second streams; the default destination is
`MODEM_HOST`, with broadcast enabled.

From the Paparazzi repository root, receive the stream with:

```sh
python3 sw/tools/rtp_viewer/rtp_viewer.py --port 5000
```

The viewer requires its Python/GStreamer dependencies. Alternatively, open the
provided SDP file with VLC:

```sh
vlc sw/tools/rtp_viewer/rtp_5000.sdp
```

If no image arrives, check that the autopilot is running, the camera and module
are enabled, the destination address and port match, and the ground station
allows incoming UDP traffic on that port. The module exposes an `rtp` setting
(`viewvideo.use_rtp`) to enable or disable streaming at runtime.

Source references: `conf/modules/video_rtp_stream.xml`,
`sw/tools/rtp_viewer/rtp_viewer.py`, and `sw/tools/rtp_viewer/rtp_5000.sdp`.
This module uses JPEG over RTP; the stock firmware's H.264 recording specification
is not the format of this stream.

## Dampers and roll oscillations

The wiki reports that the original soft Bebop 2 dampers can contribute to roll
oscillations. It describes harder replacement dampers and a washer modification,
with a possible loss of video quality as vibration isolation is reduced.

The local `conf/airframes/examples/bebop2_opticflow.xml` explicitly assumes
removed or fixed dampers in its INDI configuration, near
`FILTER_ROLL_RATE` and `FILTER_PITCH_RATE`. Mechanical damping and controller
configuration must therefore be considered together; those settings are not a
general prescription for an unmodified Bebop 2.

The wiki links to a [replacement damper design](https://www.thingiverse.com/thing:2135529).
Its suitability and the modification procedures have not been verified here.

## Direct GPS access from a laptop

The internal GPS uses `/dev/ttyPA1`. The Bebop 2 board configuration selects
`UART1` at `B230400`. The shared board header documents forwarding this serial
port over TCP for use with u-center.

Stop Paparazzi and any other application using the GPS serial port before
opening a direct connection. Perform this work with the drone on the bench
and propellers removed.

On the laptop, create a virtual serial port and wait for a TCP connection:

```sh
socat TCP-LISTEN:12345,reuseaddr PTY,link=/tmp/bebop2-gps,raw,echo=0
```

In another terminal, connect to the drone (default address shown):

```sh
telnet 192.168.42.1
```

In the drone shell, replace `LAPTOP_IP` with the laptop's address on the drone
network and forward the GPS port:

```sh
nc LAPTOP_IP 12345 < /dev/ttyPA1 > /dev/ttyPA1
```

For u-center running under Wine, link the virtual serial device to an unused
COM port on the laptop:

```sh
ln -s /tmp/bebop2-gps ~/.wine/dosdevices/com32
```

Select COM32 in u-center. Use another unused COM number if necessary; the Wine
prefix must match the one used to run u-center. Close the bridge before
restarting the autopilot. GPS configuration changes can affect subsequent
Paparazzi or stock-firmware operation.

Source references: `sw/airborne/boards/bebop.h` and
`conf/boards/bebop2.makefile`. Port 12345 keeps this TCP bridge separate from
the video examples.

## Physical serial console

The wiki describes a console under the front cover at `/dev/ttyPA0`, running
at 115200 baud. It also describes enabling an interactive shell through
`/etc/init.d/rcS` when console output is visible but no prompt appears.

These physical access details and startup changes were not verified for
Bebop 2. Confirm the connector, pinout, and electrical levels for the actual
board before attaching an adapter. Do not treat the mixed-generation wiki
photographs or wiring instructions as a verified Bebop 2 pinout.

## Linux devices and internal buses

Bebop 2 uses the shared `bebop` board implementation, with `BEBOP_VERSION2`
enabled by `conf/boards/bebop2.makefile`.

| Interface | Function | Evidence |
| --- | --- | --- |
| `/dev/ttyPA1` / UART1 | Internal GPS; default baud 230400 | Board header and Bebop 2 makefile |
| I2C0 | Camera configuration, including MT9V117 bottom camera | Camera driver; wiki also lists the front camera and its calibration EEPROM |
| I2C1 | Motor controller and AK8963 magnetometer | Actuator driver and `imu_bebop.xml` |
| I2C2 | MPU60x0 accelerometer/gyroscope | `imu_bebop.xml` |
| `/dev/ttyUSB0`, `/dev/ttyUSB1` | Default UART2/UART4 mappings for USB serial adapters | Board header; devices depend on attached hardware |
| `/dev/ttyACM0`, `/dev/ttyACM1` | Default UART5/UART6 mappings for USB ACM devices | Board header; devices depend on attached hardware |

The archived wiki additionally lists `/dev/spidev1.0` for sonar pulse generation,
`/sys/bus/iio/devices/iio:device0` for sonar ADC data, and `/dev/hx280` for the
Hantro video encoder. These exact Linux paths need confirmation on the installed
firmware. The full wiki GPIO/PWM list is omitted because its Bebop 2 applicability
and some clock units are uncertain.

The motor controller uses I2C address **0x08 in 7-bit notation**. The Paparazzi
actuator header represents it as **0x10** using its shifted address convention.
Bebop 2 motor direction handling differs from Bebop 1 in `actuators.c`; use the
Bebop 2 configuration rather than copying the old wiki motor ordering.

Source references: `sw/airborne/boards/bebop.h`,
`sw/airborne/boards/bebop/actuators.c`,
`sw/airborne/boards/bebop/actuators.h`,
`sw/airborne/boards/bebop/mt9v117.c`, and `conf/modules/imu_bebop.xml`.

## Component weights

These are measurements reported in the wiki for a Bebop 2, rather than
manufacturer specifications. Individual aircraft and replacement parts may differ.
All weights are in grams.

| Component | Unit weight | Quantity | Subtotal | Notes |
| --- | ---: | ---: | ---: | --- |
| Motor | 16.5 | 4 | 66.0 | With motor mounting screws |
| Landing gear | 2.4 | 4 | 9.6 | |
| Frame | 49.5 | 1 | 49.5 | With legs |
| Rotor | 5.0 | 4 | 20.0 | |
| Battery | 196.0 | 1 | 196.0 | |
| Camera magnesium frame | 7.3 | 1 | 7.3 | With screws |
| Camera | 14.7 | 1 | 14.7 | |
| Camera protector | 9.0 | 1 | 9.0 | |
| GPS sensor module | 16.0 | 1 | 16.0 | |
| Foam cover | 7.2 | 1 | 7.2 | |
| Main board | 107.0 | 1 | 107.0 | With all wires |
| Dampers | 2.1 | 4 | 8.4 | With screws |
| **Total** | | | **510.7** | Another Bebop 2 was measured at 511.91 g |

## Attribution

Adapted from [Bebop](https://wiki.paparazziuav.org/wiki/Bebop), wiki revision
[26134](https://wiki.paparazziuav.org/w/index.php?oldid=26134)
(2022-09-28). Contributors: Martinmm, Ghattenb, Flixr, Openuas, Microuav, Fvantienen, Ewoud, IHaveADrone, Henri, Rmeertens, Cdejong.
