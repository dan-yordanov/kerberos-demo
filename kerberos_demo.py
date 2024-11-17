import socket
import threading


# The Authentication Server (AS)
# it will respond with a TGT if the client is authenticated
def start_kerberos_as(host, port):
    """Start the Authentication Server (AS)"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"AS listening on {host}:{port}")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        print(f"Received message from {client_address}: {message.decode()}")

        if message.decode() == "authenticate":
            response = "TGT-Client-Authenticated"  # Simple TGT response
            server_socket.sendto(response.encode(), client_address)
            print("Sent TGT to client.")
        else:
            response = "Invalid request"
            server_socket.sendto(response.encode(), client_address)
            print("Sent invalid response to client.")

        # Close connection after handling one request for simplicity
        break


# TGS - it will issue a Service Ticket based on TGT
def start_kerberos_tgs(host, port):
    """Start the Ticket-Granting Server (TGS)"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"TGS listening on {host}:{port}")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        print(f"Received message from {client_address}: {message.decode()}")

        if message.decode() == "request_service_ticket":
            response = "Service-Ticket-Client-Authorized"  # Service ticket
            server_socket.sendto(response.encode(), client_address)
            print("Sent service ticket to client.")
        else:
            response = "Invalid request"
            server_socket.sendto(response.encode(), client_address)
            print("Sent invalid response to client.")

        # Close connection after handling one request for simplicity
        break


def kerberos_client_as(host, port):
    """Client to interact with the Authentication Server (AS)"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send authentication request to AS
    message = "authenticate"
    client_socket.sendto(message.encode(), (host, port))
    print(f"Sent authentication request to {host}:{port}")

    # Receive the AS response (TGT or error)
    response, _ = client_socket.recvfrom(1024)
    print(f"Received response from AS: {response.decode()}")

    # If the response is a TGT, move to TGS
    if response.decode() == "TGT-Client-Authenticated":
        print("TGT received, now requesting Service Ticket...")
        # Now request a service ticket from TGS
        kerberos_client_tgs(host, 5001)

    client_socket.close()


def kerberos_client_tgs(host, port):
    """Client to interact with the Ticket-Granting Server (TGS)"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send request to TGS for a service ticket
    message = "request_service_ticket"
    client_socket.sendto(message.encode(), (host, port))
    print(f"Sent service ticket request to TGS on {host}:{port}")

    # Receive the TGS response (service ticket or error)
    response, _ = client_socket.recvfrom(1024)
    print(f"Received response from TGS: {response.decode()}")

    # If the response is a service ticket, try to access the service
    if response.decode() == "Service-Ticket-Client-Authorized":
        print("Service ticket received, now accessing the service...")
        kerberos_client_service(host, 5002)

    client_socket.close()


def kerberos_client_service(host, port):
    """Client to access the actual service using the service ticket"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send the service ticket to the service
    message = "access_service_with_ticket"
    client_socket.sendto(message.encode(), (host, port))
    print(f"Sent service ticket to service on {host}:{port}")

    # Receive the service response (success or failure)
    response, _ = client_socket.recvfrom(1024)
    print(f"Received response from service: {response.decode()}")

    client_socket.close()


# The actual service that will validate the Service Ticket
def start_kerberos_service(host, port):
    """Start the Service that will validate the Service Ticket"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Service listening on {host}:{port}")

    while True:
        message, client_address = server_socket.recvfrom(1024)
        print(f"Received message from {client_address}: {message.decode()}")

        if message.decode() == "access_service_with_ticket":
            response = "Access Granted"
            server_socket.sendto(response.encode(), client_address)
            print("Sent access granted to client.")
        else:
            response = "Access Denied"
            server_socket.sendto(response.encode(), client_address)
            print("Sent access denied to client.")

        # Close connection after handling one request for simplicity
        break


def start_servers():
    as_thread = threading.Thread(
        target=start_kerberos_as, args=("127.0.0.1", 5000)
    )
    tgs_thread = threading.Thread(
        target=start_kerberos_tgs, args=("127.0.0.1", 5001)
    )
    service_thread = threading.Thread(
        target=start_kerberos_service, args=("127.0.0.1", 5002)
    )

    as_thread.start()
    tgs_thread.start()
    service_thread.start()


def start_client():
    kerberos_client_as("127.0.0.1", 5000)


# Start everything
start_servers()
start_client()
