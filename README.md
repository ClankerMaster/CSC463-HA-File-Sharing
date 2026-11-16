# CSC463 — High-Availability File Sharing System

**Student:** Shiv Patel  
**Course:** CSC463 — Computer Systems / Socket Programming

This project extends a two-node CentOS Stream 10 high-availability web cluster with a centralized Python TCP file-sharing service. The client can list files, download files, and upload files. Pacemaker and Corosync manage the service and its shared NFS filesystem.

## Features
- List files available on the server.
- Download files over TCP.
- Upload files using a request/ready/data/acknowledgment sequence.
- Keep shared files on NFS storage accessible from either cluster node.
- Serve clients using one virtual IP, including after failover.

## Network architecture

| Role | IP or location |
| --- | --- |
| Node 1 | `192.168.56.2` |
| Node 2 | `192.168.56.102` |
| Virtual IP | `192.168.56.200` |
| NFS server | `192.168.56.110` |
| NFS export | `/srv/nfs/fileshare` |
| Cluster mount | `/opt/fileshare/shared` |
| File service | TCP port `12000` |

The original `WebGroup` manages `WebFS`, `WebIP`, and `WebServer`. The new `FileShareGroup` manages `FileFS` and `FileServer`. Ordering and colocation constraints keep the file server with the website's virtual IP.

```text
Python client --> 192.168.56.200:12000 (virtual IP)
                             |
                    Pacemaker/Corosync
                      /           \
                  Node 1         Node 2
                      \           /
                       NFS storage
                       192.168.56.110
```

## Repository contents

- `Server.py`: Python TCP server for listing, downloads, and uploads.
- `client.py`: interactive Python TCP client.
- `config.py`: reads configuration values.
- `protocol.py`: request/response protocol headers.
- `server.config` and `client.config`: example configuration for this lab.
- `deployment/fileshare.service`: systemd service managed by Pacemaker.
- `deployment/cluster-setup.md`: deployment and failover walkthrough.

## Using the application

From a terminal with Python 3 and the application files installed:

```bash
cd /opt/fileshare/app
python3 client.py
```

Choose **1** to list available files, **2** to download a file, **3** to upload a local file, or **4** to exit. Uploads come from the `UPLOAD` directory in `client.config`; downloads go to its `DOWNLOAD` directory.

For standalone testing, set `SERVER=127.0.0.1` in `client.config` and run `python3 Server.py` in another terminal. In the high-availability setup, use `SERVER=192.168.56.200` and let Pacemaker manage the server through systemd.

## Demonstrated testing

- File listing, download, and upload on Node 1.
- Matching SHA-256 hashes for the original and uploaded test file.
- Pacemaker failover of `WebGroup` and `FileShareGroup` to Node 2 after `pcs node standby node1`.
- File listing, download, and upload from Node 1 to the file server on Node 2 through the same virtual IP.
- NFS verification of the uploaded `failover-test.txt` from Node 2.
- Initial post-failover connectivity failure (`Errno 113`) resolved by allowing TCP/12000 in the firewall.

## Protocol

`REQ`: request file list · `LST`: return file list · `DLD`: request download · `ULD`: request upload · `ERR`: error. `FIL` is defined in the starter protocol but not used by the transfer implementation.

For upload, the client sends `ULD` and a filename. The server responds with `READY`, the client sends file bytes and half-closes the socket, and the server responds with `OK` after receiving EOF.

## Limitations

This is an educational LAN prototype, not a production file service. It does not implement authentication, encryption, concurrent client handling, length-prefixed data frames, atomic uploads, or a complete end-to-end integrity check within the application protocol. The optional multiple-simultaneous-clients bonus is not implemented. Do not expose TCP/12000 to the public internet.
