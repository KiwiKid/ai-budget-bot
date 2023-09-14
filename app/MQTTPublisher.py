import paho.mqtt.client as mqtt
import os


class MQTTPublisher:
    def __init__(self):
        host = os.getenv("MQTT_HOST")
        port = os.getenv("MQTT_PORT", '1883')
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        self.client = mqtt.Client()
        if username and password and host and port:
            self.client.username_pw_set(username, password)
        else:
            print(
                f"MQTT - Could not start due to missing config\n ({username} MQTT_USERNAME) or password (length {len(password)} MQTT_PASSWORD) host:{host} port:{port}")
            return

        self.client.connect(host, int(port), 60)
        self.client.loop_start()
        self.startupComplete = True
        print(f"MQTT startup complete")

    def publish_transaction(self, account_id, transaction_data):
        if self.startupComplete:
            print(f"publish_transaction {account_id} {transaction_data}")

            topic = f"accounts/{account_id}/transactions"
            # Convert transaction data to a string (or JSON)
            payload = str(transaction_data)
            result = self.client.publish(topic, payload)

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Failed to publish to topic: {topic}")
                return False
            return True

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
