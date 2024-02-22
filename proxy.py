import socket
import ssl
import threading
import struct

# Convert query datagram to DNS query with length prefix
def dns_query(query):
    pre_length = struct.pack('>H', len(query))  # Use struct to prefix query with its length for TCP
    return pre_length + query

# Send query to Cloudflare server and receive result
def send_query(tls_conn_sock, query):
    tcp_query = dns_query(query)  # Convert UDP query to TCP format with length prefix
    tls_conn_sock.send(tcp_query)  # Send the query over TLS-secured TCP connection
    result = tls_conn_sock.recv(1024)  # Receive the response
    return result

# TLS connection with Cloudflare server
def tcp_connection(dns):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    sock.settimeout(10)
    context = ssl.create_default_context()  # Use default context for TLS
    context.load_default_certs()  # Load system's default CA certificates
    wrapped_socket = context.wrap_socket(sock, server_hostname=dns)  # Secure the socket with TLS
    wrapped_socket.connect((dns, 853))  # Connect to the DNS server over TLS on port 853
    print(wrapped_socket.getpeercert())  # Print the server's certificate details
    return wrapped_socket

# Handle requests
def request_handle(data, address, dns):
    try:
        tls_conn_sock = tcp_connection(dns)  # Establish a TLS connection to the DNS server
        tcp_result = send_query(tls_conn_sock, data)  # Send the DNS query over TCP
        if tcp_result:
            rcode = int.from_bytes(tcp_result[:6][-2:], 'big') & 0xF  # Extract RCODE from response
            if rcode == 1:
                print("Not a DNS query")
            else:
                udp_result = tcp_result[2:]  # Remove length prefix for UDP response
                s.sendto(udp_result, address)  # Send the response back to the client over UDP
                print("200 OK")
        else:
            print("No response from DNS server")
    except Exception as e:
        print(e)
    finally:
        tls_conn_sock.close()  # Ensure the TLS connection is closed

if __name__ == '__main__':
    DNS = '1.0.0.1'  # Cloudflare's DNS server
    port = 53  # DNS standard UDP port for listening to incoming DNS queries
    host = '0.0.0.0'  # Listen on all interfaces
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket for DNS queries
    s.bind((host, port))

    try:
        while True:
            data, addr = s.recvfrom(1024)  # Wait for incoming DNS queries over UDP
            # For each query, start a new thread to handle it, allowing for concurrent processing
            threading.Thread(target=request_handle, args=(data, addr, DNS)).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    except Exception as e:
        print(e)
    finally:
        s.close()  # Ensure the UDP socket is closed
