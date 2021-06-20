import paho.mqtt.client as mqtt

client = mqtt.Client( "HomeAutomationServer", clean_session=False )
client.connect( "127.0.0.1", 1883, 60 )
client.loop_start()
