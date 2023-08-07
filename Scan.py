import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
import threading
import asyncio
from bleak import BleakScanner
import obd
from obd import OBDStatus
from time import sleep
import bluetooth
import subprocess
import customtkinter
from tkdial import Meter
from rpi_backlight import Backlight
from tkinter import messagebox
import json


font1 = ('Arial',30)
font2 = ('Times bold italic',50)
font3 = ('Times bold italic',30)
font4 = ('Times bold italic',15)

root = tk.Tk()
root.configure(bg='black')
root.attributes('-fullscreen', True)

macjson = tk.StringVar()
acmac = tk.StringVar()
setauto = tk.StringVar()

def autoconnectbl():
    subprocess.call('sudo rfcomm connect hci0 %s' % macjson.get(), shell=True)
    print("Connected successfully!")

if setauto == 'True':
    f = open('data.json')
    data = json.load(f)
    for i in data['mac ']:    
        macjson.set(i)
cnctt = threading.Thread(target=autoconnectbl,daemon=True)
cnctt.start()


def acsetjson():
    data = {
        "mac ": acmac.get()
    }
    
    with open('macdata.json', 'w') as outfile:
        json.dump(data, outfile)


def basicw():
    basicw1 = tk.Toplevel(root)
    basicw1.configure(bg='black')
    basicw1.attributes('-fullscreen', True)

    time = tk.Label(basicw1, text="",fg='white',bg='black', font=font1)
    time.grid(row=0,column=0, sticky='w')
    
    tmpl = tk.Label(basicw1,text="Temp: ", fg='white',bg='black',font=font2)
    tmpl.grid(row=1,column=0, sticky='w')
    tempgauge = tk.Label(basicw1,text='', fg='white',bg='black',font=font2)
    tempgauge.grid(row=1,column=1)
    rpml = tk.Label(basicw1, text='RPM: ',fg='white', bg='black',font=font2)
    rpml.grid(row=2,column=0, sticky='w')
    kmhl = tk.Label(basicw1, text='Km/h: ',fg='white', bg='black',font=font2)
    kmhl.grid(row=3,column=0, sticky='w')
    rpmgauge = tk.Label(basicw1,text='',fg='white',bg='black',font=font2)
    rpmgauge.grid(row=2,column=1)
    speedgauge = tk.Label(basicw1,text='',fg='white',bg='black',font=font2)
    speedgauge.grid(row=3,column=1)
    blanktospaceout = tk.Label(basicw1,text='',fg='black',bg='black',font=font2)
    blanktospaceout.grid(row=4,column=0)
    voltage = tk.Label(basicw1,text='',fg='white', bg='black',font=font2)
    voltage.grid(row=4,column=0, sticky='w')

    s = ttk.Style()
    s.theme_use('clam')
    s.configure("green.Horizontal.TProgressbar",thickness=50, troughcolor='white',background='green')
    s.configure("red.Horizontal.TProgressbar",thickness=50, troughcolor='white',background='red')

    prcntrpm = tk.IntVar()

    rpmBar = ttk.Progressbar(basicw1,variable=prcntrpm,orient="horizontal",length=800,maximum=15)
    rpmBar.grid(row=5,column=0,columnspan=3,sticky=tk.N+tk.S)
    print(basicw1.winfo_width())

    def timeupdate():
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            time.config(text=current_time)

    if __name__ == '__main__':
        time1 = threading.Thread(name='timec', target=timeupdate, daemon=True)
        time1.start()

    completerpmda = tk.IntVar()

    def gauges():
        while True:
            speeddata = connection.query(obd.commands.SPEED)
            rpmdata = connection.query(obd.commands.RPM)
            watertempdata = connection.query(obd.commands.COOLANT_TEMP)
            volt = connection.query(obd.commands.ELM_VOLTAGE)
            sleep(0.2)
            completespeed = speeddata.value.magnitude 
            completerpm = rpmdata.value.magnitude
            watertemp = watertempdata.value.magnitude
            completevolt = volt.value

            rpmgauge.config(text=completerpm) 
            speedgauge.config(text=completespeed)
            tempgauge.config(text=watertemp)
            voltage.config(text=completevolt)
            prcntrpm.set(completerpm * 0.01)
            completerpmda.set(completerpm)
    
            max = 2000
            maxrpm = int(max)
            rpmsp = completerpmda.get()
            print(rpmsp)
            
            if rpmsp >= maxrpm:
                rpmBar.configure(style="red.Horizontal.TProgressbar", value=completerpmda.get())
            elif rpmsp <= maxrpm:
                rpmBar.configure(style="green.Horizontal.TProgressbar", value=completerpmda.get())
    
    if __name__ == '__main__':
        gaugethread = threading.Thread(name='gaugeupdater', target=gauges, daemon=True)
        gaugethread.start()

    def closew():
        basicw1.destroy()

    ex = tk.Button(basicw1, text='Exit', command=closew, fg='black',bg='white', font=font1)
    ex.grid(row=0,column=2,sticky=tk.E)

def settingsw():
    settingsw1 = tk.Toplevel(root)
    settingsw1.configure(bg='black')
    settingsw1.attributes('-fullscreen', True)
    backlight = Backlight()

    def exit():
            settingsw1.destroy()

    close = tk.Button(settingsw1, text='Exit', command=exit, bg='white',fg='black', font=font1)
    close.grid(row=0,column=4)

    def brightnessup():
        brightness1 = backlight.brightness
        brightnesssetup = 10
        result1 = brightness1 + brightnesssetup
        subprocess.call('rpi-backlight -b %s' % result1, shell=True)
        print(result1)
    
    def brightnessdown():
        brightness2 = backlight.brightness
        brightnesssetdown = 10
        result2 = brightness2 - brightnesssetdown
        subprocess.call('rpi-backlight -b %s' % result2, shell=True)
        print(result2)


    def blue():
        bluetoothw = tk.Toplevel(settingsw1)
        bluetoothw.configure(bg='black')
        bluetoothw.attributes('-fullscreen', True)

        def exit():
            bluetoothw.destroy()

        tk.Button(bluetoothw, text='Exit',command=exit,fg='black',bg='white',font=font1).grid(row=0,column=4)

        devs = tk.Listbox(bluetoothw,height=15,width=50,fg='white',bg='black',font=font4)
        devs.grid(row=1,column=0,columnspan=3,rowspan=4)

        def scann():
            devs.delete(0,tk.END)
            async def main():
                devices = await BleakScanner.discover()
                for d in devices:
                    devs.insert(tk.END,d)
                    print(d)
            asyncio.run(main())

        scanbl = tk.Button(bluetoothw, text='Scan', command=scann, fg='black',bg='white',font=font1)
        scanbl.grid(row=0,column=1)
        
        blanklabeltospace = tk.Label(bluetoothw,text='',fg='black',bg='black',font=font1)
        blanklabeltospace.grid(row=0,column=3)
        
        def connectblue():
            macaddres = tk.StringVar()

            try:
                for i in devs.curselection():
                    s1 = str(devs.get(i))
                    s2 = s1.split(' ')[0]
                    macad = s2.rstrip(s2[-1]) 
                    macaddres.set(macad)
                    portad = 1
                    passcode = '1234'
                    ac = messagebox.askyesno(title='AutoConnect?', message='Would you like to auto connect on next startup?')
            
                    if ac == True:
                        acmac.set(macaddres.get())
                        acsetjson()
                        setauto.set('True')
                    if ac == False:
                        setauto.set('False')

                    def cnct():
                        subprocess.call('sudo rfcomm connect hci0 %s' % macad, shell=True)
                        print("Connected successfully!")
                    cnctt = threading.Thread(target=cnct,daemon=True)
                    cnctt.start()
            
            except bluetooth.btcommon.BluetoothError:
                print("Connection failed:")
        

        cnctblue = tk.Button(bluetoothw, text='Connect', command=connectblue, fg='black',bg='white',font=font1)
        cnctblue.grid(row=0,column=2)

    def statusesw():
        statusesw1 = tk.Toplevel(root)
        statusesw1.configure(bg='black')
        statusesw1.attributes('-fullscreen', True)

        def exit():
            statusesw1.destroy()

        close = tk.Button(statusesw1, text='Exit', command=exit, bg='black',fg='white', font=font1)
        close.grid(row=0,column=4)

        tk.Label(statusesw1, text='Connection:', font=font1, bg='black').grid(row=1,column=0,sticky='w')
        tk.Label(statusesw1, text='ELM Status:', font=font1, bg='black').grid(row=2,column=0,sticky='w')
        tk.Label(statusesw1, text='OBD Status:', font=font1, bg='black').grid(row=3,column=0,sticky='w')
        tk.Label(statusesw1, text='Car Status:', font=font1, bg='black').grid(row=4,column=0,sticky='w')

        
        cstat = tk.Label(statusesw1, text='', font=font1, bg='black')
        cstat.grid(row=1,column=1)
        elmstat = tk.Label(statusesw1, text='', font=font1, bg='black')
        elmstat.grid(row=2,column=1)
        obstat = tk.Label(statusesw1, text='', font=font1, bg='black')
        obstat.grid(row=3,column=1)
        carstat = tk.Label(statusesw1, text='', font=font1, bg='black')
        carstat.grid(row=4,column=1)

        def updatest(): 
            const = OBDStatus.NOT_CONNECTED # "Not Connected"
            elmst = OBDStatus.ELM_CONNECTED # "ELM Connected"
            obdst = OBDStatus.OBD_CONNECTED # "OBD Connected"
            carst = OBDStatus.CAR_CONNECTED # "Car Connected"

            cstat.config(text=const)
            elmstat.config(text=elmst)
            obstat.config(text=obdst)
            carstat.config(text=carst)

        tk.Button(statusesw1,text='Check Connection',command=updatest,bg='white',fg='black',font=font1).grid(row=0,column=2)

    ser = tk.Listbox(settingsw1,height=10,width=50,fg='white',bg='black',font=font4)
    ser.grid(row=3,column=0,columnspan=4,rowspan=3)

    def serialports():
        ports = obd.scan_serial()
        for item in ports:
            ser.insert(tk.END,item)
    
    sersearch = threading.Thread(target=serialports,daemon=True)
    sersearch.start()

    def obdconnect():
        for i in ser.curselection():
            prt = portstr='%s' % ser.get(i)
            print(prt)

        #obd.logger.setLevel(obd.logging.DEBUG)
        global connection
        connection = obd.OBD(prt) #'/dev/pts/2'

    connectobd = tk.Button(settingsw1,command=obdconnect ,text='Connect to OBD',font=font1)
    connectobd.grid(row=0,column=1)

    bl = tk.Button(settingsw1,command=blue ,text='Bluetooth',font=font1)
    bl.grid(row=0,column=2)

    st = tk.Button(settingsw1, command=statusesw,text='Status', font=font1)
    st.grid(row=0,column=3)

    bright = tk.Label(settingsw1,text='Brightness:',fg='white',bg='black', font=font1)
    bright.grid(row=1,column=1)

    brightup = tk.Button(settingsw1, command=brightnessup,text='↑', font=font1)
    brightup.grid(row=2,column=1,sticky=tk.W)

    brightdown = tk.Button(settingsw1, command=brightnessdown,text='↓', font=font1)
    brightdown.grid(row=2,column=1,sticky=tk.E)

def sensorsw():
    sensorsw1 = tk.Toplevel(root)
    sensorsw1.configure(bg='black')
    sensorsw1.attributes('-fullscreen', True)

    def exit():
        sensorsw1.destroy()

    close = tk.Button(sensorsw1, text='Exit', command=exit, bg='white',fg='black', font=font1)
    close.grid(row=0,column=2)

    sens = tk.Listbox(sensorsw1,width=97,height=23,bg='black',fg='white')
    sens.grid(row=1,column=0,columnspan=3)

    def sensorsdata():
        #sleep(5)
        sens.delete(0,tk.END)
        elmversion = 'ELM_Version:                               %s' % (connection.query(obd.commands.ELM_VERSION).value)
        elmvoltage = 'ELM_Voltage:                               %s' % (connection.query(obd.commands.ELM_VOLTAGE).value)
        fuelstatus = 'Fuel_Status:                               %s' % (connection.query(obd.commands.FUEL_STATUS))
        engineload = 'Engine_Load:                               %s' % (connection.query(obd.commands.ENGINE_LOAD))
        coolanttemp = 'Coolant_Temp:                             %s' % (connection.query(obd.commands.COOLANT_TEMP))
        shortfueltrim1 = 'Short_Fuel_Trim_1:                     %s' % (connection.query(obd.commands.SHORT_FUEL_TRIM_1))
        longfueltrim1 = 'Long_Fuel_Trim_1:                       %s' % (connection.query(obd.commands.LONG_FUEL_TRIM_1))
        shortfueltrim2 = 'Short_Fuel_Trim_2:                     %s' % (connection.query(obd.commands.SHORT_FUEL_TRIM_2))
        longfueltrim2 = 'Long_Fuel_Trim_2:                       %s' % (connection.query(obd.commands.LONG_FUEL_TRIM_2))
        fuelpressure = 'Fuel_Pressure:                           %s' % (connection.query(obd.commands.FUEL_PRESSURE))
        intakepressure = 'Intake_Pressure:                       %s' % (connection.query(obd.commands.INTAKE_PRESSURE))
        rpm = 'RPM:                                              %s' % (connection.query(obd.commands.RPM))
        speed = 'Speed:                                          %s' % (connection.query(obd.commands.SPEED))
        timingadvance = 'Timing_Advance:                         %s' % (connection.query(obd.commands.TIMING_ADVANCE))
        intaketemp = 'Intake_Temp:                               %s' % (connection.query(obd.commands.INTAKE_TEMP))
        maf = 'MAF:                                              %s' % (connection.query(obd.commands.MAF))
        throttlepos = 'Throttle_Pos:                             %s' % (connection.query(obd.commands.THROTTLE_POS))
        airstatus = 'Air_Status:                                 %s' % (connection.query(obd.commands.AIR_STATUS))
        o2b1s1 = 'O2_B1_S1:                                      %s' % (connection.query(obd.commands.O2_B1S1))
        o2b1s2 = 'O2_B1_S2:                                      %s' % (connection.query(obd.commands.O2_B1S2))
        o2b1s3 = 'O2_B1_S3:                                      %s' % (connection.query(obd.commands.O2_B1S3))
        o2b1s4 = 'O2_B1_S4:                                      %s' % (connection.query(obd.commands.O2_B1S4))
        o2b2s1 = 'O2_B2_S1:                                      %s' % (connection.query(obd.commands.O2_B2S1))
        o2b2s2 = 'O2_B2_S2:                                      %s' % (connection.query(obd.commands.O2_B2S2))
        o2b2s3 = 'O2_B2_S3:                                      %s' % (connection.query(obd.commands.O2_B2S3))
        o2b2s4 = 'O2_B2_S4:                                      %s' % (connection.query(obd.commands.O2_B2S4))
        obdcomplicance = 'OBD_Compliance:                        %s' % (connection.query(obd.commands.OBD_COMPLIANCE))
        runtime = 'Run_Time:                                     %s' % (connection.query(obd.commands.RUN_TIME))
        distancetraveled = 'Distance_Travelled:                  %s' % (connection.query(obd.commands.DISTANCE_W_MIL))
        fuelrailpressurevac = 'Fuel_Rail_Pressure_Vac:           %s' % (connection.query(obd.commands.FUEL_RAIL_PRESSURE_VAC))
        fuelrailpressuredirect = 'Fuel_Rail_Pressure_Direct:     %s' % (connection.query(obd.commands.FUEL_RAIL_PRESSURE_DIRECT))
        o2s1volt = 'O2_S1_Volt:                                  %s' % (connection.query(obd.commands.O2_S1_WR_VOLTAGE))
        o2s2volt = 'O2_S2_Volt:                                  %s' % (connection.query(obd.commands.O2_S2_WR_VOLTAGE))
        o2s3volt = 'O2_S3_Volt:                                  %s' % (connection.query(obd.commands.O2_S3_WR_VOLTAGE))
        o2s4volt = 'O2_S4_Volt:                                  %s' % (connection.query(obd.commands.O2_S4_WR_VOLTAGE))
        o2s5volt = 'O2_S5_Volt:                                  %s' % (connection.query(obd.commands.O2_S5_WR_VOLTAGE))
        o2s6volt = 'O2_S6_Volt:                                  %s' % (connection.query(obd.commands.O2_S6_WR_VOLTAGE))
        o2s7volt = 'O2_S7_Volt:                                  %s' % (connection.query(obd.commands.O2_S7_WR_VOLTAGE))
        o2s8volt = 'O2_S8_Volt:                                  %s' % (connection.query(obd.commands.O2_S8_WR_VOLTAGE))
        egr = 'EGR:                                              %s' % (connection.query(obd.commands.COMMANDED_EGR))
        egrerror = 'EGR_Error:                                   %s' % (connection.query(obd.commands.EGR_ERROR))
        evaporativepurge = 'Evaporative_Purge:                   %s' % (connection.query(obd.commands.EVAPORATIVE_PURGE))
        fuellevel = 'Fuel_Level:                                 %s' % (connection.query(obd.commands.FUEL_LEVEL))
        evapvaporpressure = 'Evap_Vapor_Pressure:                %s' % (connection.query(obd.commands.EVAP_VAPOR_PRESSURE))
        barometricpressure = 'Barometric_Pressure:               %s' % (connection.query(obd.commands.BAROMETRIC_PRESSURE))
        o2s1wrcurrent = 'O2_S1_WR_Current:                       %s' % (connection.query(obd.commands.O2_S1_WR_CURRENT))
        o2s2wrcurrent = 'O2_S2_WR_Current:                       %s' % (connection.query(obd.commands.O2_S2_WR_CURRENT))
        o2s3wrcurrent = 'O2_S3_WR_Current:                       %s' % (connection.query(obd.commands.O2_S3_WR_CURRENT))
        o2s4wrcurrent = 'O2_S4_WR_Current:                       %s' % (connection.query(obd.commands.O2_S4_WR_CURRENT))
        o2s5wrcurrent = 'O2_S5_WR_Current:                       %s' % (connection.query(obd.commands.O2_S5_WR_CURRENT))
        o2s6wrcurrent = 'O2_S6_WR_Current:                       %s' % (connection.query(obd.commands.O2_S6_WR_CURRENT))
        o2s7wrcurrent = 'O2_S7_WR_Current:                       %s' % (connection.query(obd.commands.O2_S7_WR_CURRENT))
        o2s8wrcurrent = 'O2_S8_WR_Current:                       %s' % (connection.query(obd.commands.O2_S8_WR_CURRENT))
        catalysttempb1s1 = 'Catalyst_Temp_B1S1:                  %s' % (connection.query(obd.commands.CATALYST_TEMP_B1S1))
        catalysttempb2s1 = 'Catalyst_Temp_B2S1:                  %s' % (connection.query(obd.commands.CATALYST_TEMP_B2S1))
        catalysttempb1s2 = 'Catalyst_Temp_B1S2:                  %s' % (connection.query(obd.commands.CATALYST_TEMP_B1S2))
        catalysttempb2s2 = 'Catalyst_Temp_B2S2:                  %s' % (connection.query(obd.commands.CATALYST_TEMP_B2S2))
        controlmodulevolt = 'Control_Module_Volt:                %s' % (connection.query(obd.commands.CONTROL_MODULE_VOLTAGE))
        absoluteload = 'Absolute_Load:                           %s' % (connection.query(obd.commands.ABSOLUTE_LOAD))
        equivratio = 'Equiv_Ratio:                               %s' % (connection.query(obd.commands.COMMANDED_EQUIV_RATIO))
        relativethrottlepos = 'Relative_Throttle_Pos:            %s' % (connection.query(obd.commands.RELATIVE_THROTTLE_POS))
        ambientairtemp = 'Ambient_Air_Temp:                      %s' % (connection.query(obd.commands.AMBIANT_AIR_TEMP))
        throttleposb = 'Throttle_Pos_B:                          %s' % (connection.query(obd.commands.THROTTLE_POS_B))
        throttleposc = 'Throttle_Pos_C:                          %s' % (connection.query(obd.commands.THROTTLE_POS_C))
        acceleratorposd = 'Accelerator_Pos_D:                    %s' % (connection.query(obd.commands.ACCELERATOR_POS_D))
        acceleratorpose = 'Accelerator_Pos_E:                    %s' % (connection.query(obd.commands.ACCELERATOR_POS_E))
        acceleratorposf = 'Accelerator_Pos_F:                    %s' % (connection.query(obd.commands.ACCELERATOR_POS_F))
        throttleactuator = 'Throttle_Actuator:                   %s' % (connection.query(obd.commands.THROTTLE_ACTUATOR))
        maxmaf = 'Max_MAF:                                       %s' % (connection.query(obd.commands.MAX_MAF))
        fueltype = 'Fuel_Type:                                   %s' % (connection.query(obd.commands.FUEL_TYPE))
        ethanolfuelpercent = 'Ethanol_Fuel_Percent:              %s' % (connection.query(obd.commands.ETHANOL_PERCENT))
        absoluteevappressure = 'Absolute_Evap_Vapor_Pressure:    %s' % (connection.query(obd.commands.EVAP_VAPOR_PRESSURE_ABS))
        evappressure = 'Evap_Pressure:                           %s' % (connection.query(obd.commands.EVAP_VAPOR_PRESSURE_ALT))
        shorto2trimb1 = 'Short_O2_Trim_B1:                       %s' % (connection.query(obd.commands.SHORT_O2_TRIM_B1))
        longo2trimb1 = 'Long_O2_Trim_B1:                         %s' % (connection.query(obd.commands.LONG_O2_TRIM_B1))
        shorto2trimb2 = 'Short_O2_Trim_B2:                       %s' % (connection.query(obd.commands.SHORT_O2_TRIM_B2))
        longo2trimb2 = 'Long_O2_Trim_B2:                         %s' % (connection.query(obd.commands.LONG_O2_TRIM_B2))
        fuelrailpressureabsolute = 'Fuel_Rail_Pressure_Absolute: %s' % (connection.query(obd.commands.FUEL_RAIL_PRESSURE_ABS))
        relativeacceleratorpedal = 'Relative_Accelerator_Pedal_Pos:      %s' % (connection.query(obd.commands.RELATIVE_ACCEL_POS))
        hybridbatterylife = 'Hybrid_Battery_Life:                %s' % (connection.query(obd.commands.HYBRID_BATTERY_REMAINING))
        oiltemp = 'Oil_Temp:                                     %s' % (connection.query(obd.commands.OIL_TEMP))
        fuelinjecttiming = 'Fuel_Inject_Timing:                  %s' % (connection.query(obd.commands.FUEL_INJECT_TIMING))
        fuelrate = 'Fuel_Rate:                                   %s' % (connection.query(obd.commands.FUEL_RATE))

        for items in locals().values():
            sens.insert(tk.END,items)
        
    tk.Button(sensorsw1,text="Refresh",command=sensorsdata,font=font3,bg='black',fg='white').grid(row=0,column=1)

def codesw():
    codesw1 = tk.Toplevel(root)
    codesw1.configure(bg='black')
    codesw1.attributes('-fullscreen', True)

    def closew():
        codesw1.destroy()

    ex = tk.Button(codesw1, text='Exit', command=closew, bg='white',fg='black', font=font1)
    ex.grid(row=0,column=3)
    
    codeslist = tk.Listbox(codesw1,fg='white',bg='black', height=10,width=50,font=font4)
    codeslist.grid(row=1,column=1,columnspan=4,rowspan=3)
    
    def scancodes():
        geterrorcodes = connection.query(obd.commands.GET_DTC)
        codeslist.insert(tk.END,geterrorcodes.value)
        print(geterrorcodes)

    rcodes = tk.Button(codesw1,text='Read Codes',command=scancodes,bg='white',fg='black',font=font1)
    rcodes.grid(row=0,column=1)

    def clearcodes():
        connection.query(obd.commands.CLEAR_DTC)
    
    ccodes = tk.Button(codesw1,text='Clear Codes',command=clearcodes,bg='white',fg='black',font=font1)
    ccodes.grid(row=0,column=2)

def gauges():
    gauged = tk.Toplevel(root)
    gauged.configure(bg='black')
    gauged.attributes('-fullscreen', True)

    def exit():
        gauged.destroy()

    exitr = tk.Button(gauged, text='exit',command=exit,font=font1)
    exitr.grid(row=0,column=3,sticky=tk.E)

    scalecolour = tk.StringVar()
    needlecolour= tk.StringVar()
    bordercolour = tk.StringVar()

    speedgauge = Meter(gauged, radius=300, start=0, end=160, border_width=0,
                   fg="black", text_color="white", start_angle=270, end_angle=-270,
                   text_font="DS-Digital 30", scale_color='light blue', needle_color='pink',border_color='dark blue')
    speedgauge.grid(row=1, column=3, padx=20, pady=30,sticky=tk.E)

    rpmgauge = Meter(gauged, radius=300, start=0, end=8000, border_width=0,
               fg="black", text_color="white", start_angle=270, end_angle=-270,
               text_font="DS-Digital 30", scale_color='light blue', needle_color='pink',major_divisions=1000,minor_divisions=0,border_color='dark blue')
    rpmgauge.grid(row=1, column=1, padx=20, pady=30,sticky=tk.W)

    def gaugesupdate11():
        while True:
            speeddata1 = connection.query(obd.commands.SPEED)
            rpmdata1 = connection.query(obd.commands.RPM)
            completespeed1 = speeddata1.value.magnitude 
            completerpm1 = rpmdata1.value.magnitude
            rpmgauge.set(completerpm1)
            speedgauge.set(completespeed1)
    
    if __name__ == '__main__':
        gaugethread = threading.Thread(name='gaugeupdater1', target=gaugesupdate11, daemon=True)
        gaugethread.start()
        
    def gaugesettings():
        gauged.destroy()
        gaugesett = tk.Tk()
        gaugesett.attributes('-fullscreen', True)

        def exit():
            gaugesett.destroy()

        tk.Button(gaugesett,text='Exit',command=exit,bg='white',fg='black',font=font1).grid(row=0,column=2)

        COLORS = ['white','red', 'blue', 'yellow', 'orange', 'pink', 'purple']

        examplegspeed = Meter(gaugesett, radius=300, start=0, end=160, border_width=0,
               fg="black", text_color="white", start_angle=270, end_angle=-270,
               text_font="DS-Digital 30", scale_color=scalecolour.get(), needle_color=needlecolour.get(),border_color=bordercolour.get())
        examplegspeed.grid(row=1, column=1)

        examplegrpm = Meter(gaugesett, radius=300, start=0, end=8000, border_width=0,
               fg="black", text_color="white", start_angle=270, end_angle=-270,
               text_font="DS-Digital 30", scale_color=scalecolour.get(), needle_color=needlecolour.get(),major_divisions=1000,minor_divisions=0,border_color=bordercolour.get())
        examplegrpm.grid(row=1, column=0)

        list1 = tk.StringVar()

        tk.Label(gaugesett,text='Scale Colour:',bg='black',fg='white').grid(row=2,column=0)
        scalecolourlistb = tk.Listbox(gaugesett,bg='black',fg='white')
        scalecolourlistb.grid(row=3,column=0)
    
        tk.Label(gaugesett,text='Needle Colour:',bg='black',fg='white').grid(row=2,column=1)
        needlecolourlistb = tk.Listbox(gaugesett,bg='black',fg='white')
        needlecolourlistb.grid(row=3,column=1)
    
        tk.Label(gaugesett,text='Border Colour:',bg='black',fg='white').grid(row=2,column=2)
        bordercolourlistb = tk.Listbox(gaugesett,bg='black',fg='white')
        bordercolourlistb.grid(row=3,column=2)

        for items in COLORS:
            scalecolourlistb.insert(tk.END,items)
            needlecolourlistb.insert(tk.END,items)
            bordercolourlistb.insert(tk.END,items)
    
        def selected_scale():
            for i in scalecolourlistb.curselection():
                sc = scalecolourlistb.get(i)
                scalecolour.set(sc)

        def checkexample():
            selected_scale()

    
        tk.Button(gaugesett,text='check',command=checkexample,bg='white',fg='black',font=font1).grid(row=0,column=1)


    sett = tk.Button(gauged,text='Settings',command=gaugesettings,bg='white',fg='black',)
    sett.grid(row=0,column=2)

gaugeb = tk.Button(root, text='Gauges', command=gauges, bg='white',fg='black',font=font1)
gaugeb.grid(row=1,column=2)

codesb = tk.Button(root, text='Codes', command=codesw, bg='white',fg='black',font=font1)
codesb.grid(row=1,column=4)

sensorsb = tk.Button(root, text='Sensors', command=sensorsw, bg='white',fg='black',font=font1)
sensorsb.grid(row=1,column=3)

basicb = tk.Button(root, text='Basic', command=basicw, bg='white',fg='black',font=font1)
basicb.grid(row=1,column=1)

settingsb = tk.Button(root, text='Settings', command=settingsw, bg='white',fg='black',font=font1)
settingsb.grid(row=1,column=5)

def exit():
    root.destroy()

exitr = tk.Button(root, text='exit',command=exit,font=font1, bg='white',fg='black')
exitr.grid(row=2,column=1)

root.mainloop()

