# ABElectronics_CLI - iopi_python

A command line interface written in C for controlling the IO Pi, [IO Pi Plus](https://www.abelectronics.co.uk/p/54/IO-Pi-Plus) and [IO Pi Zero](https://www.abelectronics.co.uk/p/71/IO-Pi-Zero).

Requires python smbus to be installed with: 
```
sudo apt-get install python-smbus
```

The program can be run from the terminal window with the following command

```
python iopi.py <option> <argument>
```

For example, to read a pin from bus 1 on the IO Pi at I2C address 0x20 with pull-up resistors enabled you would run the following command.

```
python iopi.py -a 0x20 -n 1 -d 0 -u 1 -r
```

Input values can be in decimal, hexidecimal or binary.  When using hexidemial format the number with 0x, when using binary format the number with 0b.

```123 = 0x7b = 0b1111011```

When reading a single value from a port or pin the result will be returned as a decimal number if no formatting options are selected.

When reading multiple values the numbers will be formatted as a JSON string, for example:
```"read":"0","interruptstatus":"0","interruptcapture":"0"```

## command arguments
```-a --address=i2c address```  
e.g., '-a 0x21' sets the I2C address to 0x21; The default address if -a is not specified is 0x20

```-p --port=value```  
set the port to access; e.g., '-p 1' or '--port=1' sets the port to 1.  If no port or pin is specified the program will default to port 0
-n --pin=value; set the pin to access; e.g., '-n 7' or '--pin=7' sets the pin to 7.  If no port or pin is specified the program will default to port 0.  If a port is specified as well as a pin the program will use the selected port and ignore the pin value.

```-r --read```  
Read the status of the selected port or pin; For each pin 0 = logic low, 1 = logic high; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1.

```-w --write=value```  
Write a value to the selected port or pin; For each pin 0 = logic low, 1 = logic high; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1;  e.g., '-w 1 -n 3' will set pin 3 to be logic high.

```-d --direction=value```  
set port or pin direction; For each pin 0 = output, 1 = input; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1;  e.g., '-d 1 -n 3' will set pin 3 to be an input.  

```-i --invert=value```  
invert the selected port or pin; For each pin 0 = normal, 1 = inverted; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1;  e.g., '-i 1 -n 3' will set pin 3 to be inverted.

```-u --pullup=value```  
Set the internal 100K pull-up resistors for the selected port or pin; 1 = enabled, 0 = disabled; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1;  e.g., '-u 1 -n 3' will enable the pull-up resistor for pin 3.

```-m --mirrorinterrupts=value```  
Set the interrupt pins to be mirrored or for separate ports; 1 = The pins are internally connected, 0 = The pins are not connected. INTA is associated with PortA and INTB is associated with PortB;  e.g., '-m 1' will set both interrupt pins IA and IB to be mirrored.

```-l --interruptpolarity=value```  
Set the polarity of the interrupt output pins IA and IB; 1 = Active-high, 0 = Active-low; ; e.g., '-l 1' will set the interrupt output pins to go logic high when an interrupt occurs.

```-t --interrupttype=value```  
Sets the type of interrupt for the selected pin or port; 1 = interrupt is fired when the pin matches the default value, 0 = the interrupt is fired on state change; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1; e.g., '-t 0 -n 3' will set the interrupt for pin 3 to trigger on state change.

```-f --interruptdefaults=value```  
Set the compare value for interrupt-on-change on the selected port. If the associated pin level is the opposite from the set value an interrupt occurs; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1;  e.g., '-f 1 -n 3' will set the default value for pin 3 to be logic high.

```-e --enableinterrupts=value```  
Enable interrupts for the selected port or pin; For each pin 0 = off, 1 = on; If a port has been selected the value can be 0 to 255.  If a pin has been selected the value can be 0 or 1;  e.g., '-e 1 -n 3' will enable the interrupt for pin 3.

```-s --interruptstatus```  
Read the interrupt status for the selected port or pin

```-c --interruptcapture```  
Read the value from the selected port or pin at the time of the last interrupt trigger

```-z --resetinterrupts```  
Set the interrupts IA and IB to 0

```-b --binary```  
Set the output number format to binary; e.g., 0b00100100

```-x --hex```  
Set the output number format to hexidecimal; e.g., 0xFC