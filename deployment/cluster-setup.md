# High-availability cluster deployment

These notes document the lab deployment. Run cluster commands as root on a cluster node. Make sure your original `WebGroup` is already working before adding the file-sharing service.

## Requirements

- Two CentOS Stream 10 nodes running Pacemaker, Corosync, and pcs.
- A working `WebGroup` containing `WebFS`, `WebIP`, and `WebServer`.
- The existing virtual IP `192.168.56.200` (Apache uses port 80; Python uses TCP/12000).
- A dedicated NFS export `192.168.56.110:/srv/nfs/fileshare`.
- The NFS export must remain writable by the service user (UID 2500), with `root_squash` retained.
- The same application and systemd unit installed on Node 1 and Node 2.

## Application installation on each cluster node

Copy the Python source and `*.config` into `/opt/fileshare/app`. Create a `fileshare` service user with UID 2500 and verify it on each node (`id fileshare`). Ensure the service user can read the app and its configs, and that `/opt/fileshare/shared` exists. Example:

```bash
mkdir -p /opt/fileshare/app /opt/fileshare/shared
chmod 755 /opt/fileshare /opt/fileshare/app
chmod 644 /opt/fileshare/app/*.py /opt/fileshare/app/*.config
```

Install `deployment/fileshare.service` at `/etc/systemd/system/fileshare.service` on both nodes:

```bash
systemctl daemon-reload
systemctl is-enabled fileshare.service
```

It should show `disabled`: **Pacemaker controls starting/stopping this service**. Do not run a separate instance of `Server.py` on the cluster nodes during resource tests.

## NFS storage and Pacemaker resources

The original lab created `FileFS` first, then added it to `FileShareGroup`:

```bash
pcs resource create FileFS ocf:heartbeat:Filesystem \
    device="192.168.56.110:/srv/nfs/fileshare" \
    directory="/opt/fileshare/shared" \
    fstype="nfs" \
    op monitor interval=20s

pcs resource group add FileShareGroup FileFS

pcs resource create FileServer systemd:fileshare \
    op monitor interval=20s \
    --group FileShareGroup

pcs constraint colocation add FileShareGroup with WebGroup INFINITY
pcs constraint order start WebGroup then start FileShareGroup

pcs status
```

The ordered group starts its NFS mount before the Python server. Colocation makes it follow the `WebGroup` that owns the virtual IP. **Do not recreate resources if they already exist.**

## Firewall and client configuration

Permit port 12000 on both cluster nodes in the appropriate firewall zone:

```bash
firewall-cmd --permanent --add-port=12000/tcp
firewall-cmd --reload
```

In `client.config`, set `SERVER=192.168.56.200` to reach the cluster via the VIP. The Python client reads that configuration from its working directory.

## Test and recovery

Check status and test the client:

```bash
pcs status
ss -ltnp | grep ':12000'
cd /opt/fileshare/app
python3 client.py
```

List and download files, then try uploading a small file from the configured upload directory.

Simulate failover:

```bash
pcs node standby node1
pcs status
```

Verify that all resources in both `WebGroup` and `FileShareGroup` are on Node 2 and repeat client operations through the same virtual IP. In our test, `failover-test.txt` was successfully uploaded through the VIP and read from NFS on Node 2.

Restore eligibility:

```bash
pcs node unstandby node1
pcs status
```

Pacemaker might leave resources on Node 2 after Node 1 comes online again.

**Troubleshooting observation:** The first client connection after failover failed with `Errno 113: No route to host`; this was fixed by permitting inbound TCP/12000 through the firewall. That initial failure was a networking/firewall configuration issue rather than a Pacemaker resource-placement failure.

## Safety notes

Use this project only on an isolated trusted lab network. This class demonstration has no authentication, transport encryption, atomic transfer protocol, or concurrency handling. Avoid exposing port 12000 to the internet. Retain `root_squash` for the NFS export.
