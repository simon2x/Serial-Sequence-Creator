
MULTIMETER_SCPI = [(),
                   (),
                   (),
                   (),]
                   
INSTRUCTIONS = [("INS", "Setup", "Setup Instrument"),
                # ("INS", "General", "Reset Instrument"),
                # ("INS", "General", "Power Off Instrument"),
                ("INS", "Custom", "Send and Receive Message"),
                
                ("FLOW", "Flow", "Call Function"),
                # ("FLOW", "Flow", "If"),
                # ("FLOW", "Flow", "For Loop"),
                # ("FLOW", "Flow", "While Loop"),
                
                ("DMM", "Voltage", "Read Voltage"),
                
                ("PSU", "Current", "Set Current Limit"),
                ("PSU", "Voltage", "Set Voltage"),                
                ("PSU", "Voltage", "Step Voltage")]

TESTS = ["Integer Compare",
         "Float Compare",
         "String Compare"]
         # "Voltage Compare"]