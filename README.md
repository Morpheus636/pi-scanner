# PiScanner
PiScanner is a DIY digital scanner that runs on Raspberry Pi 5. It uses a Software Defined Radio with SDRTrunk to demodulate most trunked digital radio types. While analogue scanners are readily available for $100-200, commercially-available digital scanners start at $600 and go up from there. PiScanner is both more capable and cheaper, starting at approximately $250, depending on configuration options you choose.

![Image of the back of PiScanner](/images/back.jpg)

## Features
- Listen to digital and trunked radio systems used by most major public safety agencies in the US. 
    - **NOTE:** Encrypted radio systems, such as those used by the NYPD and many European and Australian agencies, cannot be monitored.
- Automatically import radio systems from the Radio Reference databases. (Requires a Radio Reference premium account.)
- Stream scanner activity and upload calls to Broadcastify.
- Support for Bluetooth audio.

### TODO
- [x] Touchscreen
- [x] Active Cooling
- [x] Speakers
- [x] Headphone Jack
- [x] Case
- [x] Multiple Tuners
- [ ] External power connector
- [ ] External power button
- [ ] External headphone jack
- [ ] Battery

## Hardware Requirements
- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) (8GB Minimum; 16GB Recommended)
- [Raspberry Pi Active Cooler](https://www.raspberrypi.com/products/active-cooler/) (Not strictly necessary, but SDRTrunk can be fairly CPU intensive.)
- [Raspberry Pi Touch Display 2](https://www.raspberrypi.com/products/touch-display-2/) (PiScanner could be adapted to work with the original touch display, but the new model is highly recommended due to its higher resolution. You will need the 15-22 pin display cable to connect it to Pi 5. You can also ignore the parts about rotating the display if you use the original.)
- [Raspberry Pi RTC Battery](https://www.raspberrypi.com/products/rtc-battery/) (Not required for online-only use, but if you intend to use the Pi Scanner without internet, you need an RTC to ensure timestamps are correct.)
- [RASPIAUDIO Mic+ V3](https://raspiaudio.com/product/mic/) (Any Audio HAT will work, but this one is useful because it includes both speakers and a headphone jack. Not required if you are using PiScanner only as a streaming node or Bluetooth audio.)
- [RTL-SDR Nano](https://www.amazon.com/dp/B076GWF6FF) (This is a two pack. One will work, but you will be bandwidth limited if you want to monitor multiple channels.)
- [SmartiPi Touch Pro 3](https://smarticase.com/collections/smartipi-touch-pro-3/products/smartipi-touch-pro-3)
- [Fan](https://smarticase.com/products/smartipi-touch-pro-3-fan?pr_prod_strat=jac&pr_rec_id=398c95a2a&pr_rec_pid=7754016063551&pr_ref_pid=7739155054655&pr_seq=uniform) - Get the one for Raspberry Pi 4, because the Pi 5's fan header is already being used by the active cooler.
- MiroSD Card
- USB-C Power Supply (The official 27W adapter is recommended, but and 5V 5A USB-C power adapter will work.)
- Right-angle USB-C adapter
- Dupont extension jumpers

## SD Card Setup
1. Download and run the Raspberry Pi Imager on your computer.
2. Select the following options:
    - Device: Raspberry Pi 5
    - OS: Raspberry Pi OS (64-Bit)
    - Storage: Your SD Card
3. Change these settings:
    - Set a username and password.
    - Set the Pi's hostname to `scanner`.
    - Enter WiFi Credentials.
    - Enable SSH.
4. Flash the SD Card image.
5. Disconnect and re-connect the SD card.
6. Open `config.txt` in the root of the SD card and add the following line:

    ```
    usb_max_current_enable=1
    ```

## Hardware Setup
1. Insert the MicroSD card into the connector in the Pi.
2. Install the Pi active cooler.
3. Connect the RTC battery to the J5 battery connector between the USB-C and HDMI port on the Pi 5. [See documentation from Raspberry Pi](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#real-time-clock-rtc)
4. Connect the Audio HAT to the Pi. You will need to use the included GPIO riser if you are also using the active cooler.
5. Connect the Touch Display to the Pi. You will need dupont extensions. [See documentation from Raspberry Pi](https://www.raspberrypi.com/documentation/accessories/touch-display-2.html#content).
    - Connect the flex cable to the header labeled `CAM/DISP 1`.
    - Connect the red wire to pin 2
    - Connect the black wire to pin 6
6. Connect the second fan to the Pi. You will need dupont extensions.
    - Connect the red wire to pin 4
    - Connect the black wire to pin 9
    - Connect the blue wire to pin 12


## Software Setup
### OS Configuration
1. **SSH Into the Pi** Connect your computer to the same network you configured in the Raspberry Pi Imager, then run the following command. You will need to enter the passsword you set earlier. Unless specifically noted, al l other commands should run in an SSH session.

    ```sh
    ssh scanner@scanner
    ``` 

2. **Update Raspberry Pi OS**

    ```sh
    sudo apt update -y
    sudo apt upgrade -y
    ```

3. **Install Drivers**

    ```sh
    sudo apt install rtl-sdr -y
    ```

4. **Enable Auto Login**

    ```sh
    sudo raspi-config nonint do_boot_behaviour B4
    ```

5. **Disable Splash Screen**

    ```sh
    sudo raspi-config nonint do_boot_splash 0
    ```

6. **Set Window Manager** You should use Wayland with LABWC. Other options do not properly support touchscreen rotation, and will break the SDRTrunk auto-start behavior.

    ```sh
    sudo raspi-config nonint do_wayland W3
    ```

7. **Rotate GUI** The Touch Display 2 is portrait by default. To rotate the GUI environment, use the GUI to open the Raspberry Pi menu, then navigate to **Preferences** > **Screen Configuration**. At the bottom left of the Screen Configuration menu, click **Screens** > **DSI-2** > **Orientation** > **Left**, then click **Apply**.

8. **Rotate Terminal** To rotate the pre-desktop environment, you will need to modify `/boot/firmware/cmdline.txt`.
    - Run:
        ```sh
        sudo nano /boot/firmware/cmdline.txt
        ```

    - Scroll to the end of the first line and insert the following (separated by one space from the existing text). Note the whole file should be one line.
        ```
        video=DSI-2:720x1280@60,rotate=90
        ```

    - Press `Ctrl` + `x`, then `Y` and `Enter` to save and exit.

9. **Enable Fan Control**
    ```sh
    wget https://github.com/morpheus636/pi-scanner/raw/refs/heads/main/config/fan_control.py
    sudo wget https://github.com/morpheus636/pi-scanner/raw/refs/heads/main/config/fan-control.service -P /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable fan-control
    sudo systemctl start fan-control
    ```

10. **Reboot**
    ```sh
    sudo reboot
    ```

### SDRTrunk
1. **Install SDRTrunk**

    ```sh
    wget https://github.com/DSheirer/sdrtrunk/releases/download/v0.6.0/sdr-trunk-linux-aarch64-v0.6.1.zip
    unzip sdr-trunk-linux-v0.6.1.zip sdr-trunk
    chmod +x sdr-trunk/bin/sdr-trunk
    ```

2. **Install JMBE**

    ```sh
    wget https://github.com/DSheirer/jmbe/releases/download/v1.0.9/jmbe-creator-linux-aarch64-v1.0.9.zip
    unzip jmbe-creator-linux-aarch64-v1.0.9.zip jmbe-creator
    chmod +x jmbe-creator/bin/creator
    ```

3. **Create Application Menu Entry for SDRTrunk**
    ```sh
    wget https://github.com/morpheus636/pi-scanner/raw/refs/heads/main/config/SDRTrunk.desktop -P .local/share/applications/
    ```

4. **Set SDRTrunk to Start Automatically**
    ```sh
    mkdir -p .config/autostart
    cp .local/share/applications/SDRTrunk.desktop .config/autostart/
    ```

5. **Set SDRTrunk Window Format** 
    - Run: 
        ```sh
        nano .config/labwc/rc.xml
        ```

    - Insert the following XML before the closing tag (`</openbox_config>`)
        ```xml
        <windowRules>
            <windowRule title="sdrtrunk v*" serverDecoration="no" skipTaskbar="yes" />
        </windowRules>
        ```
    - Press `Ctrl` + `x`, then `Enter` to save and exit.

## Attributions
PiScanner is based on the [SDR Pi](https://www.youtube.com/watch?v=3PCHfa8JTaY) by TopDNG.
### Software
- [SDRTrunk](https://github.com/DSheirer/sdrtrunk/) for decoding and recording radio signals.
