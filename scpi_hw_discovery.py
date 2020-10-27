import serial.tools.list_ports as port_list
import serial
from time import sleep


def idn_scan(dump_yml=False, baud_rates=(9600,)):
    """
    Sends "*IDN?" command to all COM ports where hardware is present.
    Commands are sent blindly with EOL (\r\n) termination and at baud_rates specified.
    Parameters
    ----------
    dump_yml - enables (True) or disables (False) dumping of .yaml file containing the mapping of
                IDN string to COM and BAUD
    baud_rates - tuple of baud rates at which the IDN query sequence will be repeated

    Returns - idn_to_com dictionary mapping IDN string (key) to a dictionary of (PORT) and (BAUD)
    This dictionary is also output to a .yaml file if dump_yaml argument is set to true.
    -------

    """
    TIMEOUT = 0.5  # If a large number of serial devices are present you might wish to shorten the timeout time to
    # speed up the query rounds however this may be at the cost of some devices not having enough time to respond

    idn_to_com = {}

    for baud in baud_rates:
        print(f'\n<NOTE>: *IDN? requests are sent blindly as:\n ASCII, EOL terminated,\n baudrate={str(baud)}, '
              f'bytesize=EIGHTBITS, \n parity=PARITY_NONE, stopbits=STOPBITS_ONE \n Device may not respond with IDN '
              f'if:\n  -device uses other baudrate or encoding, \n  -device is non SCPI compliant.\n\n')

        for port, desc, hwid in port_list.comports():

            try:
                ser = serial.Serial(port, timeout=TIMEOUT, baudrate=baud, writeTimeout=0)
                sleep(0.5)
                ser.write(b'*IDN?\r\n')
                idn = ser.readline()
                print(f'PORT: {port}\n IDN: {idn}\n DESC: {desc} \n HWID: {hwid}\n')
                ser.close()
                if idn != b'':
                    idn_to_com.update({idn.strip(): {'PORT': port, 'BAUD': baud}})
            except serial.SerialException as exc:
                print(f'PORT: {port}\n IDN: ?\n DESC: {exc} \n HWID: ?\n')

    if dump_yml:
        import yaml
        with open('idn_to_com.yml', 'w') as f:
            f.write(yaml.dump(idn_to_com, default_flow_style=False))
            
    return idn_to_com


if __name__ == "__main__":
    import sys

    print(sys.argv)
    print(len(sys.argv))

    if len(sys.argv) == 1:
        idn_scan()
    elif len(sys.argv) == 2:
        idn_scan(dump_yml=(sys.argv[1] == 'dump_yml=True'))
    else:
        idn_scan(dump_yml=(sys.argv[1] == 'dump_yml=True'), baud_rates=tuple(sys.argv[2:]))



