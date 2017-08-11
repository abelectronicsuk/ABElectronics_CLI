#!/usr/bin/env python

"""
 ================================================
 ABElectronics IO Pi 32-Channel Port Expander Command Line Interface

Requires python smbus to be installed with: sudo apt-get install python-smbus
================================================

The MCP23017 chip is split into two 8-bit ports.  port 0 controls
pins 1 to 8 while port 1 controls pins 9 to 16.
When writing to or reading from a port the least significant bit represents
the lowest numbered pin on the selected port.
"""

import sys
import getopt
try:
    import smbus
except ImportError:
    raise ImportError("python-smbus not found")
import re
import platform


class MCP23017(object):
    """
    All methods for reading and writing to the MCO23017 IO controller
    """

    # Define registers values from datasheet.
    IODIRA = 0x00  # IO value A - 1= input 0 = output.
    IODIRB = 0x01  # IO value B - 1= input 0 = output.
    # Input polarity A - If a bit is set, the corresponding GPIO register bit
    # will reflect the inverted value on the pin.
    IPOLA = 0x02
    # Input polarity B - If a bit is set, the corresponding GPIO register bit
    # will reflect the inverted value on the pin.
    IPOLB = 0x03
    # The GPINTEN register controls the interrupt-onchange feature for each
    # pin on port A.
    GPINTENA = 0x04
    # The GPINTEN register controls the interrupt-onchange feature for each
    # pin on port B.
    GPINTENB = 0x05
    # Default value for port A - These bits set the compare value for pins
    # configured for interrupt-on-change.  If the associated pin level is the
    # opposite from the register bit, an interrupt occurs.
    DEFVALA = 0x06
    # Default value for port B - These bits set the compare value for pins
    # configured for interrupt-on-change.  If the associated pin level is the
    # opposite from the register bit, an interrupt occurs.
    DEFVALB = 0x07
    # Interrupt control register for port A.  If 1 interrupt is fired when the
    # pin matches the default value, if 0 the interrupt is fired on state
    # change.
    INTCONA = 0x08
    # Interrupt control register for port B.  If 1 interrupt is fired when the
    # pin matches the default value, if 0 the interrupt is fired on state
    # change.
    INTCONB = 0x09
    IOCON = 0x0A  # see datasheet for configuration register.
    GPPUA = 0x0C  # pull-up resistors for port A.
    GPPUB = 0x0D  # pull-up resistors for port B.
    # The INTF register reflects the interrupt condition on the port A pins of
    # any pin that is enabled for interrupts. A set bit indicates that the
    # associated pin caused the interrupt.
    INTFA = 0x0E
    # The INTF register reflects the interrupt condition on the port B pins of
    # any pin that is enabled for interrupts.  A set bit indicates that the
    # associated pin caused the interrupt.
    INTFB = 0x0F
    # The INTCAP register captures the GPIO port A value at the time the
    # interrupt occurred.
    INTCAPA = 0x10
    # The INTCAP register captures the GPIO port B value at the time the
    # interrupt occurred.
    INTCAPB = 0x11
    GPIOA = 0x12  # data port A
    GPIOB = 0x13  # data port B
    OLATA = 0x14  # output latches A
    OLATB = 0x15  # output latches B

    # variables

    __address = 0x20  # I2C address
    # initial configuration
    __ioconfig = 0x22
    __bus = None

    def __init__(self, address):
        """
        init object with i2c address, default is 0x20, 0x21 for IOPi board,
        load default configuration
        """
        self.__address = address
        self.__bus = self.__get_smbus()
        self.__bus.write_byte_data(
            self.__address, self.IOCON, self.__ioconfig)
        return

    # local methods
    @staticmethod
    def __get_smbus():
        """
        internal method for getting an instance of the i2c bus
        """
        i2c__bus = 1
        # detect the device that is being used
        device = platform.uname()[1]

        if device == "orangepione":  # running on orange pi one
            i2c__bus = 0

        elif device == "orangepiplus":  # running on orange pi one
            i2c__bus = 0

        elif device == "linaro-alip":  # running on Asus Tinker Board
            i2c__bus = 1

        elif device == "raspberrypi":  # running on raspberry pi
            # detect i2C port number and assign to i2c__bus
            for line in open('/proc/cpuinfo').readlines():
                model = re.match('(.*?)\\s*\\s*(.*)', line)
                if model:
                    (name, value) = (model.group(1), model.group(2))
                    if name == "Revision":
                        if value[-4:] in ('0002', '0003'):
                            i2c__bus = 0
                        else:
                            i2c__bus = 1
                        break
        try:
            return smbus.SMBus(i2c__bus)
        except IOError:
            raise 'Could not open the i2c bus'

    @staticmethod
    def __checkbit(byte, bit):
        """ internal method for reading the value of a single bit
        within a byte """
        value = 0
        if byte & (1 << bit):
            value = 1
        return value

    @staticmethod
    def __updatebyte(byte, bit, value):
        """
        internal method for setting the value of a single bit within a byte
        """
        if value == 0:
            return byte & ~(1 << bit)
        elif value == 1:
            return byte | (1 << bit)

    def __set_pin(self, pin, value, low_reg, high_reg):
        pin = pin - 1
        reg = low_reg
        if pin >= 8:
            reg = high_reg

        regval = self.__bus.read_byte_data(self.__address, reg)
        regval = self.__updatebyte(regval, int(pin), value)
        self.__bus.write_byte_data(self.__address, reg, regval)

    def __set_port(self, port, value, low_reg, high_reg):
        reg = low_reg
        if port == 1:
            reg = high_reg

        self.__bus.write_byte_data(self.__address, reg, value)

    # public methods

    def set_direction(self, target, value, is_pin=False):
        """
        set IO value for a pin or port
        pins 1 to 16, port 0 = pins 1 to 8, port 1 = pins 9 to 16
        """
        if is_pin:
            self.__set_pin(target, value, self.IODIRA, self.IODIRB)
        else:
            self.__set_port(target, value, self.IODIRA, self.IODIRB)
        return

    def set_pullup(self, target, value, is_pin=False):
        """
        set the internal 100K pull-up resistors for an individual pin
        pins 1 to 16, port 0 = pins 1 to 8, port 1 = pins 9 to 16
        value 1 = enabled, 0 = disabled
        """

        if is_pin:
            self.__set_pin(target, value, self.GPPUA, self.GPPUB)
        else:
            self.__set_port(target, value, self.GPPUA, self.GPPUB)
        return

    def write(self, target, value, is_pin=False):
        """
        write to an individual pin or port
        pins 1 to 16, port 0 = pins 1 to 8, port 1 = pins 9 to 16
        """
        if is_pin:
            self.__set_pin(target, value, self.GPIOA, self.GPIOB)
        else:
            self.__set_port(target, value, self.GPIOA, self.GPIOB)
        return

    def read(self, target, is_pin=False):
        """
        read the value of an individual pin 1 - 16
        returns 0 = logic level low, 1 = logic level high
        """
        value = 0

        if is_pin:
            target = target - 1
            if target < 8:
                value = self.__checkbit(self.__bus.read_byte_data(
                    self.__address, self.GPIOA), target)
            else:
                target = target - 8
                value = self.__checkbit(self.__bus.read_byte_data(
                    self.__address, self.GPIOB), target)
        else:
            if target == 1:
                value = self.__bus.read_byte_data(self.__address, self.GPIOB)
            else:
                value = self.__bus.read_byte_data(self.__address, self.GPIOA)

        return value

    def invert(self, target, value, is_pin=False):
        """
        invert the polarity of the pins on a selected port
        port 0 = pins 1 to 8, port 1 = pins 9 to 16
        polarity 0 = same logic state of the input pin, 1 = inverted logic
        state of the input pin
        """
        if is_pin:
            self.__set_pin(target, value, self.IPOLA, self.IPOLB)
        else:
            self.__set_port(target, value, self.IPOLA, self.IPOLB)
        return

    def mirror_interrupts(self, value):
        """
        1 = The INT pins are internally connected, 0 = The INT pins are not
        connected. __inta is associated with PortA and __intb is associated
        with PortB
        """
        __ioconfig = self.__bus.read_byte_data(self.__address, self.IOCON)
        __ioconfig = self.__updatebyte(__ioconfig, 6, value)
        self.__bus.write_byte_data(self.__address, self.IOCON, __ioconfig)

        return

    def set_interrupt_polarity(self, value):
        """
        This sets the polarity of the INT output pins
        1 = Active-high.
        0 = Active-low.
        """
        __ioconfig = self.__bus.read_byte_data(self.__address, self.IOCON)
        __ioconfig = self.__updatebyte(__ioconfig, 1, value)
        self.__bus.write_byte_data(self.__address, self.IOCON, __ioconfig)

        return

    def set_interrupt_type(self, target, value, is_pin=False):
        """
        Sets the type of interrupt for each pin on the selected port
        1 = interrupt is fired when the pin matches the default value, 0 =
        the interrupt is fired on state change
        """
        if is_pin:
            self.__set_pin(target, value, self.INTCONA, self.INTCONB)
        else:
            self.__set_port(target, value, self.INTCONA, self.INTCONB)
        return

    def set_interrupt_defaults(self, target, value, is_pin=False):
        """
        These bits set the compare value for pins configured for
        interrupt-on-change on the selected port.
        If the associated pin level is the opposite from the register bit, an
        interrupt occurs.
        """
        if is_pin:
            self.__set_pin(target, value, self.DEFVALA, self.DEFVALB)
        else:
            self.__set_port(target, value, self.DEFVALA, self.DEFVALB)
        return

    def set_interrupt(self, target, value, is_pin=False):
        """
        Enable interrupts for the pins on the selected port
        port 0 = pins 1 to 8, port 1 = pins 9 to 16
        value = number between 0 and 255 or 0x00 and 0xFF
        """
        if is_pin:
            self.__set_pin(target, value, self.GPINTENA, self.GPINTENB)
        else:
            self.__set_port(target, value, self.GPINTENA, self.GPINTENB)
        return

    def read_int_status(self, target, is_pin=False):
        """
        read the interrupt status for the pins on the selected port
        port 0 = pins 1 to 8, port 1 = pins 9 to 16
        """
        value = 0

        if is_pin:
            target = target - 1
            if target < 8:
                value = self.__checkbit(self.__bus.read_byte_data(
                    self.__address, self.INTFA), target)
            else:
                target = target - 8
                value = self.__checkbit(self.__bus.read_byte_data(
                    self.__address, self.INTFB), target)
        else:
            if target == 1:
                value = self.__bus.read_byte_data(self.__address, self.INTFB)
            else:
                value = self.__bus.read_byte_data(self.__address, self.INTFA)

        return value

    def read_int_capture(self, target, is_pin=False):
        """
        read the value from the selected port at the time of the last
        interrupt trigger
        port 0 = pins 1 to 8, port 1 = pins 9 to 16
        """
        value = 0

        if is_pin:
            target = target - 1
            if target < 8:
                value = self.__checkbit(self.__bus.read_byte_data(
                    self.__address, self.INTCAPA), target)
            else:
                target = target - 8
                value = self.__checkbit(self.__bus.read_byte_data(
                    self.__address, self.INTCAPB), target)
        else:
            if target == 1:
                value = self.__bus.read_byte_data(self.__address, self.INTCAPB)
            else:
                value = self.__bus.read_byte_data(self.__address, self.INTCAPA)

        return value

    def reset_interrupts(self):
        """
        Reset the interrupts A and B to 0
        """
        self.read_int_capture(0, False)
        self.read_int_capture(1, False)
        return


class Command(object):
    """
    Main program methods
    """

    arguments = {
        ('-r', '--read'): 'read',
        ('-w', '--write'): 'write',
        ('-d', '--direction'): 'direction',
        ('-i', '--invert'): 'invert',
        ('-u', '--pullup'): 'pullup',
        ('-m', '--mirrorinterrupts'): 'mirrorinterrupts',
        ('-l', '--interruptpolarity'): 'interruptpolarity',
        ('-t', '--interrupttype'): 'interrupttype',
        ('-f', '--int_defaults'): 'int_defaults',
        ('-e', '--enableinterrupts'): 'enableinterrupts',
        ('-s', '--int_status'): 'int_status',
        ('-c', '--int_capture'): 'int_capture',
        ('-z', '--resetinterrupts'): 'resetinterrupts',
        ('-b', '--binary'): 'bin',
        ('-x', '--hex'): 'hex'
    }

    flags = {
        'address': False,
        'direction': False,
        'enableinterrupts': False,
        'int_capture': False,
        'int_defaults': False,
        'interruptpolarity': False,
        'int_status': False,
        'interrupttype': False,
        'invert': False,
        'mirrorinterrupts': False,
        'pin': False,
        'port': False,
        'pullup': False,
        'read': False,
        'resetinterrupts': False,
        'write': False,
        'bin': False,
        'hex': False
    }

    params = {
        'address': 0,
        'direction': 0,
        'enableinterrupts': 0,
        'int_defaults': 0,
        'interruptpolarity': 0,
        'interrupttype': 0,
        'invert': 0,
        'mirrorinterrupts': 0,
        'pin_or_port': 0,
        'pullup': 0,
        'write': 0
    }

    output = {
        'int_capture': 0,
        'int_status': 0,
        'read': 0,
    }

    output_format = "dec"
    output_count = 0

    @staticmethod
    def error_message(message):
        """
        print the error message to the console
        """
        print(message)
        return

    def num(self, val):
        """
        Convert a hex, decimal or binary string to a number
        """
        out = 0
        try:
            if "0x" in val:  # hex
                out = int(val, 16)
            elif "0b" in val:  # binary
                out = int(val, 2)
            else:  # decimal
                out = int(val, 10)
        except ValueError:
            self.error_message("Error parsing number: " + str(val))
            sys.exit(2)
        return out

    def parse_option(self, arg, option):
        """
        Check the option argument to see if it is within range.
        """
        if arg:
            val = self.num(arg)
            if self.flags['port'] and (val < 0 or val > 255):
                self.error_message(option + " argument outside of range.")
                sys.exit(2)
            elif self.flags['pin'] and (val < 0 or val > 1):
                self.error_message(option + " argument outside of range.")
                sys.exit(2)
            self.params[option] = val

        self.flags[option] = True

        return

    def run_io_commands(self):
        """
        Send all of the IO related commands to the MCP23017
        """
        # direction
        bus = MCP23017(self.params['address'])

        if self.flags['direction']:
            bus.set_direction(self.params['pin_or_port'],
                              self.params['direction'], self.flags['pin'])

        # invert
        if self.flags['invert']:
            bus.invert(self.params['pin_or_port'],
                       self.params['invert'], self.flags['pin'])

        # pullup
        if self.flags['pullup']:
            bus.set_pullup(self.params['pin_or_port'],
                           self.params['pullup'], self.flags['pin'])

        # write
        if self.flags['write']:
            bus.write(self.params['pin_or_port'],
                      self.params['write'], self.flags['pin'])

        # read
        if self.flags['read']:
            self.output_count += 1
            self.output['read'] = bus.read(self.params['pin_or_port'],
                                           self.flags['pin'])

        self.run_interrupt_commands(bus)

    def run_interrupt_commands(self, bus):
        """
        Send all of the interrupt related commands to the MCP23017
        """
        # enable interrupts
        if self.flags['enableinterrupts']:
            bus.set_interrupt(self.params['pin_or_port'],
                              self.params['enableinterrupts'],
                              self.flags['pin'])

        # mirror interrupts
        if self.flags['mirrorinterrupts']:
            bus.mirror_interrupts(self.params['mirrorinterrupts'])

        # interrupt polarity
        if self.flags['interruptpolarity']:
            bus.set_interrupt_polarity(self.params['interruptpolarity'])

        # interrupt type
        if self.flags['interrupttype']:
            bus.set_interrupt_type(self.params['pin_or_port'],
                                   self.params['interrupttype'],
                                   self.flags['pin'])

        # interrupt defaults
        if self.flags['int_defaults']:
            bus.set_interrupt_defaults(self.params['pin_or_port'],
                                       self.params['int_defaults'],
                                       self.flags['pin'])

        # interrupt status
        self.output_count += 1
        if self.flags['int_status']:
            self.output['int_status'] = bus.read_int_status(
                self.params['pin_or_port'],
                self.flags['pin'])

        # interrupt capture

        if self.flags['int_capture']:
            self.output_count += 1
            self.output['int_capture'] = bus.read_int_capture(
                self.params['pin_or_port'],
                self.flags['pin'])

        # reset interrupts
        if self.flags['resetinterrupts']:
            bus.reset_interrupts()

        return

    def format_number(self, value):
        """
        Format the number as determined by the Command
        """
        out = ""
        if self.flags['hex']:
            out = '0x{0:02x}'.format(value)
        elif self.flags['bin']:
            out = '0b{0:08b}'.format(value)
        else:
            out = str(value)
        return out

    def write_output(self):
        """
        Write any read values to the display
        """
        output = ""
        if self.flags['read']:
            if self.flags['int_status'] or self.flags['int_capture']:
                output += "\"read\":\"" + self.format_number(
                    self.output['read']) + "\""
            else:
                output += self.format_number(self.output['read'])

        if self.flags['int_status']:
            if self.flags['read'] or self.flags['int_capture']:
                output += ",\"int_status\":\"" + self.format_number(
                    self.output['int_capture']) + "\""
            else:
                output += self.format_number(self.output['int_status'])
        if self.flags['int_capture']:
            if self.flags['read'] or self.flags['int_status']:
                output += ",\"int_capture\":\"" + self.format_number(
                    self.output['int_status']) + "\""
            else:
                output += self.format_number(self.output['int_capture'])
        print(output)
        return

    def check_for_port_or_pin(self, opts):
        """
        Chec if an address, port or pin has been selected
        """
        for opt, arg in opts:
            if opt in ('-a', '--address'):
                if self.num(arg) >= 0x20 and self.num(arg) <= 0x27:
                    self.params['address'] = self.num(arg)
                else:
                    self.error_message('Address out of range - 0x20 to 0x27.')
                    sys.exit(2)
            elif opt in ("-p", "--port"):
                if self.num(arg) == 0 or self.num(arg) == 1:
                    self.flags['port'] = True
                    self.params['pin_or_port'] = self.num(arg)
                else:
                    self.error_message("Port out of range: 0 or 1. " + arg)
                    sys.exit(2)
            elif opt in ("-n", "--pin"):
                if self.flags['port']:
                    self.error_message("You cannot select both port and pin.")
                    sys.exit(2)
                if int(arg) >= 1 and int(arg) <= 16:
                    self.flags['pin'] = True
                    self.params['pin_or_port'] = int(arg)
                else:
                    self.error_message("Pin outside of range: 1 to 16.")
                    sys.exit(2)

        if not self.flags['port'] and not self.flags['pin']:
            self.error_message("Please select a port or pin number.")
            sys.exit(2)

        return


def main(argv):
    """
    Main function.
    """

    cmd = Command()

    cmd.params['address'] = 0x20  # default I2C address

    try:
        opts, args = getopt.getopt(argv, "a:bcd:e:f:i:l:m:n:p:rst:u:w:xz",
                                   ["address=", "port=", "pin=", "read",
                                    "write=", "direction=", "invert=",
                                    "pullup=", "mirrorinterrupts=",
                                    "interruptpolarity=", "interrupttype=",
                                    "int_defaults=", "enableinterrupts=",
                                    "int_status", "int_capture",
                                    "resetinterrupts", "binary", "hex"])
    except getopt.GetoptError:
        cmd.error_message("option not recognised or no argument given.")
        sys.exit(2)

    # check if the target is a port or pin
    cmd.check_for_port_or_pin(opts)

    #  parse arguments by searching the arguments dictionary
    for opt, arg in opts:
        val = [value for key, value in cmd.arguments.items()
               if len(key) > 1 and (key[0] == opt or key[1] == opt)]

        if val:
            cmd.parse_option(arg, str(val).strip('[]').strip("''"))

    cmd.run_io_commands()
    cmd.write_output()

if __name__ == "__main__":
    main(sys.argv[1:])
